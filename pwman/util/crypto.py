# ============================================================================
# This file is part of Pwman3.
#
# Pwman3 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2
# as published by the Free Software Foundation;
#
# Pwman3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pwman3; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ============================================================================
# Copyright (C) 2012 Oz Nahum <nahumoz@gmail.com>
# ============================================================================
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
# ============================================================================

"""
Encryption Module used by PwmanDatabase

Supports AES, ARC2, Blowfish, CAST, DES, DES3, IDEA, RC5.

Usage:
import pwman.util.crypto.CryptoEngine as CryptoEngine
from pwman.util.crypto import CryptoEngine

class myCallback(CryptoEngine.Callback):
    def execute(self):
        return "mykey"

params = {'encryptionAlgorithm': 'AES',
          'encryptionCallback': callbackFunction}

CryptoEngine.init(params)

crypto = CryptoEngine.get()
ciphertext = crypto.encrypt("plaintext")
plaintext = cyypto.decrypt(ciphertext)
"""
from __future__ import print_function
from Crypto.Cipher import Blowfish as cBlowfish
from Crypto.Cipher import AES as cAES
from Crypto.Cipher import ARC2 as cARC2
from Crypto.Cipher import CAST as cCAST
from Crypto.Cipher import DES as cDES
from Crypto.Cipher import DES3 as cDES3
from Crypto.Random import OSRNG

from pwman.util.callback import Callback
import pwman.util.config as config
try:
    import cPickle
except ImportError:
    import pickle as cPickle
import time
import sys
import ctypes
import hashlib
import base64


def zerome(string):
    """
    securely erase strings ...
    for windows: ctypes.cdll.msvcrt.memset
    """
    bufsize = len(string) + 1
    offset = sys.getsizeof(string) - bufsize
    ctypes.memset(id(string) + offset, 0, bufsize)

# Use this to tell if crypto is successful or not
_TAG = "PWMANCRYPTO"

_INSTANCE = None


class CryptoException(Exception):
    """Generic Crypto Exception."""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "CryptoException: " + self.message


class CryptoUnsupportedException(CryptoException):
    """Unsupported feature requested."""
    def __str__(self):
        return "CryptoUnsupportedException: " + self.message


class CryptoBadKeyException(CryptoException):
    """Encryption key is incorrect."""
    def __str__(self):
        return "CryptoBadKeyException: " + self.message


class CryptoNoKeyException(CryptoException):
    """No key has been initalised."""
    def __str__(self):
        return "CryptoNoKeyException: " + self.message


class CryptoNoCallbackException(CryptoException):
    """No Callback has been set."""
    def __str__(self):
        return "CryptoNoCallbackException: " + self.message


class CryptoEngine(object):
    """
    Cryptographic Engine, overrides CryptoEngineOld.
    The main change is that _getcipher_real is now hashing the key
    before encrypting it.

    This method can eventually remove the call to _retrievedata,
    which used to strip the _TAG from the plain text string or return
    the cPickle object as string.
    Since we don't use cPickle to serialize object anymore, we can
    safely aim towards removing this method. Thus, removing also
    the _TAG in the beginning of each string as per recommendation of
    Ralf Herzog.
    """
    _timeoutcount = 0
    _instance = None
    _instance_new = None
    _callback = None

    @classmethod
    def get(cls, dbver=0.5):
        """
        CryptoEngine.get() -> CryptoEngine
        Return an instance of CryptoEngine.
        If no instance is found, a CryptoException is raised.
        """

        if CryptoEngine._instance:
            return CryptoEngine._instance
        if CryptoEngine._instance_new:
            return CryptoEngine._instance_new

        keycrypted = config.get_value("Encryption", "keycrypted")
        algo = config.get_value("Encryption", "algorithm")

        if not algo:
            raise CryptoException("Parameters missing, no algorithm given")

        try:
            timeout = int(config.get_value("Encryption", "timeout"))
        except ValueError:
            timeout = -1

        kwargs = {'keycrypted': keycrypted, 'algorithm': algo,
                  'timeout': timeout}

        if dbver < 0.5:
            CryptoEngine._instance = CryptoEngineOld(**kwargs)
            return CryptoEngine._instance

        if dbver >= 0.5:
            CryptoEngine._instance_new = CryptoEngine(**kwargs)
            return CryptoEngine._instance_new

    def __init__(self, keycrypted=None, algorithm='AES', timeout=-1):
        """
        Initialise the Cryptographic Engine
        """
        self._algo = algorithm
        self._keycrypted = keycrypted if keycrypted else None
        self._timeout = timeout
        self._cipher = None

    def auth(self, key):
        """
        authenticate using a given key
        """
        tmpcipher = self._getcipher_real(key, self._algo)
        s = base64.b64decode(self._keycrypted)
        plainkey = tmpcipher.decrypt(s)
        key = self._retrievedata(plainkey)
        key = base64.b64decode(str(key))
        self._cipher = self._getcipher_real(key, self._algo)

    def encrypt(self, obj):
        """
        encrypt(obj) -> ciphertext
        Encrypt obj and return its ciphertext. obj must be a picklable class.
        Can raise a CryptoException and CryptoUnsupportedException"""
        cipher = self._getcipher()
        plaintext = self._preparedata(obj, cipher.block_size)
        ciphertext = cipher.encrypt(plaintext)
        if sys.version_info.major > 2:
            rv = base64.b64encode(ciphertext) + b'\n'
        else:
            rv = base64.b64encode(ciphertext) + '\n'

        #rv = str(ciphertext).encode('base64')
        return rv

    def decrypt(self, ciphertext):
        """
        decrypt(ciphertext) -> obj
        Decrypt ciphertext and returns the obj that was encrypted.
        If key is bad, a CryptoBadKeyException is raised
        Can also raise a CryptoException and CryptoUnsupportedException"""
        cipher = self._getcipher()
        ciphertext = base64.b64decode(str(ciphertext))
        plaintext = cipher.decrypt(ciphertext)
        return self._retrievedata(plaintext)

    def set_cryptedkey(self, key):
        """
        hold _keycrypted
        """
        self._keycrypted = key

    def get_cryptedkey(self):
        """
        return _keycrypted
        """
        return self._keycrypted

    @property
    def callback(self):
        """
        return call back function
        """
        return self._callback

    @callback.setter
    def callback(self, callback):
        if isinstance(callback, Callback):
            self._callback = callback
            self._getsecret = callback.getsecret
            self._getnewsecret = callback.getnewsecret
        else:
            raise CryptoNoCallbackException("callback must be an instance of"
                                            " Callback!")

    def _get_keycrypted(self):
        if self._keycrypted is None:
            # Generate a new key, 32 byts in length, if that's
            # too long for the Cipher, _getCipherReal will sort it out
            random = OSRNG.new()
            randombytes = random.read(32)
            if sys.version_info.major > 2:
                key = base64.b64encode(randombytes)+b'\n'
            else:
                key = base64.b64encode(str(randombytes))+'\n'
        else:
            password = self._getsecret("Please enter your current password")
            cipher = self._getcipher_real(password, self._algo)
            plainkey = cipher.decrypt(base64.b64decode(self._keycrypted))
            # python2 only ...
            # plainkey = cipher.decrypt(str(self._keycrypted).decode('base64'))
            key = self._retrievedata(plainkey)

        return key

    def changepassword(self):
        """
        Creates a new key from a user given password.
        The key itself is actually stored in the database as
        a chiper text. This key is encrypted using a random byte string.
        """

        if self._callback is None:
            raise CryptoNoCallbackException("No call back class has been "
                                            "specified")
        key = self._get_keycrypted()

        newpassword1 = self._getnewsecret("Please enter your new password")
        newpassword2 = self._getnewsecret("Please enter your new password again")
        while newpassword1 != newpassword2:
            print("Passwords do not match!")
            newpassword1 = self._getnewsecret("Please enter your new password")
            newpassword2 = self._getnewsecret("Please enter your new password again")

        newcipher = self._getcipher_real(newpassword1, self._algo)
        pkey = self._preparedata(key, newcipher.block_size)
        ciphertext = newcipher.encrypt(pkey)
        if sys.version_info.major > 2:
            k = base64.b64encode(ciphertext) + b'\n'
        else:
            k = base64.b64encode(str(ciphertext)) + '\n'
        # python2 only
        # self._keycrypted = str(ciphertext).encode('base64')
        self._keycrypted = k
        # newpassword1, newpassword2 are not needed any more so we erase
        # them
        zerome(newpassword1)
        zerome(newpassword2)
        del(newpassword1)
        del(newpassword2)
        # we also want to create the cipher if there isn't one already
        # so this CryptoEngine can be used from now on
        if self._cipher is None:
            if sys.version_info.major > 2:
                key = base64.b64decode(key)
            else:
                key = base64.b64decode(str(key))

            self._cipher = self._getcipher_real(key, self._algo)
            CryptoEngine._timeoutcount = time.time()

        return self._keycrypted

    def alive(self):
        """
        check if we have cipher
        """
        if self._cipher is not None:
            return True
        else:
            return False

    def forget(self):
        """
        discard cipher
        """
        self._cipher = None

    def _pre_check_get_chiper(self):
        if (self._cipher is not None
            and (self._timeout == -1
                 or (time.time() -
                     CryptoEngine._timeoutcount) < self._timeout)):
            return self._cipher
        if self._callback is None:
            raise CryptoNoCallbackException("No Callback exception")
        if self._keycrypted is None:
            raise CryptoNoKeyException("Encryption key has not been generated")

    def _getcipher(self):
        """
        get cypher from user, to decrypt DB
        """
        if self._pre_check_get_chiper():
            return self._cipher

        max_tries = 5
        tries = 0
        key = None

        while tries < max_tries:
            try:
                password = self._getsecret("Please enter your password")
                tmpcipher = self._getcipher_real(password, self._algo)
                # python2 code only
                #ciphertext = str(self._keycrypted).decode('base64')
                tc = base64.b64decode(str(self._keycrypted))
                plainkey = tmpcipher.decrypt(tc)
                key = self._retrievedata(plainkey)
                break
            except CryptoBadKeyException:
                print("Wrong password.")
                tries += 1

        if not key:
            raise CryptoBadKeyException("Wrong password entered {x} times; "
                                        "giving up ".format(x=max_tries))
        try:
            key = base64.b64decode(str(key))
            #key = str(key).decode('base64')
        except Exception:
            key = cPickle.loads(key)
            key = base64.b64decode(str(key))
            #key = str(key).decode('base64')

        self._cipher = self._getcipher_real(key, self._algo)

        CryptoEngine._timeoutcount = time.time()
        return self._cipher

    def _getcipher_real(self, key, algo):
        """
        do the real job of decrypting using functions
        form PyCrypto
        """
        if (algo == "AES"):
            if sys.version_info.major > 2 and isinstance(key, str):
                key = key.encode('utf-8')
            for i in range(1000):
                key = hashlib.sha256(key)
                key = key.digest()

            key = hashlib.sha256(key)
            cipher = cAES.new(key.digest(), cAES.MODE_ECB)

        elif (algo == 'ARC2'):
            cipher = cARC2.new(key, cARC2.MODE_ECB)
        elif (algo == 'ARC4'):
            raise CryptoUnsupportedException("ARC4 is currently unsupported")
        elif (algo == 'Blowfish'):
            cipher = cBlowfish.new(key, cBlowfish.MODE_ECB)
        elif (algo == 'CAST'):
            cipher = cCAST.new(key, cCAST.MODE_ECB)
        elif (algo == 'DES'):
            if len(key) != 8:
                raise Exception("DES Encrypted keys must be 8 characters "
                                "long!")
            cipher = cDES.new(key, cDES.MODE_ECB)
        elif (algo == 'DES3'):
            key = hashlib.sha224(key)
            cipher = cDES3.new(key.digest()[:24], cDES3.MODE_ECB)
        elif (algo == 'XOR'):
            raise CryptoUnsupportedException("XOR is currently unsupported")
        else:
            raise CryptoException("Invalid algorithm specified")
        return cipher

    def _preparedata(self, obj, blocksize):
        """
        prepare data before encrypting
        """
        plaintext = obj
        numblocks = (len(plaintext)//blocksize) + 1
        newdatasize = blocksize*numblocks
        return plaintext.ljust(newdatasize)

    def _retrievedata(self, plaintext):
        """
        retrieve encrypted data
        """
        if sys.version_info.major > 2:
            return plaintext
        try:
            plaintext.decode('utf-8')
        except UnicodeDecodeError:
            raise CryptoBadKeyException("Error decrypting, bad key")
        return plaintext


class CryptoEngineOld(CryptoEngine):

    def _getcipher_real(self, key, algo):
        """
        do the real job of decrypting using functions
        form PyCrypto
        """
        if (algo == "AES"):
            key = self._padkey(key, [16, 24, 32])
            cipher = cAES.new(key, cAES.MODE_ECB)
        elif (algo == 'ARC2'):
            cipher = cARC2.new(key, cARC2.MODE_ECB)
        elif (algo == 'ARC4'):
            raise CryptoUnsupportedException("ARC4 is currently unsupported")
        elif (algo == 'Blowfish'):
            cipher = cBlowfish.new(key, cBlowfish.MODE_ECB)
        elif (algo == 'CAST'):
            cipher = cCAST.new(key, cCAST.MODE_ECB)
        elif (algo == 'DES'):
            self._padkey(key, [8])
            cipher = cDES.new(key, cDES.MODE_ECB)
        elif (algo == 'DES3'):
            key = self._padkey(key, [16, 24])
            cipher = cDES3.new(key, cDES3.MODE_ECB)
        elif (algo == 'XOR'):
            raise CryptoUnsupportedException("XOR is currently unsupported")
        else:
            raise CryptoException("Invalid algorithm specified")
        return cipher

    def _padkey(self, key, acceptable_lengths):
        """
        pad key with extra string
        """
        maxlen = max(acceptable_lengths)
        keylen = len(key)
        if (keylen > maxlen):
            return key[0:maxlen]
        acceptable_lengths.sort()
        acceptable_lengths.reverse()
        newkeylen = None
        for i in acceptable_lengths:
            if (i < keylen):
                break
            newkeylen = i
        return key.ljust(newkeylen)

    def _preparedata(self, obj, blocksize):
        """
        prepare data before encrypting
        """
        plaintext = _TAG + obj
        numblocks = (len(plaintext)/blocksize) + 1
        newdatasize = blocksize*numblocks
        return plaintext.ljust(newdatasize)

    def _retrievedata(self, plaintext):
        """
        retrieve encrypted data
        """

        # startswith(_TAG) is to make sure the decryption
        # is correct! However this method is SHIT! It is dangerous,
        # and exposes the datebase.
        # Instead we sould make sure that the string is composed of legal
        # printable stuff and not garbage
        # string.printable is one such set
        try:
            plaintext.decode('utf-8')
        except UnicodeDecodeError:
            raise CryptoBadKeyException("Error decrypting, bad key")

        if (plaintext.startswith(_TAG)):
            plaintext = plaintext[len(_TAG):]

        try:
            # old db version used to write stuff to db with
            # plaintext = cPickle.dumps(obj)
            # DONE: completely remove this block, and convert
            # the DB to a completely plain text ...
            # See the above CryptoEngine
            # This implies that the coversion from OLD DATABASE FORMAT has
            # plain strings too ...
            return cPickle.loads(plaintext)
        except (TypeError, ValueError, cPickle.UnpicklingError, EOFError):
            return plaintext
