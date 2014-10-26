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
from StringIO import StringIO
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

    def test_false(self):
        self.assertFalse(False)

    def test_get_tags(self):
        sys.stdin = StringIO("foo bar baz\n")
        tags = self.tester.cli._get_tags(reader=lambda: "foo bar baz")
        self.assertListEqual(['foo', 'bar', 'baz'], tags)
        sys.stdin = sys.__stdin__

    def test_do_newn(self):
        sys.stdin = StringIO(("alice\nsecret\nexample.com\nsome notes"
                              "\nfoo bar baz"))
        _node = self.tester.cli.do_newn('')
        self.assertListEqual(['foo', 'bar', 'baz'], _node.tags)
        sys.stdin = sys.__stdin__
        nodeid = self.tester.cli._db.listnodes()
        self.assertListEqual([1], nodeid)
        nodes = self.tester.cli._db.getnodes(nodeid)
        ce = CryptoEngine.get()
        user = ce.decrypt(nodes[0][1])
        self.assertTrue(user, 'alice')
        tags = nodes[0][5:]
        for idx, t in enumerate(['foo', 'bar', 'baz']):
            self.assertTrue(t, tags[idx])


if __name__ == '__main__':

    ce = CryptoEngine.get()
    ce.callback = DummyCallback()
    ce.changepassword(reader=give_key)

    try:
        unittest.main(verbosity=2, failfast=True)
    except SystemExit:
        #os.remove(testdb)
        pass
