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
# Copyright (C) 2014 Oz Nahum <nahumoz@gmail.com>
# ============================================================================

from __future__ import print_function
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import base64
import os
import sys
import binascii
import time
from pwman.util.callback import Callback
import pwman.util.config as config

if sys.version_info.major > 2:  # pragma: no cover
    raw_input = input

EncodeAES = lambda c, s: base64.b64encode(c.encrypt(s))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip()


class CryptoException(Exception):
    pass


def get_digest(password, salt):
    """
    Get a digest based on clear text password
    """
    iterations = 5000
    return PBKDF2(password, salt, dkLen=32, count=iterations)


def authenticate(password, salt, digest):
    """
    salt and digest are stored in a file or a database
    """
    dig = get_digest(password, salt)
    return binascii.hexlify(dig) == digest


def write_password(reader=raw_input):
    """
    Write a secret password as a hash and the salt used for this hash
    to a file
    """
    salt = base64.b64encode(os.urandom(32))
    passwd = reader("Please type in the secret key:")
    key = get_digest(passwd, salt)
    f = open('passwords.txt', 'wt')
    hpk = salt+'$6$'.encode('utf8')+binascii.hexlify(key)
    f.write(hpk.decode('utf-8'))
    f.close()


def get_digest_from_file(filename):
    """
    Read a digested password and salt from the file
    """
    f = open(filename, 'rt')
    salt, digest = f.readline().split('$6$')
    return salt.encode('utf-8'), digest.encode('utf-8')


def get_cipher(password, salt):
    """
    Create a chiper object from a hashed password
    """
    iv = os.urandom(AES.block_size)
    dig = get_digest(password, salt)
    chiper = AES.new(dig, AES.MODE_ECB, iv)
    return chiper


def cli_auth(reader=raw_input):
    """
    Read password from the user, if the password is correct,
    finish the execution an return the password and salt which
    are read from the file.
    """
    salt, digest = get_digest_from_file('passwords.txt')
    tries = 0
    while tries < 5:
        password = reader("Please type in your master password:"
                          ).encode('utf-8')
        if authenticate(password, salt, digest):
            return password, salt

        print("You entered a wrong password...")
        tries += 1

    raise CryptoException("You entered wrong password 5 times..")


def prepare_data(text, block_size):
    """
    prepare data before encryption so the lenght matches the expected
    lenght by the algorithm.
    """
    num_blocks = len(text)//block_size + 1
    newdatasize = block_size*num_blocks
    return text.ljust(newdatasize)


def save_a_secret_message(reader=raw_input):
    """
    PoC to show we can encrypt a message
    """
    secret_msg = """This is a very important message! Learn Cryptography!!!"""
    # the secret message will be encrypted with the secret password found
    # in the file
    passwd, salt = cli_auth(reader=reader)
    cipher = get_cipher(passwd, salt)
    # explictly destroy password, so now there is no clear text reference
    # to the input given by the user
    del(passwd)
    msg = EncodeAES(cipher, prepare_data(secret_msg, AES.block_size))
    with open('secret.enc', 'wt') as s:
        s.write(msg.decode())
    print("The cipher message is:", msg.decode())


def read_a_secret_message(reader=raw_input):
    """
    PoC to show we can decrypt a message
    """
    passwd, salt = cli_auth(reader)
    cipher = get_cipher(passwd, salt)
    del(passwd)
    with open('secret.enc') as s:
        msg = s.readline()
        print("The decrypted secret message is:")
        decoded = DecodeAES(cipher, msg)
        print(decoded)


class CryptoEngine(object):  # pagma: no cover
    _timeoutcount = 0
    _instance = None
    _instance_new = None
    _callback = None

    @classmethod
    def get(cls, dbver=0.5):
        if CryptoEngine._instance:
            return CryptoEngine._instance
        if CryptoEngine._instance_new:
            return CryptoEngine._instance_new

        algo = config.get_value("Encryption", "algorithm")

        if not algo:
            raise Exception("Parameters missing, no algorithm given")

        try:
            timeout = int(config.get_value("Encryption", "timeout"))
        except ValueError:
            timeout = -1

        salt, digest = get_digest_from_file('passwords.txt')

        kwargs = {'algorithm': algo,
                  'timeout': timeout, 'salt': salt, 'digest': digest}

        if dbver >= 0.5:
            CryptoEngine._instance_new = CryptoEngine(**kwargs)
            return CryptoEngine._instance_new

    def __init__(self, salt=None, digest=None, algorithm='AES',
                 timeout=-1, reader=raw_input):
        """
        Initialise the Cryptographic Engine
        """
        self._algo = algorithm
        self._digest = digest if digest else None
        self._salt = salt if salt else None
        self._timeout = timeout
        self._cipher = None
        self._reader = reader

    def authenticate(self, password):
        """
        salt and digest are stored in a file or a database
        """
        dig = get_digest(password, self._salt)
        if binascii.hexlify(dig) == self._digest:
            CryptoEngine._timeoutcount = time.time()
            self._cipher = get_cipher(password, self._salt)
            return True
        return False

    def encrypt(self, text):
        if not self._is_authenticated():
            p, s = cli_auth(self._reader)
            cipher = get_cipher(p, s)
            del(p)
            return EncodeAES(cipher, prepare_data(text, AES.block_size))

        return EncodeAES(self._cipher, prepare_data(text, AES.block_size))

    def decrypt(self, cipher_text):
        if not self._is_authenticated():
            p, s = cli_auth(self._reader)
            cipher = get_cipher(p, s)
            del(p)
            return DecodeAES(cipher, prepare_data(cipher_text, AES.block_size))

        return DecodeAES(self._cipher, prepare_data(cipher_text,
                                                    AES.block_size))

    def _is_authenticated(self):
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
        self._keycrypted = self._create_password(reader=reader)
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
            raise Exception("callback must be an instance of Callback!")

    def _create_password(self, reader=raw_input):
        """
        Create a secret password as a hash and the salt used for this hash.
        Change reader to manipulate how input is given.
        """
        salt = base64.b64encode(os.urandom(32))
        passwd = reader("Please type in the secret key:")
        key = self._get_digest(passwd, salt)
        hpk = salt+'$6$'.encode('utf8')+binascii.hexlify(key)
        return hpk.decode('utf-8')

    def _get_digest(self, password, salt):
        """
        Get a digest based on clear text password
        """
        iterations = 5000
        return PBKDF2(password, salt, dkLen=32, count=iterations)


if __name__ == '__main__':  # pragma: no cover
    if '-i' in sys.argv:
        write_password()
    save_a_secret_message()
    read_a_secret_message()
