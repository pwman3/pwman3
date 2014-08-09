import unittest
import pwman.util.config as config
import os
from pwman.util.crypto_engine import (write_password, save_a_secret_message,
                                      read_a_secret_message,
                                      CryptoEngine, CryptoException)
import time

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

config.set_defaults(default_config)

give_key = lambda msg: "verysecretkey"
give_wrong_key = lambda msg: "verywrongtkey"


class CryptoEngineTest(unittest.TestCase):

    def test_a_write_password(self):
        write_password(reader=give_key)

    def test_b_save_secret(self):
        save_a_secret_message(reader=give_key)

    def test_c_read_secret(self):
        read_a_secret_message(reader=give_key)

    def test_d_get_crypto(self):
        ce = CryptoEngine.get()

        secret2 = ce.changepassword(reader=give_key)
        secret1 = ce.changepassword(reader=give_key)
        # althouth the same secret key is used,
        # the secret hash is not the same, because a
        # different random seed is used when calling
        # CryptoEngine._get_digest
        self.assertNotEqual(secret1, secret2)

    def test_e_authenticate(self):
        ce = CryptoEngine.get()
        self.assertFalse(ce.authenticate('verywrong'))
        self.assertTrue(ce.authenticate('verysecretkey'))
        ce._timeout = -1
        self.assertTrue(ce._is_authenticated())

    def test_f_encrypt_decrypt(self):
        ce = CryptoEngine.get()
        ce._reader = give_key
        secret = ce.encrypt("topsecret")
        decrypt = ce.decrypt(secret)
        self.assertEqual(decrypt, "topsecret")
        ce._cipher = None
        secret = ce.encrypt("topsecret")
        decrypt = ce.decrypt(secret)
        self.assertEqual(decrypt, "topsecret")

    def test_g_encrypt_decrypt_wrong_pass(self):
        ce = CryptoEngine.get()
        ce._cipher = None
        ce._reader = give_wrong_key
        self.assertRaises(CryptoException, ce.encrypt, "secret")
        ce._reader = give_key
        secret = ce.encrypt("topsecret")
        decrypt = ce.decrypt(secret)
        self.assertEqual(decrypt, "topsecret")

    def test__hhh_is_timedout(self):
        ce = CryptoEngine.get()
        ce._timeout = 1
        time.sleep(1.1)
        self.assertTrue(ce._is_timedout())
        self.assertIsNone(ce._cipher)
        self.assertFalse(ce._is_authenticated())
