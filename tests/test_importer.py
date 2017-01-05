# ============================================================================
# This file is part of Pwman3.
#
# Pwman3 is free software; you can redistribute iut and/or modify
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
# Copyright (C) 2012-2017 Oz Nahum Tiram <oz.tiram@gmail.com>
# ============================================================================
import os
import unittest
import sys

from collections import namedtuple
import pwman.data.factory
from pwman.util.crypto_engine import CryptoEngine
from pwman.exchange.importer import CSVImporter, Importer
from pwman.data.drivers.sqlite import SQLite
from .test_crypto_engine import give_key, DummyCallback

import_example = """
Username;URL;Password;Notes;Tags
alice;wonderland.com;secert;scratch;foo,bar
hatman;behindthemirror.com;pa33w0rd;scratch;foo,bar
"""


class TestImporter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        f = open('import_file.csv', 'w')
        f.write(import_example)
        f.close()

    @classmethod
    def tearDownClass(cls):
        for item in ('import_file.csv', 'test-importer.db',
                     'testfile.conf', 'importdummy.db'):
            try:
                os.unlink(item)
            except OSError:
                continue

    def setUp(self):
        config = {}
        db = SQLite('test-importer.db')
        Args = namedtuple('args', 'file_delim')
        args = Args(file_delim=['import_file.csv', ';'])
        self.importer = CSVImporter(args,
                                    config, db)

    def test_1_read_file(self):
        lines = self.importer._read_file()
        self.assertNotIn(["Username", "URL", "Password", "Notes", " Tags"],
                         lines)

    def test_2_create_node(self):
        # create a node , should be encrypted, but not yet inserted to db
        n = "alice;wonderland.com;secert;scratch;foo,bar".split(";")
        node = self.importer._create_node(n)
        ce = CryptoEngine.get()
        self.assertEqual(ce.decrypt(node._username).decode(), u'alice')
        self.assertEqual([b'foo', b'bar'], [t for t in node.tags])

    def test_3_insert_node(self):
        self.importer._open_db()
        n = "alice;wonderland.com;secert;scratch;foo,bar".split(";")
        node = self.importer._create_node(n)
        # do the actual insert of the node to the databse
        self.importer._insert_node(node)

    def test_4_runner(self):
        # test the whole procees:
        """
          open csv
          open db
          for line in csv:
              create node
              insert node

          close db
        """

        # args need import_file , db,
        Args = namedtuple('Args', 'file_delim, db')
        if os.path.exists('importdummy.db'):
            os.unlink('importdummy.db')
        args = Args(file_delim=['import_file.csv', ';'], db='importdummy.db')
        p = os.getcwd()
        if sys.platform.startswith("win"):
            p = p.strip("C:\\")
            print(os.getcwd())

        db = pwman.data.factory.createdb('sqlite:///' + p +
                                         '/importdummy.db', 0.6)
        importer = Importer((args, '', db))
        importer.importer.run(callback=DummyCallback)


if __name__ == '__main__':

    ce = CryptoEngine.get()
    ce.callback = DummyCallback()
    ce.changepassword(reader=give_key)
    unittest.main(verbosity=2, failfast=True)
