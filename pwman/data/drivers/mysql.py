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
# mysql -u root -p
# create database pwmantest
# create user 'pwman'@'localhost' IDENTIFIED BY '123456';
# grant all on pwmantest.* to 'pwman'@'localhost';

"""MySQL Database implementation."""
from pwman.data.database import Database, __DB_FORMAT__

import pymysql as mysql
mysql.install_as_MySQLdb()


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

        return str(__DB_FORMAT__)

    def __init__(self, mysqluri, dbformat=__DB_FORMAT__):
        self.dburi = mysqluri
        self.dbversion = dbformat
        self._sub = "%s"
        self._list_nodes_sql = "SELECT NODEID FROM LOOKUP WHERE TAGID = %s "
        self._add_node_sql = ("INSERT INTO NODE(USERNAME, PASSWORD, URL, "
                              "NOTES) "
                              "VALUES(%s, %s, %s, %s)")
        self._insert_tag_sql = "INSERT INTO TAG(DATA) VALUES(%s)"
        self.ProgrammingError = mysql.ProgrammingError

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
