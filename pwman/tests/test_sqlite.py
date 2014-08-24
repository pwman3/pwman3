#============================================================================
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
#============================================================================
# Copyright (C) 2012 Oz Nahum Tiram <nahumoz@gmail.com>
#============================================================================
import os
import unittest
from pwman.data.drivers.sqlite import SQLite


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.db = SQLite('test.db')

    def test_create_tables(self):
        # the method _open calls _create_tables
        self.db._open()


if __name__ == '__main__':
    try:
        unittest.main(verbosity=2)
    except SystemExit:
        os.remove('test.db')
