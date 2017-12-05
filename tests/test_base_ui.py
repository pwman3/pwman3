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
import sys
from io import StringIO, BytesIO

from pwman.util.crypto_engine import CryptoEngine
from .test_crypto_engine import give_key, DummyCallback
from pwman.data.database import __DB_FORMAT__
from .test_tools import (SetupTester, testdb)
from pwman.data import factory
from pwman.data.nodes import Node


class dummy_stdin(object):

    def __init__(self):
        self.idx = -1
        self.ans = ['4', 'some fucking notes', 'X']

    def __call__(self, msg):
        self.idx += 1
        return self.ans[self.idx]


class TestBaseUI(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        for item in (testdb, 'foo.csv', 'pwman-export.csv'):
            try:
                os.unlink(item)
            except OSError:
                continue

        SetupTester().clean()

    def setUp(self):
        "test that the right db instance was created"
        dbver = __DB_FORMAT__
        self.db = factory.createdb('sqlite://' + testdb, dbver)
        self.tester = SetupTester(dbver, testdb)
        self.tester.create()

    def tearDown(self):
        #self.tester.cli.do_exit("")
        pass

    def test_get_tags(self):
        sys.stdin = StringIO("foo bar baz\n")
        tags = self.tester.cli._get_tags(reader=lambda: "foo bar baz")
        self.assertListEqual(['foo', 'bar', 'baz'], tags)
        sys.stdin = sys.__stdin__

    def test_1_do_new(self):
        sys.stdin = BytesIO((b"alice\nsecret\nexample.com\nsome notes"
                             b"\nfoo bar baz"))
        _node = self.tester.cli._do_new('')

        sys.stdin = sys.__stdin__
        self.assertListEqual([b'foo', b'bar', b'baz'], [t for t
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
        sys.stdout = self.output
        self.tester.cli.do_list('')
        self.tester.cli.do_list('foo')
        self.tester.cli.do_list('bar')
        sys.stdout = sys.__stdout__
        self.output.getvalue()

    def test_3_do_export(self):
        self.tester.cli.do_export("{'filename':'foo.csv'}")
        with open('foo.csv') as f:
            l = f.readlines()
        # on windows there is an extra empty line in the exported file
        self.assertIn('alice;example.com;secret;some notes;foo,bar,baz\n', l)
    def test_3a_do_export(self):
        self.tester.cli.do_export("f")
        with open('pwman-export.csv') as f:
            l = f.readlines()

        self.assertIn('alice;example.com;secret;some notes;foo,bar,baz\n', l)

    def test_4_do_forget(self):
        self.tester.cli.do_forget('')
        ce = CryptoEngine.get()
        self.assertIsNone(ce._cipher)

    def test_5_do_print(self):
        v = StringIO()
        sys.stdout = v
        self.tester.cli.do_print('1')
        self.assertIn('\x1b[31mUsername:\x1b[0m alice', v.getvalue())
        self.tester.cli.do_print('a')
        self.assertIn("print accepts only a single ID ...", v.getvalue())

        sys.stdout = sys.__stdout__

    def test_6_do_tags(self):
        v = StringIO()
        sys.stdout = v
        self.tester.cli.do_tags('1')
        v = v.getvalue()
        for t in ['foo', 'bar', 'baz']:
            t in v
        sys.stdout = sys.__stdout__

    def test_7_get_ids(self):
        # used by do_cp or do_open,
        # this spits many time could not understand your input
        self.assertEqual([1], self.tester.cli._get_ids('1'))
        self.assertListEqual([1, 2, 3, 4, 5], self.tester.cli._get_ids('1-5'))
        self.assertListEqual([], self.tester.cli._get_ids('5-1'))
        self.assertListEqual([], self.tester.cli._get_ids('5x-1'))
        self.assertListEqual([], self.tester.cli._get_ids('5x'))
        self.assertListEqual([], self.tester.cli._get_ids('5\\'))

    def test_8_do_edit_1(self):
        node = self.tester.cli._db.getnodes([1])[0]
        node = node[1:5] + [node[5:]]
        node = Node.from_encrypted_entries(*node)
        sys.stdin = StringIO(("1\nfoo\nx\n"))
        self.tester.cli.do_edit('1')
        v = StringIO()
        sys.stdin = sys.__stdin__
        sys.stdout = v
        self.tester.cli.do_print('1')
        self.assertIn('\x1b[31mUsername:\x1b[0m foo', v.getvalue())

    def test_8_do_edit_2(self):
        node = self.tester.cli._db.getnodes([1])[0]
        node = node[1:5] + [node[5:]]
        node = Node.from_encrypted_entries(*node)
        sys.stdin = StringIO(("2\ns3kr3t\nx\n"))
        self.tester.cli.do_edit('1')
        v = StringIO()
        sys.stdin = sys.__stdin__
        sys.stdout = v
        self.tester.cli.do_print('1')
        self.assertIn('\x1b[31mPassword:\x1b[0m s3kr3t', v.getvalue())

    def test_9_do_delete(self):
        self.assertIsNone(self.tester.cli._do_rm('x'))
        sys.stdin = StringIO("y\n")
        self.tester.cli.do_rm('1')
        sys.stdin = sys.__stdin__
        sys.stdout = StringIO()
        self.tester.cli.do_ls('')
        self.assertNotIn('alice', sys.stdout.getvalue())
        sys.stdout = sys.__stdout__

    def test_10_do_info(self):
        self.output = StringIO()
        sys.stdout = self.output
        self.tester.cli.do_info(b'')
        self.assertIn(testdb, sys.stdout.getvalue())

if __name__ == '__main__':

    ce = CryptoEngine.get()
    ce.callback = DummyCallback()
    ce.changepassword(reader=give_key)
    unittest.main(verbosity=2, failfast=True)
