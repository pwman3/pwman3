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
'''
A module to hold the importer class
'''
import csv


class BaseImporter(object):

    """
    The base class which defines the action needed to import data
    to pwman database
    """

    def __init__(self):
        pass


class CSVImporter(BaseImporter):

    """
    A reference implementation which imports a CSV to the pwman database
    """
    def __init__(self, args, config):
        self.args = args
        self.config = config

    def _read_file(self):
        return []

    def _create_node(self, row):
        pass

    def runner(self):
        for row in self._read_file():
            self._create_node()


class Importer(object):

    """
    The actual job runner which by default runs a csv importer instance.
    This could be changes by calling other instance which for example import
    from KeePass XML or other formats.
    """
    def __init__(self, invoke=CSVImporter):
        self.runner = invoke()

    def run(self):
        self.runner()
