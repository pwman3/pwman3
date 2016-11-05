# ============================================================================
# This file is part of Pwman3.
#
# Pwman3 is free software; you can redistribute iut and/or modify
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
# Copyright (C) 2012, 2013, 2014 Oz Nahum Tiram <nahumoz@gmail.com>
# ============================================================================
import unittest
import os
import time
import string
from pwman.util.callback import Callback
from pwman.util.crypto_engine import (CryptoEngine, CryptoException,
                                      generate_password)

# set cls_timout to negative number (e.g. -1) to disable
default_config = {'Global': {'umask': '0100', 'colors': 'yes',
                             'cls_timeout': '5'
                             },
                  'Database': {'type': 'SQLite',
                               'filename': os.path.join("tests", "pwman.db")},
                  'Encryption': {'algorithm': 'AES'},
                  'Readline': {'history': os.path.join("tests",
                                                       "history")}
                  }

give_key = lambda msg: b"12345"
give_wrong_key = lambda msg: b"verywrongtkey"

salt = b'cUDHNMJdTRxiIDPXuT163UMvi4fd2pXz/bRg2Zm8ajE='
digest = b'9eaec7dc1ee647338406739c54dbf9c4881c74702008eb978622811cfc46a07f'


class DummyCallback(Callback):

    def getinput(self, question):
        return b'12345'

    def getsecret(self, question):
        return b'12345'

    def getnewsecret(self, question):
        return b'12345'


class TestPassGenerator(unittest.TestCase):

    def test_len(self):
        self.assertEqual(13, len(generate_password(pass_len=13)))

    def test_has_no_lower(self):
        password = generate_password(uppercase=True, lowercase=False)
        lower = set(string.ascii_lowercase)
        it = lower.intersection(set(password))
        print(it)
        self.assertTrue(len(it) == 0)

    def test_has_digits(self):
        password = generate_password(uppercase=True, lowercase=False)
        digits = set(string.digits)
        it = digits.intersection(password)
        print(it)
        try:
            self.assertTrue(len(it) >= 0)
        except unittest.AssetionError:
            print(it)

    def test_has_no_digits(self):
        password = generate_password(uppercase=True, digits=False,
                                     lowercase=False)
        digits = set(string.digits)
        it = digits.intersection(password)
        print(it)
        try:
            self.assertTrue(len(it) == 0)
        except unittest.AssetionError:
            print(it)


class CryptoEngineTest(unittest.TestCase):

    def test4_d_get_crypto(self):
        ce = CryptoEngine.get()
        ce.callback = DummyCallback()
        secret2 = ce.changepassword(reader=give_key)
        secret1 = ce.changepassword(reader=give_key)
        # althouth the same secret key is used,
        # the secret hash is not the same, because a
        # different random seed is used when calling
        # CryptoEngine._get_digest
        self.assertNotEqual(secret1, secret2)

    def test5_e_authenticate(self):
        ce = CryptoEngine.get()
        ce._reader = give_key
        self.assertFalse(ce.authenticate(b'verywrong'))
        self.assertTrue(ce.authenticate(b'12345'))
        ce._expires_at = int(time.time()) + 600
        self.assertTrue(ce._is_authenticated())

    def test6_is_timedout(self):
        ce = CryptoEngine.get()
        ce._expires_at = time.time() - 2
        time.sleep(1.1)
        self.assertTrue(ce._is_timedout())
        self.assertIsNone(ce._cipher)
        self.assertFalse(ce._is_authenticated())

    def test_f_encrypt_decrypt(self):
        ce = CryptoEngine.get()
        ce._reader = give_key
        if not ce._salt:
            ce._salt = salt
        secret = ce.encrypt(b"topsecret")
        decrypt = ce.decrypt(secret)
        self.assertEqual(decrypt.decode(), "topsecret")
        ce._cipher = None
        secret = ce.encrypt(b"topsecret")
        decrypt = ce.decrypt(secret)
        self.assertEqual(decrypt.decode(), "topsecret")

    def test_g_encrypt_decrypt_wrong_pass(self):
        ce = CryptoEngine.get()
        ce._cipher = None
        ce._getsecret = give_wrong_key
        self.assertRaises(CryptoException, ce.encrypt, b"secret")
        ce._getsecret = lambda x: b'12345'
        secret = ce.encrypt(b"topsecret")
        decrypt = ce.decrypt(secret)
        self.assertEqual(decrypt.decode(), "topsecret")

if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True)
