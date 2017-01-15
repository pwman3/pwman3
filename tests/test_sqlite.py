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
# Copyright (C) 2012-2017 Oz Nahum Tiram <nahumoz@gmail.com>
# ============================================================================
import os
import unittest
from pwman.data.drivers.sqlite import SQLite
from pwman.data.nodes import Node
from pwman.util.crypto_engine import CryptoEngine
from .test_crypto_engine import give_key, DummyCallback


class TestSQLite(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        for item in ('test.db',):
            try:
                os.remove(item)
            except OSError:
                continue

    @classmethod
    def setUp(cls):
        cls.db = SQLite('test.db')
        cls.db._open()

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
                    **{'username': "alice", 'password': "secret",
                       'url': "wonderland.com",
                       'notes': "a really great place",
                       'tags': ['foo', 'bar']})
        self.db.add_node(node)
        rv = self.db._cur.execute("select * from node")
        ce = CryptoEngine.get()
        res = rv.fetchone()
        self.assertEqual(ce.decrypt(res[1]), b"alice")

    def test_4_test_tags(self):
        node = Node(clear_text=True,
                    **{'username': u"alice", 'password': u"secret",
                       'url': u"wonderland.com",
                       'notes': u"a really great place",
                       'tags': ['foo', 'bar']})
        ce = CryptoEngine.get()
        self.db._get_or_create_tag(node._tags[0])
        self.assertEqual(1, self.db._get_or_create_tag(node._tags[0]))
        rv = self.db._get_or_create_tag(ce.encrypt(b'baz'))
        self.assertEqual(3, rv)
        self.db._con.commit()

    def test_5_test_lookup(self):
        self.db._cur.execute('SELECT nodeid, tagid FROM LOOKUP')
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
        # the tag 'bar' is found in a node created in:
        # test_3_add_node
        # test_6_listnodes

        tag = ce.encrypt(b'bar')
        rv = self.db.listnodes(tag)
        self.assertEqual(len(rv), 2)
        tag = ce.encrypt(b'baz')
        # the tag 'baz' is found in a node created in
        # test_6_listnodes
        rv = self.db.listnodes(tag)
        self.assertEqual(len(rv), 1)

    def test_8_getnodes(self):
        nodes = self.db.getnodes([1, 2])
        self.assertEqual(len(nodes), 2)

    def test_9_editnode(self):
        # delibertly insert clear text into the database
        ce = CryptoEngine.get()
        tags = [ce.encrypt("foo"), ce.encrypt("auto")]
        node = {'user': 'transparent', 'password': 'notsecret',
                'tags': tags}
        self.db.editnode('2', **node)
        self.db._cur.execute('SELECT USER, PASSWORD FROM NODE WHERE ID=2')
        rv = self.db._cur.fetchone()
        self.assertEqual(rv, ('transparent', 'notsecret'))
        node = {'user': 'modify', 'password': 'notsecret',
                'tags': tags}
        # now the tags bank and baz are orphan ...
        # what happens? it should be completely removed.
        # To spare IO we only delete orphand tags when
        # db.close is called.
        self.db.editnode('2', **node)

    def test_9_test_no_orphans(self):
        self.db._clean_orphans()
        self.db._con.commit()
        ce = CryptoEngine.get()
        tags = None
        while not tags:
            tags = self.db._cur.execute('SELECT * FROM tag').fetchall()
        tags_clear = [ce.decrypt(tag[1]) for tag in tags]
        self.assertNotIn(b"baz", tags_clear)

    def test_a10_test_listtags(self):
        """there should be only 3 tags left"""
        tags = self.db.listtags()
        self.assertEqual(3, len(list(tags)))

    def test_a11_test_rmnodes(self):
        for n in [1, 2]:
            self.db.removenodes([n])
        rv = self.db._cur.execute("select * from node").fetchall()
        self.assertListEqual(rv, [])

    def test_a12_test_savekey(self):
        ce = CryptoEngine.get()
        self.db.savekey(ce.get_cryptedkey())
        self.assertEqual(ce.get_cryptedkey(), self.db.loadkey())


if __name__ == '__main__':

    ce = CryptoEngine.get()
    ce.callback = DummyCallback()
    ce.changepassword(reader=give_key)
    unittest.main(verbosity=2, failfast=True)
