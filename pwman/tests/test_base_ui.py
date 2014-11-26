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
# Copyright (C) 2014 Oz Nahum Tiram <nahumoz@gmail.com>
# ============================================================================
import os
import unittest
from pwman.util.crypto_engine import CryptoEngine
from .test_crypto_engine import give_key, DummyCallback
from pwman.data.database import __DB_FORMAT__
from .test_tools import (SetupTester)
from pwman.data import factory
from pwman.ui import get_ui_platform
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import sys

testdb = os.path.join(os.path.dirname(__file__), "test-baseui.pwman.db")


class TestBaseUI(unittest.TestCase):

    def setUp(self):
        "test that the right db instance was created"
        dbver = __DB_FORMAT__
        self.dbtype = 'SQLite'
        self.db = factory.create(self.dbtype, dbver, testdb)
        self.tester = SetupTester(dbver, testdb)
        self.tester.create()

    def test_get_ui_platform(self):
        _, osx = get_ui_platform('darwin')
        self.assertTrue(osx)
        _, osx = get_ui_platform('win')
        self.assertFalse(osx)
        _, osx = get_ui_platform('foo')
        self.assertFalse(osx)

    def test_get_tags(self):
        sys.stdin = StringIO("foo bar baz\n")
        tags = self.tester.cli._get_tags(reader=lambda: "foo bar baz")
        self.assertListEqual(['foo', 'bar', 'baz'], tags)
        sys.stdin = sys.__stdin__

    def test_1_do_new(self):
        sys.stdin = StringIO(("alice\nsecret\nexample.com\nsome notes"
                              "\nfoo bar baz"))
        _node = self.tester.cli._do_new('')

        sys.stdin = sys.__stdin__
        self.assertListEqual(['foo', 'bar', 'baz'], [t.decode() for t
                                                     in _node.tags])
        nodeid = self.tester.cli._db.listnodes()
        self.assertListEqual([1], nodeid)
        nodes = self.tester.cli._db.getnodes(nodeid)
        ce = CryptoEngine.get()
        user = ce.decrypt(nodes[0][1])
        self.assertTrue(user, 'alice')
        tags = nodes[0][5:]
        for idx, t in enumerate(['foo', 'bar', 'baz']):
            self.assertTrue(t, tags[idx])

    def test_2_do_list(self):
        self.output = StringIO()
        self.saved_stdout = sys.stdout
        sys.stdout = self.output
        self.tester.cli.do_list('')
        self.tester.cli.do_list('foo')
        self.tester.cli.do_list('bar')
        sys.stdout = self.saved_stdout
        self.output.getvalue()

    def test_3_do_export(self):
        self.tester.cli.do_export("{'filename':'foo.csv'}")
        with open('foo.csv') as f:
            l = f.readlines()

        self.assertIn('alice;example.com;secret;some notes;foo,bar,baz', l[1])
        self.tester.cli.do_export("f")
        with open('pwman-export.csv') as f:
            l = f.readlines()
        self.assertIn('alice;example.com;secret;some notes;foo,bar,baz', l[1])

    def test_4_do_forget(self):
        self.tester.cli.do_forget('')
        ce = CryptoEngine.get()
        self.assertIsNone(ce._cipher)

if __name__ == '__main__':

    ce = CryptoEngine.get()
    ce.callback = DummyCallback()
    ce.changepassword(reader=give_key)

    try:
        unittest.main(verbosity=2, failfast=True)
    except SystemExit:
        #os.remove(testdb)
        pass
