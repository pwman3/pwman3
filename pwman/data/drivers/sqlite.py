# ============================================================================
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
# ============================================================================
# Copyright (C) 2012, 2013, 2014 Oz Nahum Tiram <nahumoz@gmail.com>
# ============================================================================
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
# ============================================================================

"""SQLite Database implementation."""
from __future__ import print_function
from ..database import Database, __DB_FORMAT__
import sqlite3 as sqlite


class SQLite(Database):

    @classmethod
    def check_db_version(cls, fname):
        """
        check the database version.
        """
        try:
            con = sqlite.connect(fname)
        except sqlite.OperationalError as E:
            print("could not open %s" % fname)
            raise E
        cur = con.cursor()
        try:
            cur.execute("SELECT VERSION FROM DBVERSION")
            row = cur.fetchone()
            cur.close()
            con.close()
            return row[-1]
        except sqlite.OperationalError as E:
            if "no such table" in str(E):
                return str(__DB_FORMAT__)

    def __init__(self, filename, dbformat=__DB_FORMAT__):
        """Initialise SQLitePwmanDatabase instance."""
        self._filename = filename
        self.dbversion = dbformat
        ##### WARNING #####
        # The following code changes the column name from USER to USERNAME
        # in NODE table for SQLITE.

        self._add_node_sql = ("INSERT INTO NODE(USERNAME, PASSWORD, URL, NOTES)"
                              "VALUES(?, ?, ?, ?)")
        self._list_nodes_sql = "SELECT NODEID FROM LOOKUP WHERE TAGID = ? "
        self._insert_tag_sql = "INSERT INTO TAG(DATA) VALUES(?)"
        self._get_node_sql = "SELECT * FROM NODE WHERE ID = ?"
        self._sub = '?'
        self._data_wrapper = lambda x: x
        self.integer = "INTEGER"
        self.autoincr = "AUTOINCREMENT"

    def _open(self):
        try:
            self._con = sqlite.connect(self._filename)
        except sqlite.OperationalError as E:
            print("could not open %s" % self._filename)
            raise E

        self._cur = self._con.cursor()
        self._create_tables()
