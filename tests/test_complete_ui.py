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
# Copyright (C) 2012-2014 Oz Nahum <nahumoz@gmail.com>
# ============================================================================
# pylint: disable=I0011
from __future__ import print_function
import pexpect
import unittest
import os
import shutil


class Ferrum(unittest.TestCase):
    def clean_files(self):
        lfile = 'convert-test.log'
        with open(lfile) as l:
            lines = l.readlines()
            orig = lines[0].split(':')[-1].strip()
            backup = lines[1].split()[-1].strip()
        shutil.copy(backup, orig)
        # do some cleaning
        os.remove(lfile)
        os.remove('test-chg_passwd.log')
        os.remove(backup)

    def test_b_run_convert(self):
        "invoke pwman with -k option to convert the old data"
        lfile = 'convert-test.log'
        logfile = open(lfile, 'wb')
        cmd = (os.path.join(os.path.dirname(__file__), '../scripts/pwman3'
                            ) + ' -k -e Blowfish -d ')
        child = pexpect.spawn(cmd, logfile=logfile)
        child.expect('[\s|\S]+Please enter your password:', timeout=10)
        self.assertEqual(6, child.sendline('12345'))

        rv = child.expect('pwman successfully converted the old database')
        self.assertEqual(0, rv)
        # if successfully converted, reset the converted database
        # todo - add test to run auto_convert

    def test_c_change_pass(self):
        lfile = 'test-chg_passwd.log'
        logfile = open(lfile, 'wb')
        child = pexpect.spawn(os.path.join(os.path.dirname(__file__),
                                           '../../scripts/pwman3') +
                              ' -d ', logfile=logfile)
        child.sendline('passwd')
        child.expect("Please enter your current password:")
        child.sendline('12345')
        child.sendline('foobar')
        child.sendline('foobar')
        self.clean_files()


def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(Ferrum))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
