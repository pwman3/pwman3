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
import unittest
import sys
from .test_crypto_engine import give_key, DummyCallback
if sys.version_info.major > 2:  # pragma: no cover
    from urllib.parse import urlparse
else:  # pragma: no cover
    from urlparse import urlparse
import psycopg2 as pg
from pwman.data.drivers.mysql import MySQLDatabase
from pwman.util.crypto_engine import CryptoEngine


class TestPostGresql(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        u = "postgresql://tester:123456@localhost/pwman"
        u = urlparse(u)
        # password required, for all hosts
        # u = "postgresql://<user>:<pass>@localhost/pwman"
        self.db = PostgresqlDatabase(u)
        self.db._open()

    @classmethod
    def tearDownClass(self):
        self.db._cur.execute("DROP TABLE LOOKUP")
        self.db._cur.execute("DROP TABLE TAG")
        self.db._cur.execute("DROP TABLE NODE")
        self.db._cur.execute("DROP TABLE DBVERSION")
        self.db._cur.execute("DROP TABLE CRYPTO")
        self.db._con.commit()
