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
# Copyright (C) 2013 Oz Nahum <nahumoz@gmail.com>
# ============================================================================

from pwman.data.nodes import NewNode
from pwman.data.tags import TagNew
from pwman.data import factory
from pwman.data.drivers.sqlite import DatabaseException, SQLiteDatabaseNewForm
from pwman.util import config
from pwman.util.config import get_pass_conf
from pwman.util.generator import leetlist
from pwman.util.crypto import CryptoEngine, CryptoBadKeyException
from pwman import default_config, set_xsel
from pwman.ui import get_ui_platform
from pwman.ui.tools import CMDLoop, CliMenuItem
from pwman import (parser_options, get_conf_options, get_conf_file, set_umask)
from pwman.data.database import __DB_FORMAT__
from pwman.ui.mac import PwmanCliMacNew
from pwman.ui.win import PwmanCliWinNew
from collections import namedtuple
import sys
import unittest
if sys.version_info.major > 2:
    from io import StringIO
else:
    import StringIO
import os
import os.path

dummyfile = """
[Encryption]

[Readline]

[Global]
xsel = /usr/bin/xsel
colors = yes
umask = 0100
cls_timeout = 5

[Database]
"""


def node_factory(username, password, url, notes, tags=None):
    node = NewNode()
    node.username = username
    node.password = password
    node.url = url
    node.notes = notes
    tags = [TagNew(tn) for tn in tags]
    node.tags = tags

    return node

_saveconfig = False

PwmanCliNew, OSX = get_ui_platform(sys.platform)


from test_tools import (SetupTester, DummyCallback2,
                        DummyCallback3, DummyCallback4)


class DBTests(unittest.TestCase):

    """test everything related to db"""

    def setUp(self):
        "test that the right db instance was created"
        dbver = __DB_FORMAT__
        self.dbtype = config.get_value("Database", "type")
        self.db = factory.create(self.dbtype, dbver)
        self.tester = SetupTester(dbver)
        self.tester.create()

    def test_db_created(self):
        "test that the right db instance was created"
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
        # node = NewNode(username, password, url, notes)
        node = NewNode()
        node.username = username
        node.password = password
        node.url = url
        node.notes = notes
        # node = NewNode(username, password, url, notes)
        tags = [TagNew(tn) for tn in ['testing1', 'testing2']]
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
        enc = CryptoEngine.get()
        enc._callback = DummyCallback2()
        self.assertRaises(CryptoBadKeyException,
                          self.tester.cli._db.changepassword)

    def test_db_change_pass(self):
        "fuck yeah, we change the password and the new dummy works"
        enc = CryptoEngine.get()
        enc._callback = DummyCallback3()
        self.tester.cli._db.changepassword()
        self.tester.cli.do_forget('')
        enc._callback = DummyCallback4()
        self.tester.cli.do_ls('')

    def test_db_list_tags(self):
        # tags are return as ecrypted strings
        tags = self.tester.cli._db.listtags()
        self.assertEqual(2, len(tags))
        self.tester.cli.do_filter('testing1')
        tags = self.tester.cli._db.listtags()
        self.assertEqual(2, len(tags))
        self.tester.cli.do_ls('')

    def test_db_remove_node(self):
        node = self.tester.cli._db.getnodes([1])
        self.tester.cli._db.removenodes(node)
        # create the removed node again
        node = NewNode()
        node.username = 'tester'
        node.password = 'Password'
        node.url = 'example.org'
        node.notes = 'some notes'
        tags = [TagNew(tn) for tn in ['testing1', 'testing2']]
        node.tags = tags
        self.db.open()
        self.db.addnodes([node])

    def test_sqlite_init(self):
        db = SQLiteDatabaseNewForm("test")
        self.assertEquals("test", db._filename)


class TestDBFalseConfig(unittest.TestCase):

    def setUp(self):
        # filename = default_config['Database'].pop('filename')
        self.fname1 = default_config['Database'].pop('filename')
        self.fname = config._conf['Database'].pop('filename')

    def test_db_missing_conf_parameter(self):
        self.assertRaises(DatabaseException, factory.create,
                          'SQLite', __DB_FORMAT__)

    def test_get_ui_platform(self):
        uiclass, osx = get_ui_platform('windows')
        self.assertFalse(osx)
        self.assertEqual(uiclass.__name__, PwmanCliWinNew.__name__)
        uiclass, osx = get_ui_platform('darwin')
        self.assertTrue(osx)
        self.assertEqual(uiclass.__name__, PwmanCliMacNew.__name__)
        del(uiclass)
        del(osx)

    def tearDown(self):
        config.set_value('Database', 'filename', self.fname)
        default_config['Database']['filename'] = self.fname1
        config._conf['Database']['filename'] = self.fname


class CLITests(unittest.TestCase):

    """
    test command line functionallity
    """

    def setUp(self):
        "test that the right db instance was created"
        self.dbtype = config.get_value("Database", "type")
        self.db = factory.create(self.dbtype, __DB_FORMAT__)
        self.tester = SetupTester(__DB_FORMAT__)
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

    def test_random_leet_password(self):
        password = self.tester.cli.get_password(None, leetify=True, length=7)
        l_num = 0
        for v in leetlist.values():
            if v in password:
                l_num += 1
        # sometime despite all efforts, randomness dictates that no
        # leetifying happens ...
        self.assertTrue(l_num >= 0)

    def test_leet_password(self):
        password = self.tester.cli.get_password(None, leetify=True,
                                                reader=lambda x: u'HAtman')
        self.assertRegexpMatches(password, ("(H|h)?(A|a|4)?(T|t|\+)?(m|M|\|"
                                            "\/\|)?(A|a|4)?(N|n|\|\\|)?"))

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
        # node = NewNode('alice', 'dough!', 'example.com',
        #               'lorem impsum')
        node = NewNode()
        node.username = 'alice'
        node.password = 'dough!'
        node.url = 'example.com'
        node.notes = 'somenotes'
        node.tags = 'lorem ipsum'

        tags = self.tester.cli.get_tags(reader=lambda: u'looking glass')
        node.tags = tags
        self.tester.cli._db.addnodes([node])
        self.tester.cli._db._cur.execute(
            "SELECT ID FROM NODES ORDER BY ID ASC", [])
        rows = self.tester.cli._db._cur.fetchall()

        # by now the db should have 2 new nodes
        # the first one was added by test_create_node in DBTests
        # the second was added just now.
        # This will pass only when running all the tests then ...
        self.assertEqual(len(rows), 2)

        node = NewNode()
        node.username = 'alice'
        node.password = 'dough!'
        node.url = 'example.com'
        node.notes = 'somenotes'
        node.tags = 'lorem ipsum'

        tags = self.tester.cli.get_tags(reader=lambda: u'looking glass')
        node.tags = tags
        self.tester.cli._db.addnodes([node])

    def test_get_ids(self):
        # used by do_cp or do_open,
        # this spits many time could not understand your input
        self.assertEqual([1], self.tester.cli.get_ids('1'))
        self.assertListEqual([1, 2, 3, 4, 5], self.tester.cli.get_ids('1-5'))
        self.assertListEqual([], self.tester.cli.get_ids('5-1'))
        self.assertListEqual([], self.tester.cli.get_ids('5x-1'))
        self.assertListEqual([], self.tester.cli.get_ids('5x'))
        self.assertListEqual([], self.tester.cli.get_ids('5\\'))

    def test_edit(self):
        node = self.tester.cli._db.getnodes([2])[0]
        menu = CMDLoop()
        menu.add(CliMenuItem("Username", self.tester.cli.get_username,
                             node.username,
                             node.username))
        menu.add(CliMenuItem("Password", self.tester.cli.get_password,
                             node.password,
                             node.password))
        menu.add(CliMenuItem("Url", self.tester.cli.get_url,
                             node.url,
                             node.url))
        menunotes = CliMenuItem("Notes",
                                self.tester.cli.get_notes(reader=lambda:
                                                          u'bla bla'),
                                node.notes,
                                node.notes)
        menu.add(menunotes)
        menu.add(CliMenuItem("Tags", self.tester.cli.get_tags,
                             node.tags,
                             node.tags))

        dummy_stdin = StringIO.StringIO('4\n\nX')
        self.assertTrue(len(dummy_stdin.readlines()))
        dummy_stdin.seek(0)
        sys.stdin = dummy_stdin
        menu.run(node)
        self.tester.cli._db.editnode(2, node)
        sys.stdin = sys.__stdin__

    def test_get_pass_conf(self):
        numerics, leet, s_chars = get_pass_conf()
        self.assertFalse(numerics)
        self.assertFalse(leet)
        self.assertFalse(s_chars)

    def test_do_tags(self):
        self.tester.cli.do_filter('bank')

    def test_do_forget(self):
        self.tester.cli.do_forget('')

    def test_do_auth(self):
        crypto = CryptoEngine.get()
        crypto.auth('12345')

    def test_do_clear(self):
        self.tester.cli.do_clear('')

    def test_do_exit(self):
        self.assertTrue(self.tester.cli.do_exit(''))


class FakeSqlite(object):

    def check_db_version(self):
        return ""


class FactoryTest(unittest.TestCase):

    def test_factory_check_db_ver(self):
        self.assertEquals(factory.check_db_version('SQLite'), 0.5)

    def test_factory_check_db_file(self):
        orig_sqlite = getattr(factory, 'sqlite')
        factory.sqlite = FakeSqlite()
        self.assertEquals(factory.check_db_version('SQLite'), 0.3)
        factory.sqlite = orig_sqlite

    def test_factory_create(self):
        db = factory.create('SQLite', filename='foo.db')
        db._open()
        self.assertTrue(os.path.exists('foo.db'))
        os.unlink('foo.db')
        self.assertIsInstance(db, SQLiteDatabaseNewForm)
        self.assertRaises(DatabaseException, factory.create, 'UNKNOWN')


class ConfigTest(unittest.TestCase):

    def setUp(self):
        "test that the right db instance was created"
        dbver = 0.4
        self.dbtype = config.get_value("Database", "type")
        self.db = factory.create(self.dbtype, dbver)
        self.tester = SetupTester(dbver)
        self.tester.create()
        self.orig_config = config._conf.copy()
        self.orig_config['Encryption'] = {'algorithm': 'AES'}

    def test_config_write(self):
        _filename = os.path.join(os.path.dirname(__file__),
                                 'testing_config')
        config._file = _filename
        config.save(_filename)
        self.assertTrue(_filename)
        os.remove(_filename)

    def test_config_write_with_none(self):
        _filename = os.path.join(os.path.dirname(__file__),
                                 'testing_config')
        config._file = _filename
        config.save()
        self.assertTrue(os.path.exists(_filename))
        os.remove(_filename)

    def test_write_no_permission(self):
        # this test will pass if you run as root ...
        # assuming you are not doing something like that
        self.assertRaises(config.ConfigException, config.save,
                          '/root/test_config')

    def test_add_default(self):
        config.add_defaults({'Section1': {'name': 'value'}})
        self.assertIn('Section1', config._defaults)
        config._defaults.pop('Section1')

    def test_get_conf(self):
        cnf = config.get_conf()
        cnf_keys = cnf.keys()
        self.assertTrue('Encryption' in cnf_keys)
        self.assertTrue('Readline' in cnf_keys)
        self.assertTrue('Global' in cnf_keys)
        self.assertTrue('Database' in cnf_keys)

    def test_load_conf(self):
        self.assertRaises(config.ConfigException, config.load, 'NoSuchFile')
        # Everything should be ok
        config.save('TestConfig.ini')
        config.load('TestConfig.ini')
        # let's corrupt the file
        cfg = open('TestConfig.ini', 'w')
        cfg.write('Corruption')
        cfg.close()
        self.assertRaises(config.ConfigException, config.load,
                          'TestConfig.ini')
        os.remove('TestConfig.ini')

    def test_all_config(self):
        sys.argv = ['pwman3']
        default_config['Database'] = {'type': '',
                                      'filename': ''}
        _save_conf = config._conf.copy()
        config._conf = {}
        with open('dummy.conf', 'w') as dummy:
            dummy.write(dummyfile)
        sys.argv = ['pwman3', '-d', '', '-c', 'dummy.conf']
        p2 = parser_options()
        args = p2.parse_args()
        self.assertRaises(Exception, get_conf_options, args, False)
        config._conf = _save_conf.copy()
        os.unlink('dummy.conf')

    def test_set_xsel(self):
        set_xsel(config, False)

        set_xsel(config, True)
        if sys.platform == 'linux2':
            self.assertEqual(None, config._conf['Global']['xsel'])

    def test_get_conf_file(self):
        Args = namedtuple('args', 'cfile')
        args = Args(cfile='nosuchfile')
        # setting the default
        # in case the user specifies cfile as command line option
        # and that file does not exist!
        foo = config._conf.copy()
        get_conf_file(args)
        # args.cfile does not exist, hence the config values
        # should be the same as in the defaults
        config.set_config(foo)

    def test_get_conf_options(self):
        Args = namedtuple('args', 'cfile, dbase, algo')
        args = Args(cfile='nosuchfile', dbase='dummy.db', algo='AES')
        self.assertRaises(Exception, get_conf_options, (args, 'False'))
        config._defaults['Database']['type'] = 'SQLite'
        # config._conf['Database']['type'] = 'SQLite'
        xsel, dbtype = get_conf_options(args, 'True')
        self.assertEqual(dbtype, 'SQLite')

    def test_set_conf(self):
        set_conf_f = getattr(config, 'set_conf')
        private_conf = getattr(config, '_conf')
        set_conf_f({'Config': 'OK'})
        self.assertDictEqual({'Config': 'OK'}, config._conf)
        config._conf = private_conf

    def test_umask(self):
        config._defaults = {'Global': {}}
        self.assertRaises(config.ConfigException, set_umask, config)

    def tearDown(self):
        config._conf = self.orig_config.copy()
