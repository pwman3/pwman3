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
# Copyright (C) 2014-2017 Oz Nahum Tiram <oz.tiram@gmail.com>
# ============================================================================
import unittest
from pwman.util.crypto_engine import CryptoEngine
from pwman.data.nodes import Node
from .test_crypto_engine import give_key, DummyCallback


class TestNode(unittest.TestCase):

    def setUp(self):
        self.node = Node(username=b'foo', password=b's3kr3t',
                         url=b'example.com', notes=b'just a reminder to self',
                         tags=[b'baz', b'baz'])

    def test_do_encdict(self):

        ce = CryptoEngine.get()

        for k, v in self.node.to_encdict().items():
            if k == 'user':
                username = getattr(self.node, 'username')
                value = ce.decrypt(v).decode()
                self.assertEqual(value, username)

            elif k not in ['tags', 'mdate']:
                value = getattr(self.node, k)
                if value:
                    self.assertEqual(ce.decrypt(v).decode(), value)
                else:
                    print(f"Value of {k} is {value}")

    def test_setters(self):
        new_node = {'username': b'baz', 'password': b'n3ws3k43t',
                    'notes': b'i have changed the password',
                    'url': b'newexample.com', 'tags': [b'tag1', b'tag2']}

        for k in new_node:
            setattr(self.node, k, new_node[k])

        for attribute in ['username', 'password', 'url', 'notes']:
            self.assertEqual(bytearray(getattr(self.node, attribute), 'utf-8'), new_node[attribute])

        self.assertEqual(bytearray(getattr(self.node, 'username'), 'utf-8'), new_node['username'])
        self.assertEqual(bytearray(getattr(self.node, 'password'), 'utf-8'), new_node['password'])
        self.assertEqual(getattr(self.node, 'tags'), new_node['tags'])


if __name__ == '__main__':
    import os
    ce = CryptoEngine.get()
    ce.callback = DummyCallback()
    ce.changepassword(reader=give_key)
    try:
        unittest.main(verbosity=2, failfast=int(os.getenv('PWMAN_FAILFAST', "1")))
    except SystemExit:
        pass
