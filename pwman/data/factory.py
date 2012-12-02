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
# Copyright (C) 2012 Oz Nahum <nahumoz@gmail.com>
#============================================================================
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
#============================================================================

"""
Factory to create Database instances
A Generic interface for all DB engines.
Usage:

import pwman.data.factory as DBFactory

db = DBFactory.create(params)
db.open()
.....
"""
from pwman.data.database import Database, DatabaseException

import pwman.util.config as config

def create(type):
    """
    create(params) -> Database
    Create a Database instance. 
    'type' can only be 'SQLite' at the moment
    """

    if type == "BerkeleyDB":
        pass
#        db = BerkeleyDatabase.BerkeleyDatabase(params)
    elif (type == "SQLite"):
        try: 
            from pwman.data.drivers import sqlite
            db = sqlite.SQLiteDatabase()
        except ImportError, e:
            raise DatabaseException("python-sqlite not installed")
    elif (type == "Postgresql"):
        try:
            from pwman.data.drivers import postgresql
            db = postgresql.PostgresqlDatabase()
        except ImportError, e:
            raise DatabaseException("python-pygresql not installed")
    elif (type == "MySQL"):
        try:
            from pwman.data.drivers import mysql
            db = mysql.MySQLDatabase()
        except ImportError, e:
            raise DatabaseException("python-mysqldb not installed")
    else:
        raise DatabaseException("Unknown database type specified")
    return db
