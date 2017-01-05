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
import os
import os.path
import unittest
import sys

from collections import namedtuple

from pwman import set_xsel
from pwman.data import factory
from pwman.data.database import __DB_FORMAT__
from pwman import (get_conf, get_conf_options, get_db_version)
from .test_tools import SetupTester

dummyfile = """
[Encryption]

[Readline]

[Global]
xsel = /usr/bin/xsel
colors = yes
cls_timeout = 5

[Database]
"""

db =  ".".join(("pwman","test", sys.version.split(" " ,1)[0], "db"))
testdb = os.path.abspath(os.path.join(os.path.dirname(__file__), db))


class TestFactory(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        SetupTester().clean()


class TestInit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('dummy.cfg', 'w') as d:
            d.write(dummyfile)

    @classmethod
    def tearDownClass(cls):
        for item in ('dummy.cfg', testdb):
            try:
                os.unlink(item)
            except (OSError, PermissionError):
                continue

    def setUp(self):
        "test that the right db instance was created"
        self.dbtype = 'sqlite'
        self.db = factory.createdb('sqlite://' + os.path.abspath(testdb),
                                   __DB_FORMAT__)
        self.tester = SetupTester(__DB_FORMAT__, dburi=testdb)
        self.tester.create()

    def tearDown(self):
        del(self.tester)
        try:
            os.unlink(self.db._filename)
        except PermissionError:
            pass

    def test_get_db_version(self):
        v = get_db_version(self.tester.configp, 'sqlite')
        self.assertEqual(v, u"'0.6'")
        v = get_db_version(self.tester.configp, 'sqlite')
        self.assertEqual(v, u"'0.6'")

    def test_set_xsel(self):
        Args = namedtuple('args', 'cfile, dbase, algo')
        args = Args(cfile='dummy.cfg', dbase='dummy.db', algo='AES')
        xsel, dbtype, configp = get_conf_options(args, 'True')
        set_xsel(configp, False)
        set_xsel(configp, True)

    def test_get_conf_file(self):
        Args = namedtuple('args', 'cfile')
        args = Args(cfile='dummy.cfg')
        get_conf(args)

    def test_get_conf_options(self):
        Args = namedtuple('args', 'cfile, dbase, algo')
        args = Args(cfile='dummy.cfg', dbase='dummy.db', algo='AES')
        xsel, dburi, configp = get_conf_options(args, 'True')
        self.assertEqual(dburi, 'dummy.db')


if __name__ == '__main__':

    try:
        unittest.main(verbosity=2, failfast=True)
    except SystemExit:
        if os.path.exists(testdb):
            os.remove(testdb)
