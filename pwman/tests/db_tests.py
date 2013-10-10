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


class DBTests(unittest.TestCase):
    """test everything related to db"""
    def setUp(self):
        "test that the right db instance was created"
        dbver = 0.4
        self.dbtype = config.get_value("Database", "type")
        self.db = pwman.data.factory.create(self.dbtype, dbver)

    def test_db_created(self):
        "test that the right db instance was created"
        # self.db = pwman.data.factory.create(dbtype, dbver)
        self.assertIn(self.dbtype, self.db.__class__.__name__)

    def test_db_opened(self):
        "db was successfuly opened"
        # it will have a file name associated
        self.assertTrue(hasattr(self.db, '_filename'))

    def test_create_node(self):
        "test that a node can be successfuly created"
        # this method does not test do_new
        # which is a UI method, rather we test
        # _db.addnodes
        username = 'tester'
        password = 'Password'
        url = 'example.org'
        notes = 'some notes'
        node = NewNode(username, password, url, notes)
        tags = [Tag(tn) for tn in ['testing1', 'testing2']]
        node.tags = tags
        self.db.open()
        self.db.addnodes([node])
        idx_created = node._id
        new_node = self.db.getnodes([idx_created])[0]
        for key, attr in {'password': password, 'username': username,
                          'url': url, 'notes': notes}.iteritems():
            self.assertEquals(attr, eval('new_node.'+key))

        self.db.close()


class CLITests(unittest.TestCase):
    """test command line functionallity"""
    def test(self):
        self.assertTrue(True)
