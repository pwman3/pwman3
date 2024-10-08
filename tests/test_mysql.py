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

"""
setting up mysql for testing

$ mysql -u root -h localhost -p

mysql > CREATE DATABASE pwmantest;
mysql > CREATE USER pwman IDENTIFIED BY '123456';
mysql > GRANT ALL on pwmantest.* to 'pwman'@'localhost';
"""
import os
import unittest
import time

from urllib.parse import urlparse

import pymysql

from pwman.data.drivers.mysql import MySQLDatabase
from pwman.util.crypto_engine import CryptoEngine

from .test_crypto_engine import give_key, DummyCallback


MYSQLHOST = os.getenv("MYSQLHOST", "localhost")


class TestMySQLDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.DBURI = "mysql://pwman:123456@%s:3306/pwmantest" % MYSQLHOST
        self.db = MySQLDatabase(urlparse(self.DBURI))
        self.db._open()

    @classmethod
    def tearDownClass(self):
        for table in ['LOOKUP', 'TAG', 'NODE', 'DBVERSION', 'CRYPTO']:
            try:
                self.db._cur.execute("DROP TABLE {}".format(table))
            except Exception:
                pass
            self.db._con.commit()

    def test_1_con(self):
        self.assertIsInstance(self.db._con, pymysql.connections.Connection)

    def test_2_create_tables(self):
        self.db._create_tables()
        self.assertTrue(self.db._check_tables())
        # invoking this method a second time should not raise an exception
        self.db._create_tables()
        self.assertTrue(self.db._check_tables())

    def test_3_load_key(self):
        self.db.savekey('SECRET$6$KEY')
        secretkey = self.db.loadkey()
        self.assertEqual(secretkey, 'SECRET$6$KEY')

    def test_4_save_crypto(self):
        self.db.save_crypto_info("TOP", "SECRET")
        secretkey = self.db.loadkey()
        self.assertEqual(secretkey, 'TOP$6$SECRET')
        row = self.db.fetch_crypto_info()
        self.assertEqual(row, ('TOP', 'SECRET'))

    def test_5_add_node(self):
        innode = ["TBONE", "S3K43T", "example.org", "some note",
                  ["bartag", "footag"]]
        self.db.add_node(innode)
        node, tags = list(self.db.getnodes([1]))[0]

        self.assertEqual(innode[:-1] + [t for t in innode[-1]], node[1:] + tags)

    def test_6_list_nodes(self):
        ret = self.db.lazy_list_node_ids()
        self.assertEqual(list(ret), [1])
        ret = self.db.lazy_list_node_ids("footag")
        ret = list(ret)
        self.assertEqual(ret, [1])

    def test_6a_list_tags(self):
        ret = self.db.listtags()
        self.assertListEqual(ret, ['bartag', 'footag'])

    def test_6b_get_nodes(self):
        node_tags = list(self.db.getnodes([1]))
        self.assertTupleEqual(node_tags[0],
                             ([1, "TBONE", "S3K43T", "example.org", "some note"],
                              ["bartag", "footag"])
                             )

    def test_7_get_or_create_tag(self):
        s = self.db._get_or_create_tag("SECRET")
        s1 = self.db._get_or_create_tag("SECRET")

        self.assertEqual(s, s1)

    def test_7a_clean_orphans(self):

        self.db._clean_orphans()
        rv = self.db._get_tag("SECRET")
        self.assertIsNone(rv)

    def test_8_remove_node(self):
        self.db.removenodes([1])
        n = list(self.db.lazy_list_node_ids())
        self.assertEqual(len(n), 0)

    def test_9_check_db_version(self):

        dburi = self.DBURI
        v = self.db.check_db_version(urlparse(dburi))
        self.assertEqual(v, '0.6')
        self.db._cur.execute("DROP TABLE DBVERSION")
        self.db._con.commit()
        v = self.db.check_db_version(urlparse(dburi))
        self.assertEqual(v, '0.6')
        self.db._cur.execute("CREATE TABLE DBVERSION("
                             "VERSION TEXT NOT NULL) ")
        self.db._con.commit()

MARIADBHOST = os.getenv("MARIADBHOST", "localhost")

class TestMariaDBDatabase(TestMySQLDatabase):

    @classmethod
    def setUpClass(self):
        self.DBURI = "mysql://pwman:123456@%s:3308/pwmantest" % MARIADBHOST
        self.db = MySQLDatabase(urlparse(self.DBURI))
        self.db._open()

if __name__ == '__main__':

    ce = CryptoEngine.get()
    ce.callback = DummyCallback()
    ce.changepassword(reader=give_key)
    unittest.main(verbosity=2, failfast=int(os.getenv("PWMAN_FAILFAST", 1)))
