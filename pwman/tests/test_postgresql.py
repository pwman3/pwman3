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
from pwman.data.drivers.sqlite import PostgresqlDatabase
from pwman.data.nodes import Node
from pwman.util.crypto_engine import CryptoEngine
from .test_crypto_engine import give_key, DummyCallback


class TestPostGresql(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.db = SQLite('test.db')
        self.db._open()

    @classmethod
    def tearDownClass(self):
        # TODO: DROP Test DATABASE
        pass
