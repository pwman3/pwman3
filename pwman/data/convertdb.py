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
# Copyright (C) 2013 Oz Nahum <nahumoz@gmail.com>
# ============================================================================
from __future__ import print_function
import os
import shutil
import time
from pwman.util.crypto_engine import CryptoEngine
import pwman.data.factory
from pwman.util.callback import CLICallback
import sqlite3 as sqlite

_NEWVERSION = 0.4


class DBConverter(object):
    """
    A general class to provide a base template for converting a database
    from one version to another
    """
    def __init__(self, args, config):
        self.dbname = config.get_value('Database', 'filename')
        self.dbtype = config.get_value("Database", "type")
        if not args.output:
            self.newdb_name = self.dbname
        else:
            self.newdb_name = '.new-%s'.join(os.path.splitext(self.dbname))

    @staticmethod
    def detect_db_version(filename):
        """
        This method should accept a pwman db file name, and it should try to
        detect which database version it is.
        """
        con = sqlite.connect(filename)
        cur = con.cursor()
        cur.execute("SELECT DBVERSION FROM DBVERSION")
        row = cur.fetchone()
        if not row:
            return "0.3"
        else:
            return row[0]

    @staticmethod
    def invoke_converter(dbversion, future_version):
        """
        this method should accept the two parameters and according to them
        invoke the right converter
        """
        pass

    def backup_old_db(self):
        print("Will convert the following Database: %s " % self.dbname)
        backup = '.backup-%s'.join(os.path.splitext(self.dbname)) % \
            time.strftime(
                '%Y-%m-%d-%H:%M')
        shutil.copy(self.dbname, backup)
        print("backup created in ", backup)

    def read_old_db(self):
        raise Exception("This methodod should be overriden")

    def create_new_db(self, new_version=_NEWVERSION):
        if os.path.exists(self.newdb_name):
            os.remove(self.newdb_name)

        self.newdb = pwman.data.factory.create(self.dbtype, new_version,
                                               self.newdb_name)
        self.newdb._open()

    def convert_nodes(self):
        raise Exception("This methodod should be overriden")

    def save_new_nodes_to_db(self):
        self.newdb.addnodes(self.NewNodes)
        self.newdb._commit()

    def save_old_key(self):
        raise Exception("This methodod should be overriden")

    def print_success(self):
        print("pwman successfully converted the old database to the new "
              "format.\nPlease run `pwman3 -d %s` to make sure your password "
              "and data are still correct. If you found errors, please "
              "report a bug in Pwman homepage in github. " % self.newdb_name)

    def run(self):
        self.backup_old_db()
        self.read_old_db()
        self.create_new_db()
        self.convert_nodes()
        self.save_new_nodes_to_db()
        self.save_old_key()
        self.print_success()


class PwmanConvertKey(DBConverter):

    def read_old_db(self):
        enc = CryptoEngine.get()
        enc.callback = CLICallback()
        self.db.open()
        self.oldnodes = self.db.listnodes()
        self.oldnodes = self.db.getnodes(self.oldnodes)

    def save_old_key(self):
        CryptoEngine._instance = None
        enc = CryptoEngine.get(0.5)
        self.oldkey = enc.get_cryptedkey()
        self.newdb.savekey(self.oldkey)
