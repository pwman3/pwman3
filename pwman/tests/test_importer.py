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
# Copyright (C) 2012, 2013, 2014 Oz Nahum Tiram <nahumoz@gmail.com>
# ============================================================================
import os
import unittest
from pwman.util.crypto_engine import CryptoEngine
from collections import namedtuple
from .test_crypto_engine import give_key, DummyCallback
from pwman.exchange.importer import CSVImporter
from pwman.data.drivers.sqlite import SQLite

import_example = """
Username;URL;Password;Notes;Tags
alice;wonderland.com;secert;scratch;foo,bar
hatman;behindthemirror.com;pa33w0rd;scratch;foo,bar
"""

with open('import_file.csv', 'w') as f:
    f.write(import_example)


class TestImporter(unittest.TestCase):

    def setUp(self):
        config = {}
        db = SQLite('test-importer.db')
        Args = namedtuple('args', 'import_file')
        self.importer = CSVImporter(Args(import_file='import_file.csv'),
                                    config, db)

    def test_read_file(self):
        lines = self.importer._read_file()
        self.assertNotIn(["Username", "URL", "Password", "Notes", " Tags"],
                         lines)

    def test_create_node(self):
        # create a node , should be encrypted, but not yet inserted to db
        n = "alice;wonderland.com;secert;scratch;foo,bar".split(";")
        node = self.importer._create_node(n)
        ce = CryptoEngine.get()
        self.assertEqual(ce.decrypt(node._username).decode(), u'alice')
        self.assertEqual(['foo', 'bar'], [t for t in node.tags])

    def test_insert_node(self):
        n = "alice;wonderland.com;secert;scratch;foo,bar".split(";")
        node = self.importer._create_node(n)
        self.importer._open_db()
        # do the actual insert of the node to the databse
        self.importer._insert_node(node)

    def test_runner(self):
        # test the whole procees:
        """
          open csv
          open db
          for line in csv:
              create node
              insert node

          close db
        """
        pass


if __name__ == '__main__':

    ce = CryptoEngine.get()
    ce.callback = DummyCallback()
    ce.changepassword(reader=give_key)
    try:
        unittest.main(verbosity=2, failfast=True)
    except SystemExit:
        os.remove('import_file.csv')
