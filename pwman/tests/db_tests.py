from pwman.util.callback import Callback
import os
import os.path
import sys


class DummyCallback(Callback):

    def getinput(self, question):
        return '12345'

    def getsecret(self, question):
        return '12345'


class DummyCallback2(Callback):

    def getinput(self, question):
        return 'newsecret'

    def getsecret(self, question):
        return 'newsecret'
if 'darwin' in sys.platform:  # pragma: no cover
    from pwman.ui.mac import PwmanCliMac as PwmanCliOld
    from pwman.ui.mac import PwmanCliMacNew as PwmanCliNew
    OSX = True
elif 'win' in sys.platform:  # pragma: no cover
    from pwman.ui.cli import PwmanCli
    from pwman.ui.win import PwmanCliWinNew as PwmanCliNew
    OSX = False
else:
    from pwman.ui.cli import PwmanCliOld
    from pwman.ui.cli import PwmanCliNew
    OSX = False

import pwman.util.config as config
import pwman.data.factory
from pwman.data.nodes import NewNode
from pwman.data.tags import Tag, TagNew
from pwman.util.crypto import CryptoEngine, CryptoBadKeyException
from pwman import which, default_config
import unittest

_saveconfig = False

default_config['Database'] = {'type': 'SQLite',
                              'filename':
                              os.path.join(os.path.dirname(__file__),
                                           "test.pwman.db")
                              }


class SetupTester(object):

    def __init__(self):
        config.set_defaults(default_config)
        if not OSX:
            self.xselpath = which("xsel")
            config.set_value("Global", "xsel", self.xselpath)
        else:
            self.xselpath = "xsel"

    def clean(self):
        if os.path.exists(config.get_value('Database', 'filename')):
            os.remove(config.get_value('Database', 'filename'))

        if os.path.exists(os.path.join(os.path.dirname(__file__),
                                       'testing_config')):
            os.remove(os.path.join(os.path.dirname(__file__),
                                   'testing_config'))

    def create(self):
        dbver = 0.4
        dbtype = config.get_value("Database", "type")
        db = pwman.data.factory.create(dbtype, dbver)
        self.cli = PwmanCliNew(db, self.xselpath, DummyCallback)


class DBTests(unittest.TestCase):
    """test everything related to db"""

    def setUp(self):
        "test that the right db instance was created"
        dbver = 0.4
        self.dbtype = config.get_value("Database", "type")
        self.db = pwman.data.factory.create(self.dbtype, dbver)
        self.tester = SetupTester()
        self.tester.create()

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
            self.assertEquals(attr, getattr(new_node, key))
        self.db.close()

    def test_tags(self):
        enc = CryptoEngine.get()
        got_tags = self.tester.cli._tags(enc)
        self.assertEqual(2, len(got_tags))

    def test_change_pass(self):
        self.tester.cli.callback = DummyCallback2
        self.assertRaises(CryptoBadKeyException,
                          self.tester.cli._db.changepassword)


class CLITests(unittest.TestCase):
    """
    test command line functionallity
    """

    def setUp(self):
        "test that the right db instance was created"
        dbver = 0.4
        self.dbtype = config.get_value("Database", "type")
        self.db = pwman.data.factory.create(self.dbtype, dbver)
        self.tester = SetupTester()
        self.tester.create()

    def test_input(self):
        name = self.tester.cli.get_username(reader=lambda: u'alice')
        self.assertEqual(name, u'alice')

    def test_password(self):
        password = self.tester.cli.get_password(None,
                                                reader=lambda x: u'hatman')
        self.assertEqual(password, u'hatman')

    def test_random_password(self):
        password = self.tester.cli.get_password(None, length=7)
        self.assertEqual(len(password), 7)

    def test_get_url(self):
        url = self.tester.cli.get_url(reader=lambda: u'example.com')
        self.assertEqual(url, u'example.com')

    def test_get_notes(self):
        notes = self.tester.cli.get_notes(reader=lambda:
                                          u'test 123\n test 456')
        self.assertEqual(notes, u'test 123\n test 456')

    def test_get_tags(self):
        tags = self.tester.cli.get_tags(reader=lambda: u'looking glass')
        for t in tags:
            self.assertIsInstance(t, TagNew)

        for t, n in zip(tags, 'looking glass'.split()):
            self.assertEqual(t.name.strip(), n)

    # creating all the components of the node does
    # the node is still not added !

    def test_add_new_entry(self):
        node = NewNode('alice', 'dough!', 'example.com',
                       'lorem impsum')
        tags = self.tester.cli.get_tags(reader=lambda: u'looking glass')
        node.tags = tags
        self.tester.cli._db.addnodes([node])
        self.tester.cli._db._cur.execute(
            "SELECT ID FROM NODES ORDER BY ID ASC", [])
        rows = self.tester.cli._db._cur.fetchall()

        # by now the db should have 2 new nodes
        # the first one was added by test_create_node in DBTests
        # the second was added just now.
        # This will pass only when running all the tests than ...
        self.assertEqual(len(rows), 2)

    def test_get_ids(self):
        #used by do_cp or do_open,
        # this spits many time could not understand your input
        self.assertEqual([1], self.tester.cli.get_ids('1'))
        self.assertListEqual([1, 2, 3, 4, 5], self.tester.cli.get_ids('1-5'))
        self.assertListEqual([], self.tester.cli.get_ids('5-1'))
        self.assertListEqual([], self.tester.cli.get_ids('5x-1'))
        self.assertListEqual([], self.tester.cli.get_ids('5x'))
        self.assertListEqual([], self.tester.cli.get_ids('5\\'))


class ConfigTest(unittest.TestCase):

    def setUp(self):
        "test that the right db instance was created"
        dbver = 0.4
        self.dbtype = config.get_value("Database", "type")
        self.db = pwman.data.factory.create(self.dbtype, dbver)
        self.tester = SetupTester()
        self.tester.create()

    def test_config_write(self):
        config.save(os.path.join(os.path.dirname(__file__), 'testing_config'))

    def test_config_write_with_none(self):
        config._file = os.path.join(os.path.dirname(__file__),
                                    'testing_config')
        config.save()

    def test_write_no_permission(self):
        # this test will pass if you run as root ...
        # assuming you are not doing something like that
        self.assertRaises(config.ConfigException, config.save,
                          '/root/test_config')

    def test_add_default(self):
        config.add_defaults({'Section1': {'name': 'value'}})
        self.assertIn('Section1', config._defaults)
