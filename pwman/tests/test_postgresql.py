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
# Copyright (C) 2015 Oz Nahum Tiram <nahumoz@gmail.com>
# ============================================================================

import os
import unittest
import sys
from pwman.data.drivers.postgresql import PostgresqlDatabase
from pwman.data.nodes import Node
from pwman.util.crypto_engine import CryptoEngine
from .test_crypto_engine import give_key, DummyCallback
import psycopg2 as pg


class TestPostGresql(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        secret = open('secret.txt').readline().strip()
        u = "postgresql://oz123:%s@localhost/pwman" % secret
        self.db = PostgresqlDatabase(u)
        self.db._open()

    @classmethod
    def tearDownClass(self):

        self.db._cur.execute("TRUNCATE DBVERSION")

    def test_con(self):

        self.assertIsInstance(self.db._cur, pg._psycopg.cursor)

if __name__ == '__main__':

    ce = CryptoEngine.get()
    ce.callback = DummyCallback()
    ce.changepassword(reader=give_key)
    unittest.main(verbosity=2, failfast=True)
