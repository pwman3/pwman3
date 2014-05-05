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
# Copyright (C) 2012-2014 Oz Nahum <nahumoz@gmail.com>
#============================================================================
# pylint: disable=I0011

import pexpect
import unittest
import os
import shutil

OLD_DB_PATH = os.path.join(os.path.dirname(__file__), 'pwman.v0.0.8.db')
NEW_DB_PATH = os.path.join(os.path.dirname(__file__), 'pwman.v0.0.8-newdb.db')

_db_warn = ("pwman3 detected that you are using the old database format")


class Ferrum(unittest.TestCase):

    def test_db_warning(self):
        "when trying to run with old db, we should see warning"
        child = pexpect.spawn(os.path.join(os.path.dirname(__file__),
                                           '../../scripts/pwman3') +
                              ' -d '+OLD_DB_PATH)
        self.assertEqual(0, child.expect(_db_warn, timeout=0.5))

    def test_run_convert(self):
        "invoke pwman with -k option to convert the old data"
        lfile = 'test.log'
        logfile = open(lfile, 'w')
        child = pexpect.spawn(os.path.join(os.path.dirname(__file__),
                                           '../../scripts/pwman3') +
                              ' -k -e Blowfish -d '+OLD_DB_PATH,
                              logfile=logfile)
        child.expect('[\s|\S]+Please enter your password:', timeout=5)
        self.assertEqual(6, child.sendline('12345'))

        rv = child.expect('pwman successfully converted the old database')
        self.assertEqual(0, rv)
        # if successfully converted, reset the converted database
        if not rv:
            with open(lfile) as l:
                lines = l.readlines()
                orig = lines[0].split(':')[-1].strip()
                backup = lines[1].split()[-1].strip()
            shutil.copy(backup, orig)
            # do some cleaning
            os.remove(lfile)
            os.remove(backup)
        # todo - add test to run auto_convert

def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(Ferrum))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
    os.remove(NEW_DB_PATH)


