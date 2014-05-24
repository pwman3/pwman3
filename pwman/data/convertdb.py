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
# Copyright (C) 2013 Oz Nahum <nahumoz@gmail.com>
#============================================================================
from __future__ import print_function
import os
import shutil
import time
import getpass
from pwman.util.crypto import CryptoEngine
import pwman.data.factory
from pwman.util.callback import Callback
from pwman.data.nodes import NewNode
from pwman.data.tags import Tag
from pwman.data.database import Database, DatabaseException
import sqlite3 as sqlite
import pwman.util.config as config
import cPickle

_NEWVERSION = 0.4


class SQLiteDatabaseReader(Database):
    """SQLite Database implementation"""

    def __init__(self):
        """Initialise SQLitePwmanDatabase instance."""
        Database.__init__(self)

        try:
            self._filename = config.get_value('Database', 'filename')
        except KeyError, e:
            raise DatabaseException(
                "SQLite: missing parameter [%s]" % (e))

    def _open(self):
        try:
            self._con = sqlite.connect(self._filename)
            self._cur = self._con.cursor()
            self._checktables()
        except sqlite.DatabaseError, e:
            raise DatabaseException("SQLite: %s" % (e))

    def close(self):
        self._cur.close()
        self._con.close()

    def getnodes(self, ids):
        nodes = []
        for i in ids:
            sql = "SELECT DATA FROM NODES WHERE ID = ?"
            try:
                self._cur.execute(sql, [i])

                row = self._cur.fetchone()
                if row is not None:
                    node = cPickle.loads(str(row[0]))
                    node.set_id(i)
                    nodes.append(node)
            except sqlite.DatabaseError, e:
                raise DatabaseException("SQLite: %s" % (e))
        return nodes

    def listnodes(self):
        sql = ''
        params = []
        if len(self._filtertags) == 0:
            sql = "SELECT ID FROM NODES ORDER BY ID ASC"
        else:
            first = True
            for t in self._filtertags:
                if not first:
                    sql += " INTERSECT "
                else:
                    first = False
                sql += ("SELECT NODE FROM LOOKUP LEFT JOIN TAGS "
                        " ON TAG = TAGS.ID"
                        " WHERE TAGS.DATA = ? ")

                params.append(cPickle.dumps(t))
        try:
            self._cur.execute(sql, params)

            ids = []
            row = self._cur.fetchone()
            while (row is not None):
                ids.append(row[0])
                row = self._cur.fetchone()
            return ids
        except sqlite.DatabaseError, e:
            raise DatabaseException("SQLite: %s" % (e))

    def _commit(self):
        try:
            self._con.commit()
        except sqlite.DatabaseError, e:
            self._con.rollback()
            raise DatabaseException(
                "SQLite: Error commiting data to db [%s]" % (e))

    def _tagids(self, tags):
        ids = []
        for t in tags:
            sql = "SELECT ID FROM TAGS WHERE DATA = ?"
            if not isinstance(t, Tag):
                raise DatabaseException(
                    "Tried to insert foreign object into database [%s]", t)
            data = cPickle.dumps(t)

            try:
                self._cur.execute(sql, [data])
                row = self._cur.fetchone()
                if (row is not None):
                    ids.append(row[0])
                else:
                    sql = "INSERT INTO TAGS(DATA) VALUES(?)"
                    self._cur.execute(sql, [data])
                    ids.append(self._cur.lastrowid)
            except sqlite.DatabaseError, e:
                raise DatabaseException("SQLite: %s" % (e))
        return ids

    def _checktables(self):
        """ Check if the Pwman tables exist """
        self._cur.execute("PRAGMA TABLE_INFO(NODES)")
        if (self._cur.fetchone() is None):
            # table doesn't exist, create it
            # SQLite does have constraints implemented at the moment
            # so datatype will just be a string
            self._cur.execute("CREATE TABLE NODES "
                              "(ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                              "DATA BLOB NOT NULL)")
            self._cur.execute("CREATE TABLE TAGS "
                              "(ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                              "DATA BLOB NOT NULL UNIQUE)")
            self._cur.execute("CREATE TABLE LOOKUP "
                              "(NODE INTEGER NOT NULL, TAG INTEGER NOT NULL,"
                              " PRIMARY KEY(NODE, TAG))")

            self._cur.execute("CREATE TABLE KEY "
                              + "(THEKEY TEXT NOT NULL DEFAULT '')")
            self._cur.execute("INSERT INTO KEY VALUES('')")
            try:
                self._con.commit()
            except DatabaseException, e:
                self._con.rollback()
                raise e

    def loadkey(self):
        """
        fetch the key to database. the key is also stored
        encrypted.
        """
        self._cur.execute("SELECT THEKEY FROM KEY")
        keyrow = self._cur.fetchone()
        if (keyrow[0] == ''):
            return None
        else:
            return keyrow[0]


class CLICallback(Callback):
    def getinput(self, question):
        return raw_input(question)

    def getsecret(self, question):
        return getpass.getpass(question + ":")

    def getnewsecret(self, question):
        return getpass.getpass(question + ":")


class PwmanConvertDB(object):
    """
    Class to migrate from DB in version 0.3 to
    DB used in later versions.
    """

    def __init__(self, args, config):
        self.dbname = config.get_value('Database', 'filename')
        self.dbtype = config.get_value("Database", "type")
        if not args.output:
            self.newdb_name = self.dbname
        else:
            self.newdb_name = '.new-%s'.join(os.path.splitext(self.dbname))

    def backup_old_db(self):
        print("Will convert the following Database: %s " % self.dbname)
        if os.path.exists(config.get_value("Database", "filename")):
            dbver = pwman.data.factory.check_db_version(self.dbtype)
            self.dbver = float(dbver)
        backup = '.backup-%s'.join(os.path.splitext(self.dbname)) % \
            time.strftime(
                '%Y-%m-%d-%H:%M')
        shutil.copy(self.dbname, backup)
        print("backup created in ", backup)

    def read_old_db(self):
        "read the old db and get all nodes"

        self.db = SQLiteDatabaseReader()
        enc = CryptoEngine.get()
        enc.set_callback(CLICallback())
        self.db.open()
        self.oldnodes = self.db.listnodes()
        self.oldnodes = self.db.getnodes(self.oldnodes)

    def create_new_db(self):
        if os.path.exists(self.newdb_name):
            #print("%s already exists, please move this file!" % dest)
            #sys.exit(2)
            os.remove(self.newdb_name)

        self.newdb = pwman.data.factory.create(self.dbtype, _NEWVERSION,
                                               self.newdb_name)
        self.newdb._open()

    def convert_nodes(self):
        """convert old nodes instances to new format"""
        self.NewNodes = []
        for node in self.oldnodes:
            username = node.get_username()
            password = node.get_password()
            url = node.get_url()
            notes = node.get_notes()
            tags = node.get_tags()
            tags_strings = [tag._name for tag in tags]
            newNode = NewNode()
            newNode.username = username
            newNode.password = password
            newNode.url = url
            newNode.notes = notes
            newNode.tags = tags_strings
            self.NewNodes.append(newNode)

    def save_new_nodes_to_db(self):
        self.newdb.addnodes(self.NewNodes)
        self.newdb._commit()

    def save_old_key(self):
        enc = CryptoEngine.get()
        self.oldkey = enc.get_cryptedkey()
        self.newdb.savekey(self.oldkey)

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
