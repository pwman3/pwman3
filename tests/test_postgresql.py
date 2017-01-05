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
# Copyright (C) 2015-2017 Oz Nahum Tiram <nahumoz@gmail.com>
# ============================================================================
import unittest
import sys
from .test_crypto_engine import give_key, DummyCallback
if sys.version_info.major > 2:  # pragma: no cover
    from urllib.parse import urlparse
else:  # pragma: no cover
    from urlparse import urlparse
import psycopg2 as pg
from pwman.data.drivers.postgresql import PostgresqlDatabase
from pwman.util.crypto_engine import CryptoEngine
##
# testing on linux host
# su - postgres
# psql
# postgres=# CREATE USER tester WITH PASSWORD '123456';
# postgres=# grant ALL ON DATABASE pwman to tester;
#
##


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

    def test_1_con(self):
        self.assertIsInstance(self.db._cur, pg._psycopg.cursor)

    def test_2_create_tables(self):
        self.db._create_tables()
        # invoking this method a second time should not raise an exception
        self.db._create_tables()

    def test_3_load_key(self):
        self.db.savekey('SECRET$6$KEY')
        secretkey = self.db.loadkey()
        self.assertEqual(secretkey, b'SECRET$6$KEY')

    def test_4_save_crypto(self):
        self.db.save_crypto_info(b"TOP", b"SECRET")
        secretkey = self.db.loadkey()
        self.assertEqual(secretkey, b'TOP$6$SECRET')
        row = self.db.fetch_crypto_info()
        self.assertEqual(list(map(bytearray, row)),
                         [bytearray(b'TOP'), bytearray(b'SECRET')])

    def test_5_add_node(self):
        innode = [b"TBONE", b"S3K43T", b"example.org", b"some note",
                  [b"footag", b"bartag"]]
        self.db.add_node(innode)
        outnode = self.db.getnodes([1])[0]
        self.assertEqual(innode[:-1] + [t for t in innode[-1]], outnode[1:])

    def test_6_list_nodes(self):
        ret1 = self.db.listnodes()
        self.assertEqual(ret1, [1])
        ret2 = self.db.listnodes(b"footag")
        self.assertEqual(ret2, [1])

    def test_6a_list_tags(self):
        ret = self.db.listtags()
        self.assertListEqual(ret, [b'footag', b'bartag'])

    def test_6b_get_nodes(self):
        ret = self.db.getnodes([1])
        retb = self.db.getnodes([])
        self.assertListEqual(ret, retb)

    def test_7_get_or_create_tag(self):
        s = self.db._get_or_create_tag(b"SECRET")
        s1 = self.db._get_or_create_tag(b"SECRET")

        self.assertEqual(s, s1)

    def test_7a_clean_orphans(self):

        self.db._clean_orphans()
        rv = self.db._get_tag("SECRET")
        self.assertIsNone(rv)

    def test_8_remove_node(self):
        self.db.removenodes([1])
        n = self.db.listnodes()
        self.assertEqual(len(n), 0)

    def test_9_check_db_version(self):

        dburi = "postgresql://tester:123456@localhost/pwman"
        v = self.db.check_db_version(dburi)
        self.assertEqual(str(v), '0.6')
        self.db._cur.execute("DROP TABLE DBVERSION")
        self.db._con.commit()
        v = self.db.check_db_version(dburi)
        self.assertEqual(str(v), '0.6')
        self.db._cur.execute("CREATE TABLE DBVERSION("
                             "VERSION TEXT NOT NULL DEFAULT {}"
                             ")".format('0.6'))
        self.db._con.commit()


if __name__ == '__main__':

    ce = CryptoEngine.get()
    ce.callback = DummyCallback()
    ce.changepassword(reader=give_key)
    unittest.main(verbosity=2, failfast=True)
