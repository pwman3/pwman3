import os
import os.path

_saveconfig = True


import sys

if 'darwin' in sys.platform:
    from pwman.ui.mac import PwmanCliMac as PwmanCli
    from pwman.ui.mac import PwmanCliMacNew as PwmanCliNew
    OSX = True
elif 'win' in sys.platform:
    from pwman.ui.cli import PwmanCli
    from pwman.ui.win import PwmanCliWinNew as PwmanCliNew
    OSX = False
else:
    from pwman.ui.cli import PwmanCli
    from pwman.ui.cli import PwmanCliNew
    OSX = False


import pwman.util.config as config
import pwman.data.factory
from pwman.data.convertdb import PwmanConvertDB


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


class DBTests(unittest.TestCase):
    """test everything related to db"""
    def test(self):
        self.assertTrue(True)

    def test_db_created(self):
        "test that the right db instance was created"
        dbver = 0.4
        dbtype = config.get_value("Database", "type")
        self.db = pwman.data.factory.create(dbtype, dbver)
        self.assertIn(dbtype, self.db.__class__.__name__)

    def db_opened(self):
        """
        if the db was successfuly opened
        it will have a file name associated
        """
        self.assertTrue(hasattr(self.db, '_filename'))


class CLITests(unittest.TestCase):
    """test command line functionallity"""
    def test(self):
        self.assertTrue(True)
