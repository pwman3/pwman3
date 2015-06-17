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
# Copyright (C) 2015 Oz Nahum <nahumoz@gmail.com>
# ============================================================================
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
# ============================================================================

"""Postgresql Database implementation."""
import psycopg2 as pg
from pwman.data.database import Database, __DB_FORMAT__


class PostgresqlDatabase(Database):

    """
    Postgresql Database implementation

    This assumes that your database admin has created a pwman database
    for you and shared the user name and password with you.

    This driver send no clear text on wire. ONLY excrypted stuff is sent
    between the client and the server.

    Encryption and decryption are happening on your localhost, not on
    the Postgresql server.
    """

    @classmethod
    def check_db_version(cls, dburi):
        """
        Check the database version
        """
        con = pg.connect(dburi)
        cur = con.cursor()
        try:
            cur.execute("SELECT VERSION from DBVERSION")
            version = cur.fetchone()
            cur.close()
            con.close()
            return version[-1]
        except pg.ProgrammingError:
            con.rollback()
            return __DB_FORMAT__

    def __init__(self, pgsqluri, dbformat=__DB_FORMAT__):
        """
        Initialise PostgresqlDatabase instance.
        """
        self._pgsqluri = pgsqluri
        self.dbversion = dbformat
        self._sub = "%s"
        self._list_nodes_sql = "SELECT NODEID FROM LOOKUP WHERE TAGID = %s "
        self._add_node_sql = ('INSERT INTO NODE(USERNAME, PASSWORD, URL, '
                              'NOTES) VALUES(%s, %s, %s, %s) RETURNING ID')
        self._insert_tag_sql = "INSERT INTO TAG(DATA) VALUES(%s) RETURNING ID"
        self.ProgrammingError = pg.ProgrammingError

    def _open(self):

        self._con = pg.connect(self._pgsqluri.geturl())
        self._cur = self._con.cursor()
        self._create_tables()
