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
from pwman.data.drivers.sqlite import SQLite
from pwman.data.nodes import Node
from pwman.util.crypto_engine import CryptoEngine


class TestSQLite(unittest.TestCase):
    def setUp(self):
        self.db = SQLite('test.db')
        self.db._open()

    def test_1_create_tables(self):
        self.db._create_tables()
        self.db._con.commit()
        # the method _open calls _create_tables
        self.db.save_crypto_info("foo", "bar")
        self.db._create_tables()

    def test_1a_create_tables(self):
        self.db._create_tables()

    def test_2_crypto_info(self):
        self.db._create_tables()
        self.db.save_crypto_info("foo", "bar")
        f = self.db.fetch_crypto_info()
        self.assertListEqual([u'foo', u'bar'], list(f))

    def test_3_add_node(self):
        node = Node(clear_text=True,
                    **{'username': u"alice", 'password': u"secret",
                       'url': u"wonderland.com",
                       'notes': u"a really great place",
                       'tags': [u'foo', u'bar']})
        self.db.add_node(node)
        rv = self.db._cur.execute("select * from node")
        # clearly this fails, while alice is not found in clear text in the
        # database!
        ce = CryptoEngine.get()
        res = rv.fetchone()
        self.assertIn(ce.encrypt(u'alice'), res[1])

    def test_4_test_tags(self):
        node = Node(clear_text=True,
                    **{'username': u"alice", 'password': u"secret",
                       'url': u"wonderland.com",
                       'notes': u"a really great place",
                       'tags': [u'foo', u'bar']})
        ce = CryptoEngine.get()
        self.db._get_or_create_tag(node._tags[0])
        self.assertEqual(1, self.db._get_or_create_tag(node._tags[0]))
        self.assertEqual(3, self.db._get_or_create_tag(ce.encrypt('baz')))

    def test_5_test_lookup(self):
        self.db._cur.execute('SELECT * FROM LOOKUP')
        rows = self.db._cur.fetchall()
        self.assertEqual(2, len(rows))

    def test_6_listnodes(self):
        node = Node(clear_text=True,
                    **{'username': u"hatman", 'password': u"secret",
                       'url': u"wonderland.com",
                       'notes': u"a really great place",
                       'tags': [u'baz', u'bar']})
        self.db.add_node(node)
        ids = self.db.listnodes()
        self.assertEqual(2, len(ids))

    def test_7_listnodes_w_filter(self):
        ce = CryptoEngine.get()
        tag = ce.encrypt(u'bar')
        rv = self.db.listnodes(tag)
        self.assertEqual(len(rv), 2)
        tag = ce.encrypt(u'baz')
        rv = self.db.listnodes(tag)
        self.assertEqual(len(rv), 1)

    def test_8_getnodes(self):
        nodes = self.db.getnodes([1, 2])
        self.assertEqual(len(nodes), 2)

    def test_9_editnode(self):
        # delibertly insert clear text into the database
        node = {'user': 'transparent', 'password': 'notsecret'}
        self.db.editnode(2, **node)
        self.db._cur.execute('SELECT USER, PASSWORD FROM NODE WHERE ID=2')
        rv = self.db._cur.fetchone()
        self.assertEqual(rv, (u'transparent', u'notsecret'))

    def tearDown(self):
        self.db.close()

if __name__ == '__main__':
    try:
        unittest.main(verbosity=2)
    except SystemExit:
        os.remove('test.db')
