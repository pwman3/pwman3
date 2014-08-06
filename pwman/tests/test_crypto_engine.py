import unittest
import pwman.util.config as config
import os
from pwman.util.crypto_engine import (write_password, save_a_secret_message,
                                      read_a_secret_message)

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


class CryptoEngineTest(unittest.TestCase):

    def test_a_write_password(self):
        write_password(reader=give_key)

    def test_b_save_secret(self):
        save_a_secret_message(reader=give_key)

    def test_c_read_secret(self):
        read_a_secret_message(reader=give_key)
