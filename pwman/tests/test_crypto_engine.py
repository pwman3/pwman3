import unittest
import pwman.util.config as config
from pwman.util.callback import Callback
import os
from pwman.util.crypto_engine import (CryptoEngine, CryptoException)
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

#config.set_defaults(default_config)

give_key = lambda msg: "12345"
give_wrong_key = lambda msg: "verywrongtkey"

salt = b'cUDHNMJdTRxiIDPXuT163UMvi4fd2pXz/bRg2Zm8ajE='
digest = b'9eaec7dc1ee647338406739c54dbf9c4881c74702008eb978622811cfc46a07f'


class DummyCallback(Callback):

    def getinput(self, question):
        return u'12345'

    def getsecret(self, question):
        return u'12345'

    def getnewsecret(self, question):
        return u'12345'


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
        self.assertFalse(ce.authenticate('verywrong'))
        self.assertTrue(ce.authenticate('12345'))
        ce._timeout = -1
        self.assertTrue(ce._is_authenticated())

    def test6_is_timedout(self):
        ce = CryptoEngine.get()
        ce._timeout = 1
        time.sleep(1.1)
        self.assertTrue(ce._is_timedout())
        self.assertIsNone(ce._cipher)
        self.assertFalse(ce._is_authenticated())

    def test_f_encrypt_decrypt(self):
        ce = CryptoEngine.get()
        ce._reader = give_key
        if not ce._salt:
            ce._salt = salt
        secret = ce.encrypt("topsecret")
        decrypt = ce.decrypt(secret)
        self.assertEqual(decrypt.decode(), "topsecret")
        ce._cipher = None
        secret = ce.encrypt("topsecret")
        decrypt = ce.decrypt(secret)
        self.assertEqual(decrypt.decode(), "topsecret")

    def test_g_encrypt_decrypt_wrong_pass(self):
        ce = CryptoEngine.get()
        ce._cipher = None
        ce._getsecret = give_wrong_key
        self.assertRaises(CryptoException, ce.encrypt, "secret")
        ce._getsecret = lambda x: u'12345'
        secret = ce.encrypt(u"topsecret")
        decrypt = ce.decrypt(secret)
        self.assertEqual(decrypt.decode(), "topsecret")

if __name__ == '__main__':
    unittest.main(verbosity=1, failfast=True)
