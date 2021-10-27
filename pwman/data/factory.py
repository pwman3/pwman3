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
# Copyright (C) 2012-2016 Oz Nahum Tiram <oz.tiram@gmail.com>
# ============================================================================

import sys
from urllib.parse import urlparse

import os

from pwman.data.database import DatabaseException, __DB_FORMAT__
from pwman.data import drivers


def parse_sqlite_uri(dburi):
    """return dburi.netloc if on windows, because this was someone break"""
    if not dburi.path:
        return dburi.netloc
    filename = os.path.abspath(dburi.path)
    return filename


def parse_postgres_uri(dburi):
    return dburi.geturl()


def no_parse_uri(dburi):
    return dburi


class_db_map = {'sqlite':
                ['SQLite', parse_sqlite_uri],
                'postgresql': ['PostgresqlDatabase', parse_postgres_uri,
                               'python-psycopg2'],
                'mysql': ['MySQLDatabase', no_parse_uri, 'pymysql'],
                'mongodb': ['MongoDB', no_parse_uri, 'pymongo']
                }
create_db_map = {'sqlite':
                 ['SQLite', parse_sqlite_uri],
                 'postgresql': ['PostgresqlDatabase', no_parse_uri,
                                'python-psycopg2'],
                 'mysql': ['MySQLDatabase', no_parse_uri, 'pymysql'],
                 'mongodb': ['MongoDB', no_parse_uri, 'pymongo']
                 }


def check_db_version(dburi):

    dburi = urlparse(dburi)
    dbtype = dburi.scheme

    if not dbtype:
        print("Your URI seems incorrect ...")
        sys.exit(1)

    try:
        cls = getattr(drivers, class_db_map[dbtype][0])
        ver = cls.check_db_version(class_db_map[dbtype][1](dburi))
        return ver
    except AttributeError:
        raise DatabaseException(
            '%s not installed? ' % class_db_map[dbtype][-1])


def migratedb(dbinst):
    from pwman.data.migration import migrations

    for migration in migrations[str(__DB_FORMAT__)]:
        m = migration(dbinst)
        m.apply()


def createdb(dburi, version):

    dburi = urlparse(dburi)
    dbtype = dburi.scheme
    try:
        cls = getattr(drivers, create_db_map[dbtype][0])
        dbinst = cls(create_db_map[dbtype][1](dburi))
    except AttributeError:
        raise DatabaseException(
            '%s not installed? ' % class_db_map[dbtype][-1])
    except KeyError:
        raise DatabaseException('Unknown database [%s] given ...' % (dbtype))

    if version != str(__DB_FORMAT__):
        migratedb(dbinst)

    return dbinst
