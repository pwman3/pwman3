import pwman.util.config as config
import os
from pwman.util.crypto_engine import (CryptoEngine, CryptoException)
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
import unittest


class CryptoTest(unittest.TestCase):

    def test_no_algorithm(self):
        CryptoEngine._instance_new = None
        config.set_value('Encryption', 'algorithm', '')
        self.assertRaises((CryptoException,), CryptoEngine.get)
        config.set_value('Encryption', 'algorithm', 'AES')

    def test_getcipher(self):
        crypto = CryptoEngine()
        self.assertRaises((CryptoNoCallbackException,), crypto._getcipher)

    def test_prepare_data(self):
        obj = 'dummy_data'
        self.assertTrue(True)

    def test_get(self):
        CryptoEngine._instance_new = None
        old_engine = CryptoEngine.get(0.4)
        self.assertIsInstance(old_engine, CryptoEngineOld)
        CryptoEngine._instance = None
        new_engine = CryptoEngine.get(dbver=0.5)
        self.assertIsInstance(new_engine, CryptoEngine)
        self.assertFalse(isinstance(new_engine, CryptoEngineOld))
        CryptoEngine._instance = None
        old_engine = CryptoEngine.get()

    def test_alive(self):
        old_engine = CryptoEngine.get()
        self.assertTrue(old_engine.alive())
        old_engine._cipher = None
        self.assertFalse(old_engine.alive())
        CryptoEngine.get()


if __name__ == '__main__':
    unittest.main()
