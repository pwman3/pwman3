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
        Args = namedtuple('args', 'import_file')
        self.importer = CSVImporter(Args(import_file='foo'), config)

    def test_fail(self):
        self.assertTrue(True)

if __name__ == '__main__':

    ce = CryptoEngine.get()
    ce.callback = DummyCallback()
    ce.changepassword(reader=give_key)

    try:
        unittest.main(verbosity=2, failfast=True)
    except SystemExit:
        os.remove('import_file.csv')
