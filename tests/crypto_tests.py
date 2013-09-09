import pwman.util.config as config
import pwman.data.factory
from pwman.data.nodes import NewNode
from pwman.data.tags import Tag

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
        # TODO: set config to no algorithm
        # check that the proper exception is raised
        self.assertRaises()

        # TODO: write a white box test for each
        #       method in CryptoEngine



