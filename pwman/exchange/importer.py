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
'''
A module to hold the importer class
'''
import csv
from pwman.data.nodes import Node
from pwman.util.crypto_engine import CryptoEngine
from pwman.ui.tools import CLICallback


class BaseImporter(object):  # pragma: no cover

    """
    The base class which defines the action needed to import data
    to pwman database
    """

    def __init__(self):
        pass


class CSVImporter(BaseImporter):

    """
    A reference implementation which imports a CSV to the pwman database
    """
    def __init__(self, args, config, db):
        self.args = args
        self.config = config
        self._db = db

    def _read_file(self):
        """read the csv file, remove empty lines and the header"""
        inp1 = self.args.import_file[0]
        inp2 = self.args.import_file[1]
        # Check if import_file[0] or [1] is the delimitter
        try:
            csv_f = csv.reader(inp1, delimiter=inp2)
        except IOerror:
            csv_f = csv.reader(inp2, delimiter=inp1)
        lines = [line for line in csv_f]
        lines = list(filter(None, lines))
        return lines[1:]

    def _create_node(self, row):
        """create a node object with encrypted properties"""
        # Check if delimiter matches file. 
        try:
            n = {'clear_text': True,
                 'username': row[0], 'password': row[2], 'url': row[1],
                 'notes': row[3],
                 'tags': row[4].split(',')}
            node = Node(**n)
        except IndexError as err:
            print '{}\nDid you specify the correct delimiter?'.format(err)
            sys.exit(1)
        return node

    def _insert_node(self, node):
        "insert the node object to the database"
        self._db.add_node(node)

    def _open_db(self):
        """
        open existing db or create a new db

        This will expect a CRYPTO table!
        Hence if not CRYPTO table one should create it...
        """
        self._db._open()
        self._db._create_tables()
        self._db._con.commit()
        self._db.open()

    def run(self, callback=CLICallback):

        enc = CryptoEngine.get()
        enc.callback = callback()
        self._open_db()

        for row in self._read_file():
            node = self._create_node(row)
            self._insert_node(node)

        self._db.close()


class Importer(object):

    """
    The actual job runner which by default runs a csv importer instance.
    This could be changes by calling other instance which for example import
    from KeePass XML or other formats.
    """
    def __init__(self,  args, invoke=CSVImporter):
        self.importer = invoke(*args)

    def run(self):  # pragma: no cover
        self.importer.run()
