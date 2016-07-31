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
# Copyright (C) 2016 Oz N Tiram <oz.tiram@gmail.com>
# ============================================================================

from __future__ import print_function
import base64
import binascii
import ctypes
import os
import random
import string
import sys
import time

# PyCrypto not found, we use a compatible implementation
# in pure Python.
# This is good for Windows where software installation suck
# or embeded devices where compilation is a bit harder
from pwman.util.crypto import AES
from pwman.util.crypto.pypbkdf2 import PBKDF2


from pwman.util.callback import Callback

if sys.version_info.major > 2:  # pragma: no cover
    raw_input = input


def encode_AES(cipher, clear_text):
    return base64.b64encode(cipher.encrypt(clear_text))


def decode_AES(cipher, encoded_text):
    return cipher.decrypt(base64.b64decode(encoded_text)).rstrip()


def generate_password(pass_len=8, uppercase=True, lowercase=True, digits=True,
                      special_chars=True):
    allowed = ''
    if lowercase:
        allowed = allowed + string.ascii_lowercase
    if uppercase:
        allowed = allowed + string.ascii_uppercase
    if digits:
        allowed = allowed + string.digits
    if special_chars:
        allowed = allowed + string.punctuation

    password = ''.join(random.SystemRandom().choice(allowed)
                       for _ in range(pass_len))
    return password


def zerome(string):
    """
    securely erase strings ...
    for windows: ctypes.cdll.msvcrt.memset
    """
    bufsize = len(string) + 1
    offset = sys.getsizeof(string) - bufsize
    ctypes.memset(id(string) + offset, 0, bufsize)


class CryptoException(Exception):
    pass


def get_digest(password, salt):
    """
    Get a digest based on clear text password
    """
    iterations = 5000
    if isinstance(password, bytes):
        password = password.decode()
    try:
        return PBKDF2(password, salt, dkLen=32, count=iterations)
    except TypeError:
        return PBKDF2(password, salt, iterations=iterations).read(32)


def get_cipher(password, salt):
    """
    Create a chiper object from a hashed password
    """
    iv = os.urandom(AES.block_size)
    dig = get_digest(password, salt)
    chiper = AES.new(dig, AES.MODE_CBC, iv)
    return chiper


def prepare_data(text, block_size):
    """
    prepare data before encryption so the lenght matches the expected
    lenght by the algorithm.
    """
    num_blocks = len(text)//block_size + 1
    newdatasize = block_size*num_blocks
    return text.ljust(newdatasize)


class CryptoEngine(object):  # pagma: no cover
    _timeoutcount = 0
    _instance = None
    _callback = None

    @classmethod
    def get(cls, timeout=-1):
        if CryptoEngine._instance:
            return CryptoEngine._instance

        CryptoEngine._instance = CryptoEngine(timeout)
        return CryptoEngine._instance

    def __init__(self, salt=None, digest=None, algorithm='AES',
                 timeout=-1, reader=None):
        """
        Initialise the Cryptographic Engine
        """
        self._algo = algorithm
        self._digest = digest if digest else None
        self._salt = salt if salt else None
        self._timeout = timeout
        self._cipher = None
        self._reader = reader
        self._callback = None
        self._getsecret = None  # This is set in callback.setter

    def authenticate(self, password):
        """
        salt and digest are stored in a file or a database
        """
        dig = get_digest(password, self._salt)
        if binascii.hexlify(dig) == self._digest or dig == self._digest:
            CryptoEngine._timeoutcount = time.time()
            self._cipher = get_cipher(password, self._salt)
            return True
        return False

    def _auth(self):
        """
        Read password from the user, if the password is correct,
        finish the execution an return the password and salt which
        are read from the file.
        """
        salt = self._salt
        tries = 0
        while tries < 5:
            password = self._getsecret("Please type in your master password"
                                       ).encode('utf-8')
            if self.authenticate(password):
                return password, salt

            print("You entered a wrong password...")
            tries += 1
        raise CryptoException("You entered wrong password 5 times..")

    def encrypt(self, text):
        if not self._is_authenticated():
            p, s = self._auth()
            cipher = get_cipher(p, s)
            self._cipher = cipher
            del(p)

        return encode_AES(self._cipher, prepare_data(text, AES.block_size))

    def decrypt(self, cipher_text):
        if not self._is_authenticated():
            p, s = self._auth()
            cipher = get_cipher(p, s)
            self._cipher = cipher
            del(p)

        return decode_AES(self._cipher, prepare_data(cipher_text,
                                                     AES.block_size))

    def forget(self):
        """
        discard cipher
        """
        self._cipher = None

    def _is_authenticated(self):
        if not self._digest and not self._salt:
            self._create_password()
        if not self._is_timedout() and self._cipher is not None:
            return True
        return False

    def _is_timedout(self):
        if self._timeout > 0:
            if (time.time() - CryptoEngine._timeoutcount) > self._timeout:
                self._cipher = None
            return True
        return False

    def changepassword(self, reader=raw_input):
        if self._callback is None:
            raise CryptoException("No callback class has been specified")

        # if you change the password of the database you have to Change
        # all the cipher texts in the databse!!!
        self._keycrypted = self._create_password()
        self.set_cryptedkey(self._keycrypted)
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
        else:
            raise Exception("callback must be an instance of Callback!")

    def _create_password(self):
        """
        Create a secret password as a hash and the salt used for this hash.
        Change reader to manipulate how input is given.
        """
        salt = base64.b64encode(os.urandom(32))
        passwd = self._getsecret("Please type in the master password")
        key = get_digest(passwd, salt)
        hpk = salt+'$6$'.encode('utf8')+binascii.hexlify(key)
        self._digest = key
        self._salt = salt
        self._cipher = get_cipher(passwd, salt)
        return hpk.decode('utf-8')

    def set_cryptedkey(self, key):
        # TODO: rename this method!
        salt, digest = key.split('$6$')
        self._digest = digest.encode('utf-8')
        self._salt = salt.encode('utf-8')

    def get_cryptedkey(self):
        # TODO: rename this method!
        """
        return _keycrypted
        """
        return self._salt.decode() + u'$6$' + self._digest.decode()
