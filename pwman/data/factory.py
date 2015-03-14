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
# Copyright (C) 2012-2014 Oz Nahum Tiram <nahumoz@gmail.com>
# ============================================================================
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
# ============================================================================

"""
Factory to create Database instances
A Generic interface for all DB engines.
Usage:

import pwman.data.factory as DBFactory

db = DBFactory.create(params)
db.open()
.....
"""
import sys
if sys.version_info.major > 2:  # pragma: no cover
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

import os

from pwman.data.database import DatabaseException, __DB_FORMAT__
from pwman.data.drivers import sqlite
from pwman.data.drivers import postgresql


def check_db_version(dburi):

    ver = str(__DB_FORMAT__)
    dburi = urlparse(dburi)
    dbtype = dburi.scheme
    filename = os.path.abspath(dburi.path)
    if dbtype == "sqlite":
        ver = sqlite.SQLite.check_db_version(filename)
    if dbtype == "postgresql":
        #  ver = postgresql.PostgresqlDatabase.check_db_version(dburi)
        ver = postgresql.PostgresqlDatabase.check_db_version(dburi.geturl())

    return float(ver.strip("\'"))


def createdb(dburi, version):
    dburi = urlparse(dburi)
    dbtype = dburi.scheme
    filename = dburi.path

    if dbtype == "sqlite":
        from pwman.data.drivers import sqlite
        db = sqlite.SQLite(filename, dbformat=version)

    elif dbtype == "postgresql":
        try:
            from pwman.data.drivers import postgresql
            db = postgresql.PostgresqlDatabase(dburi)
        except ImportError:  # pragma: no cover
            raise DatabaseException("python-psycopg2 not installed")
    elif dbtype == "mysql":  # pragma: no cover
        try:
            from pwman.data.drivers import mysql
            db = mysql.MySQLDatabase()
        except ImportError:
            raise DatabaseException("python-mysqldb not installed")
    else:
        raise DatabaseException("Unknown database type specified")
    return db
