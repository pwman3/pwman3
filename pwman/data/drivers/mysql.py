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
# Copyright (C) 2012-2015 Oz Nahum <nahumoz@gmail.com>
# ============================================================================
#mysql -u root -p
#create database pwmantest
#create user 'pwman'@'localhost' IDENTIFIED BY '123456';
#grant all on pwmantest.* to 'pwman'@'localhost';

"""MySQL Database implementation."""
from __future__ import print_function
from pwman.data.database import Database, __DB_FORMAT__
import MySQLdb as mysql


class MySQLDatabase(Database):

    @classmethod
    def check_db_version(cls, dburi):
        port = 3306
        credentials, host = dburi.netloc.split('@')
        user, passwd = credentials.split(':')
        if ':' in host:
            host, port = host.split(':')
            port = int(port)
        con = mysql.connect(host=host, port=port, user=user, passwd=passwd,
                            db=dburi.path.lstrip('/'))
        cur = con.cursor()
        try:
            cur.execute("SELECT VERSION FROM DBVERSION")
            version = cur.fetchone()
            cur.close()
            con.close()
            return version[-1]
        except mysql.ProgrammingError:
            con.rollback()

    def __init__(self, mysqluri, dbformat=__DB_FORMAT__):
        self.dburi = mysqluri
        self.dbversion = dbformat

    def _open(self):

        port = 3306
        credentials, host = self.dburi.netloc.split('@')
        user, passwd = credentials.split(':')
        if ':' in host:
            host, port = host.split(':')
            port = int(port)

        self._con = mysql.connect(host=host, port=port, user=user,
                                  passwd=passwd,
                                  db=self.dburi.path.lstrip('/'))
        self._cur = self._con.cursor()
        self._create_tables()

    def _create_tables(self):

        try:
            self._cur.execute("SELECT 1 from DBVERSION")
            version = self._cur.fetchone()
            if version:
                return
        except mysql.ProgrammingError:
            self._con.rollback()

        try:
            self._cur.execute("CREATE TABLE NODE(ID SERIAL PRIMARY KEY, "
                              "USERNAME TEXT NOT NULL, "
                              "PASSWORD TEXT NOT NULL, "
                              "URL TEXT NOT NULL, "
                              "NOTES TEXT NOT NULL"
                              ")")

            self._cur.execute("CREATE TABLE TAG"
                              "(ID  SERIAL PRIMARY KEY,"
                              "DATA VARCHAR(255) NOT NULL UNIQUE)")

            self._cur.execute("CREATE TABLE LOOKUP ("
                              "nodeid INTEGER NOT NULL REFERENCES NODE(ID),"
                              "tagid INTEGER NOT NULL REFERENCES TAG(ID)"
                              ")")

            self._cur.execute("CREATE TABLE CRYPTO "
                              "(SEED TEXT, DIGEST TEXT)")

            self._cur.execute("CREATE TABLE DBVERSION("
                              "VERSION TEXT NOT NULL "
                              ")")

            self._cur.execute("INSERT INTO DBVERSION VALUES(%s)",
                              (self.dbversion,))

            self._con.commit()
        except mysql.ProgrammingError:  # pragma: no cover
            self._con.rollback()
