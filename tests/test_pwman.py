#!/usr/bin/env python
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
# Copyright (C) 2013-2017 Oz Nahum <nahumoz@gmail.com>
# ============================================================================

import os
import sys
import unittest
from .test_crypto_engine import CryptoEngineTest, TestPassGenerator
from .test_config import TestConfig
from .test_sqlite import TestSQLite
from .test_postgresql import TestPostGresql
from .test_mysql import TestMySQLDatabase
from .test_mongodb import TestMongoDB
from .test_importer import TestImporter
from .test_factory import TestFactory
from .test_base_ui import TestBaseUI
from .test_init import TestInit
from .test_nodes import TestNode


if 'win' not in sys.platform:
    from .test_complete_ui import (Ferrum)

# make sure we use local pwman
sys.path.insert(0, os.getcwd())
# check if old DB exists, if so remove it.
# excuted only once when invoked upon import or
# upon run
# SetupTester().clean()


def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(CryptoEngineTest))
    suite.addTest(loader.loadTestsFromTestCase(TestPassGenerator))
    suite.addTest(loader.loadTestsFromTestCase(TestConfig))
    suite.addTest(loader.loadTestsFromTestCase(TestSQLite))
    suite.addTest(loader.loadTestsFromTestCase(TestPostGresql))
    suite.addTest(loader.loadTestsFromTestCase(TestMySQLDatabase))
    suite.addTest(loader.loadTestsFromTestCase(TestMongoDB))
    suite.addTest(loader.loadTestsFromTestCase(TestImporter))
    suite.addTest(loader.loadTestsFromTestCase(TestFactory))
    suite.addTest(loader.loadTestsFromTestCase(TestBaseUI))
    suite.addTest(loader.loadTestsFromTestCase(TestInit))
    suite.addTest(loader.loadTestsFromTestCase(TestNode))
    if 'win' not in sys.platform:
        suite.addTest(loader.loadTestsFromTestCase(Ferrum))
    return suite

if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True)
