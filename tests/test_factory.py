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
# Copyright (C) 2013-2017 Oz Nahum Tiram <nahumoz@gmail.com>
# ============================================================================

import os
import os.path
import unittest
import sys

from pwman.data import factory
from pwman.data.database import DatabaseException
from pwman.data.drivers.sqlite import SQLite
from pwman.data.database import __DB_FORMAT__
from .test_tools import (SetupTester)
try:
    from pwman.data.drivers.postgresql import PostgresqlDatabase
    has_psycopg = True
except ImportError:
    has_psycopg = False
db = ".".join(("pwman", "test", sys.version.split(" ", 1)[0], "db"))
testdb = os.path.abspath(os.path.join(os.path.dirname(__file__), db))

_saveconfig = False


class TestFactory(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        SetupTester().clean()

    def setUp(self):
        "test that the right db instance was created"
        self.dbtype = 'sqlite'
        self.db = factory.createdb('sqlite:///'+testdb, __DB_FORMAT__)
        self.tester = SetupTester(__DB_FORMAT__, testdb)
        self.tester.create()

    def test_factory_check_db_ver(self):
        self.assertEqual(
            factory.check_db_version('sqlite://'+testdb), "0.7")

    @unittest.skip("not supported at the moment")
    def test_factory_check_db_file(self):
        fn = os.path.join(os.path.dirname(__file__), 'baz.db')
        db = factory.createdb('sqlite:///'+os.path.abspath(fn), 0.3)
        db._open()
        self.assertEqual(factory.check_db_version('sqlite:///'+fn), 0.3)
        os.unlink(fn)

    def test_factory_create(self):
        fn = os.path.join(os.path.dirname(__file__), 'foo.db')
        db = factory.createdb('sqlite://'+os.path.abspath(fn), 0.7)
        db._open()
        self.assertTrue(os.path.exists(fn))
        db.close()
        os.unlink(fn)
        self.assertIsInstance(db, SQLite)
        self.assertRaises(DatabaseException, factory.createdb,
                          *('UNKNOWN', __DB_FORMAT__))

    def test_factory_createdb(self):
        db = factory.createdb("sqlite:///test.db", 0.7)
        self.assertIsInstance(db, SQLite)
        del db
        db = factory.createdb("sqlite:///test.db", 0.7)
        self.assertIsInstance(db, SQLite)
        del db

    @unittest.skipUnless(has_psycopg, "requires psycopg")
    def test_factory_createdb_postgresql(self):
        db = factory.createdb("postgresql:///pwman", 0.7)
        self.assertIsInstance(db, PostgresqlDatabase)
        del db
        db = factory.createdb("postgresql:///pwman", 0.7)
        self.assertIsInstance(db, PostgresqlDatabase)
        del db


class TestSQLiteMigration(unittest.TestCase):
    @classmethod
    def setUp(cls):
        "test that the right db instance was created"
        cls.dbtype = 'sqlite'
        cls.db = factory.createdb('sqlite:///'+testdb, __DB_FORMAT__)
        cls.db._open()
        cls.db.execute("")
        cls.db.execute("ALTER TABLE NODE DROP COLUMN MDATE")
        cls.db.execute("UPDATE DBVERSION SET VERSION = '0.6'")

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        for item in ('test.db',):
            try:
                os.remove(item)
            except OSError:
                continue

    def test_database_is_migrated(self):
        factory.migratedb(self.db)
        self.assertEqual("0.7", factory.check_db_version(f"sqlite:///{self.db.dburi}"))


if __name__ == '__main__':
    # make sure we use local pwman
    sys.path.insert(0, os.getcwd())
    # check if old DB exists, if so remove it.
    # excuted only once when invoked upon import or
    # upon run
    SetupTester().clean()
    unittest.main(verbosity=1, failfast=True)
