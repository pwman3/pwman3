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
# Copyright (C) 2014 Oz Nahum Tiram <nahumoz@gmail.com>
#============================================================================

import os
import sys
import unittest
from pwman.util.config import Config, ConfigException, default_config
if sys.version_info.major > 2:
    from configparser import NoSectionError
else:
    from ConfigParser import NoSectionError

# TODO: Drop support for none AES Encryption,
# So the whole section [Encryption] can be dropped.
with open('testfile.conf', 'w') as f:
    f.write("""
[Encryption]
algorithm = Blowfish

[Global]
xsel = /usr/bin/xsel
colors = yes
umask = 0100
cls_timeout = 5

[Database]
type = SQLite
""")


class TestConfig(unittest.TestCase):

    @staticmethod
    def clean_all():
        for item in ('testfile.conf', 'wrong_conf.conf', 'dummy.cfg',
                     'import_file.csv'):
            try:
                os.unlink(item)
            except OSError:
                continue

    def setUp(self):
        self.conf = Config(filename='testfile.conf', defaults=default_config)

    def test_has_defaults(self):
        self.assertTrue(self.conf.parser.has_section('Readline'))

    def test_has_blowfish(self):
        self.assertEqual('Blowfish', self.conf.get_value('Encryption',
                                                         'algorithm'))

    def test_has_user_history(self):
        self.assertEqual(os.path.expanduser('~/.pwman/history'),
                         self.conf.get_value('Readline', 'history'))

    def test_has_user_db(self):
        self.assertEqual(os.path.expanduser('~/.pwman/pwman.db'),
                         self.conf.get_value('Database', 'filename'))

    def test_wrong_config(self):
        with open('wrong_conf.conf', 'w') as f:
            f.write("""
[Encryption
algorithm = Blowfish
""")
        self.assertRaises(ConfigException, Config, 'wrong_conf.conf')

    def test_set_value(self):
        self.conf.set_value('Global', 'colors', 'no')
        self.assertEqual('no', self.conf.get_value('Global', 'colors'))

    def test_set_value_wrong(self):
        self.assertRaises(NoSectionError,
                          self.conf.set_value, *('Error', 'colors', 'no'))

if __name__ == '__main__':
    try:
        unittest.main(verbosity=2)
    except SystemExit:
        TestConfig.clean_all()
