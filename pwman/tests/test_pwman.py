#!/usr/bin/env python
#============================================================================
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
#============================================================================
# Copyright (C) 2013 Oz Nahum <nahumoz@gmail.com>
#============================================================================

import os
import sys
import unittest
from db_tests import (DBTests, SetupTester, CLITests, ConfigTest,
                      TestDBFalseConfig, FactoryTest)

from crypto_tests import CryptoTest
from test_complete_ui import Ferrum, NEW_DB_PATH

if os.path.exists(NEW_DB_PATH):
    os.remove(NEW_DB_PATH)

# make sure we use local pwman
sys.path.insert(0, os.getcwd())
# check if old DB exists, if so remove it.
# excuted only once when invoked upon import or
# upon run
SetupTester().clean()


class Dumb(unittest.TestCase):
    def test_stupid(self):
        self.assertTrue(True)


def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    #suite.addTest(loader.loadTestsFromTestCase(DBTests))
    #suite.addTest(loader.loadTestsFromTestCase(CryptoTest))
    #suite.addTest(loader.loadTestsFromTestCase(CLITests))
    #suite.addTest(loader.loadTestsFromTestCase(ConfigTest))
    #suite.addTest(loader.loadTestsFromTestCase(FactoryTest))
    #suite.addTest(loader.loadTestsFromTestCase(TestDBFalseConfig))
    suite.addTest(loader.loadTestsFromTestCase(Dumb))
    #suite.addTest(loader.loadTestsFromTestCase(Ferrum))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
