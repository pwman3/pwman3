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

OLD_DB_PATH = os.path(os.path.dirname(__file__), 'pwman.db.v0.0.8')

_db_warn = ("\n*** WARNNING: You are using the old database format"
            " which is insecure."
            " Please upgrade to the new database "
            " format. Do note: support for this DB format will be dropped in"
            " v0.5. This  database format is on hold. No bugs are fixead"
            " Check the help (pwman3 -h) or look at the manpage which"
            " explains how to proceed. ***")

class Ferrum(unittest.TestCase):

    def test_db_warning(self):
        "when trying to run with old db, we should see warning"
        child = pexpect.spawn('../../scripts/pwman3 -t -d '+OLD_DB_PATH)




def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(Ferrum))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())


