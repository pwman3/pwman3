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
from pwman.data.database import Database
import MySQLdb as mysql
import pwman.util.config as config


class MySQLDatabase(Database):

    @classmethod
    def check_db_version(cls, dburi):
        port = 3306
        credentials, host = dburi.netloc.split('@')
        user, passwd = credentials.split(':')
        if ':' in host:
            host, port = host.split(':')
            port = int(port)
        try:
            con = mysql.connect(host=host, port=port, user=user, passwd=passwd,
                                db=dburi.path.lstrip('/'))
            cur = con.cursor()
            cur.execute("SELECT VERSION FROM DBVERSION")
            version = cur.fetchone()
            cur.close()
            con.close()
            return version[-1]
        except mysql.ProgrammingError:
            con.rollback()
