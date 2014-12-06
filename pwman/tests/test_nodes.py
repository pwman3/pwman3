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
import unittest
from pwman.util.crypto_engine import CryptoEngine
from pwman.data.nodes import Node
from .test_crypto_engine import give_key, DummyCallback


class TestNode(unittest.TestCase):

    def setUp(self):
        self.node = Node(username=u'foo', password=u's3kr3t',
                         url=u'example.com', notes=u'just a reminder to self',
                         tags=[u'baz', u'baz'])

    def test_do_encdict(self):
        ce = CryptoEngine.get()
        for k, v in self.node.to_encdict().items():
            if k == 'user':
                self.assertEqual(ce.decrypt(v).decode(), getattr(self.node,
                                                                 'username'))
            elif k != 'tags':
                self.assertEqual(ce.decrypt(v).decode(), getattr(self.node, k))

    def test_setters(self):
        new_node = {'username': 'baz', 'password': 'n3ws3k43t',
                    'notes': 'i have changed the password',
                    'url': 'newexample.com', 'tags': ['tag1', 'tag2']}

        for k in new_node:
            setattr(self.node, k, new_node[k])

        self.assertEqual(getattr(self.node, 'username'), new_node['username'])
        self.assertEqual(getattr(self.node, 'password'), new_node['password'])
        self.assertEqual(getattr(self.node, 'url'), new_node['url'])
        self.assertEqual(getattr(self.node, 'notes'), new_node['notes'])
        self.assertEqual(getattr(self.node, 'tags'), new_node['tags'])


if __name__ == '__main__':
    ce = CryptoEngine.get()
    ce.callback = DummyCallback()
    ce.changepassword(reader=give_key)
    try:
        unittest.main(verbosity=2, failfast=True)
    except SystemExit:
        pass
