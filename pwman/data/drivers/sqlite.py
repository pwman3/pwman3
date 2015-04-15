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
        cur.execute("PRAGMA TABLE_INFO(DBVERSION)")
        row = cur.fetchone()
        try:
            return row[-2]
        except TypeError:
            return str(__DB_FORMAT__)

    def __init__(self, filename, dbformat=__DB_FORMAT__):
        """Initialise SQLitePwmanDatabase instance."""
        self._filename = filename
        self.dbformat = dbformat
        self._add_node_sql = ("INSERT INTO NODE(USER, PASSWORD, URL, NOTES)"
                              "VALUES(?, ?, ?, ?)")
        self._list_nodes_sql = "SELECT NODEID FROM LOOKUP WHERE TAGID = ? "
        self._insert_tag_sql = "INSERT INTO TAG(DATA) VALUES(?)"
        self._sub = '?'

    def _open(self):
        self._con = sqlite.connect(self._filename)
        self._cur = self._con.cursor()
        self._create_tables()

    def _create_tables(self):
        self._cur.execute("PRAGMA TABLE_INFO(NODE)")
        if self._cur.fetchone() is not None:
            return

        self._cur.execute("CREATE TABLE NODE (ID INTEGER PRIMARY KEY "
                          "AUTOINCREMENT, "
                          "USER TEXT NOT NULL, "
                          "PASSWORD TEXT NOT NULL, "
                          "URL TEXT NOT NULL,"
                          "NOTES TEXT NOT NULL)")

        self._cur.execute("CREATE TABLE TAG"
                          "(ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                          "DATA BLOB NOT NULL UNIQUE)")

        self._cur.execute("CREATE TABLE LOOKUP ("
                          "nodeid INTEGER NOT NULL, "
                          "tagid INTEGER NOT NULL, "
                          "FOREIGN KEY(nodeid) REFERENCES NODE(ID),"
                          "FOREIGN KEY(tagid) REFERENCES TAG(ID))")

        self._cur.execute("CREATE TABLE CRYPTO"
                          "(SEED TEXT,"
                          " DIGEST TEXT)")

        # create a table to hold DB version info
        self._cur.execute("CREATE TABLE DBVERSION"
                          "(VERSION TEXT NOT NULL DEFAULT '%s')" %
                          self.dbformat)
        self._cur.execute("INSERT INTO DBVERSION VALUES('%s')" %
                          self.dbformat)
        try:
            self._con.commit()
        except Exception as e:  # pragma: no cover
            self._con.rollback()
            raise e
