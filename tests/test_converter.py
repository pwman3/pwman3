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
# Copyright (C) 2012-2017 Oz Nahum Tiram <oz.tiram@gmail.com>
# ============================================================================
# pylint: disable=I0011
from __future__ import print_function
import sys
import os
sys.path.insert(0, os.getcwd())
from pwman.data.database import Database, DatabaseException
from pwman.data.drivers.sqlite import SQLiteDatabaseNewForm
from pwman.data.nodes import Node
from pwman.data.nodes import NewNode
from pwman.util.crypto_engine import CryptoEngine
from pwman.data.tags import Tag
from db_tests import node_factory
from pwman.util.callback import CLICallback
import sqlite3 as sqlite
import pwman.util.config as config
from pwman import default_config
import cPickle
from test_tools import SetupTester, DummyCallback4
from pwman.data.convertdb import DBConverter
import copy
import unittest


class SQLiteDatabase(Database):
    """SQLite Database implementation"""

    def __init__(self, fname):
        """Initialise SQLitePwmanDatabase instance."""
        Database.__init__(self)

        try:
            self._filename = fname
        except KeyError as e:
            raise DatabaseException(
                "SQLite: missing parameter [%s]" % (e))

    def _open(self):
        try:
            self._con = sqlite.connect(self._filename)
            self._cur = self._con.cursor()
            self._checktables()
        except sqlite.DatabaseError as e:
            raise DatabaseException("SQLite: %s" % (e))

    def close(self):
        self._cur.close()
        self._con.close()

    def listtags(self, all=False):
        sql = ''
        params = []
        if len(self._filtertags) == 0 or all:
            sql = "SELECT DATA FROM TAGS ORDER BY DATA ASC"
        else:
            sql = ("SELECT TAGS.DATA FROM LOOKUP"
                   + " INNER JOIN TAGS ON LOOKUP.TAG = TAGS.ID"
                   + " WHERE NODE IN (")
            first = True
            for t in self._filtertags:
                if not first:
                    sql += " INTERSECT "
                else:
                    first = False

                sql += (("SELECT NODE FROM LOOKUP OUTER JOIN TAGS ON "
                         "TAG = TAGS.ID "
                         " WHERE TAGS.DATA = ?"))
                params.append(cPickle.dumps(t))
            sql += ") EXCEPT SELECT DATA FROM TAGS WHERE "
            first = True
            for t in self._filtertags:
                if not first:
                    sql += " OR "
                else:
                    first = False
                sql += "TAGS.DATA = ?"
                params.append(cPickle.dumps(t))
        try:
            self._cur.execute(sql, params)

            tags = []
            row = self._cur.fetchone()
            while (row is not None):
                tag = cPickle.loads(str(row[0]))
                tags.append(tag)
                row = self._cur.fetchone()
            return tags
        except sqlite.DatabaseError as e:
            raise DatabaseException("SQLite: %s" % (e))

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
            except sqlite.DatabaseError as e:
                raise DatabaseException("SQLite: %s" % (e))
        return nodes

    def editnode(self, id, node):
        if not isinstance(node, Node):
            raise DatabaseException(
                "Tried to insert foreign object into database [%s]" % node)
        try:
            sql = "UPDATE NODES SET DATA = ? WHERE ID = ?"
            self._cur.execute(sql, [cPickle.dumps(node), id])

        except sqlite.DatabaseError as e:
            raise DatabaseException("SQLite: %s" % (e))
        self._setnodetags(node)
        self._checktags()
        self._commit()

    def addnodes(self, nodes):
        for n in nodes:
            sql = "INSERT INTO NODES(DATA) VALUES(?)"
            if not isinstance(n, Node):
                raise DatabaseException(("Tried to insert foreign object"
                                        "into database [%s]", n))
            value = cPickle.dumps(n)
            try:
                self._cur.execute(sql, [value])
            except sqlite.DatabaseError as e:
                raise DatabaseException("SQLite: %s" % (e))
            id = self._cur.lastrowid
            n.set_id(id)

            self._setnodetags(n)
            self._commit()

    def removenodes(self, nodes):
        for n in nodes:
            if not isinstance(n, Node):
                raise DatabaseException(
                    "Tried to delete foreign object from database [%s]", n)
            try:
                sql = "DELETE FROM NODES WHERE ID = ?"
                self._cur.execute(sql, [n.get_id()])

            except sqlite.DatabaseError as e:
                raise DatabaseException("SQLite: %s" % (e))
            self._deletenodetags(n)

        self._checktags()
        self._commit()

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
                sql += ("SELECT NODE FROM LOOKUP OUTER JOIN "
                        "TAGS ON TAG = TAGS.ID"
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
        except sqlite.DatabaseError as e:
            raise DatabaseException("SQLite: %s" % (e))

    def _commit(self):
        try:
            self._con.commit()
        except sqlite.DatabaseError as e:
            self._con.rollback()
            raise DatabaseException(
                "SQLite: Error commiting data to db [%s]" % (e))

    def _tagids(self, tags):
        ids = []
        for t in tags:
            sql = "SELECT ID FROM TAGS WHERE DATA = ?"
            if not isinstance(t, Tag):
                raise DatabaseException("Tried to insert foreign "
                                        "object into database [%s]", t)
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
            except sqlite.DatabaseError as e:
                raise DatabaseException("SQLite: %s" % (e))
        return ids

    def _deletenodetags(self, node):
        try:
            sql = "DELETE FROM LOOKUP WHERE NODE = ?"
            self._cur.execute(sql, [node.get_id()])

        except sqlite.DatabaseError as e:
            raise DatabaseException("SQLite: %s" % (e))
        self._commit()

    def _setnodetags(self, node):
        self._deletenodetags(node)
        ids = self._tagids(node.get_tags())

        for i in ids:
            sql = "INSERT OR REPLACE INTO LOOKUP VALUES(?, ?)"
            params = [node.get_id(), i]

            try:
                self._cur.execute(sql, params)
            except sqlite.DatabaseError as e:
                raise DatabaseException("SQLite: %s" % (e))
        self._commit()

    def _checktags(self):
        try:
            sql = ("DELETE FROM TAGS WHERE ID NOT "
                   "IN (SELECT TAG FROM LOOKUP GROUP BY TAG)")
            self._cur.execute(sql)
        except sqlite.DatabaseError as e:
            raise DatabaseException("SQLite: %s" % (e))
        self._commit()

    def _checktables(self):
        """ Check if the Pwman tables exist """
        self._cur.execute("PRAGMA TABLE_INFO(NODES)")
        if (self._cur.fetchone() is None):
            # table doesn't exist, create it
            # SQLite does have constraints implemented at the moment
            # so datatype will just be a string
            self._cur.execute("CREATE TABLE NODES"
                              + "(ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                              + "DATA BLOB NOT NULL)")
            self._cur.execute("CREATE TABLE TAGS"
                              + "(ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                              + "DATA BLOB NOT NULL UNIQUE)")
            self._cur.execute("CREATE TABLE LOOKUP"
                              + "(NODE INTEGER NOT NULL, TAG INTEGER NOT NULL,"
                              + " PRIMARY KEY(NODE, TAG))")

            self._cur.execute("CREATE TABLE KEY"
                              + "(THEKEY TEXT NOT NULL DEFAULT '')")
            self._cur.execute("INSERT INTO KEY VALUES('')")

            try:
                self._con.commit()
            except DatabaseException as e:
                self._con.rollback()
                raise e

    def savekey(self, key):
        sql = "UPDATE KEY SET THEKEY = ?"
        values = [key]
        self._cur.execute(sql, values)
        try:
            self._con.commit()
        except sqlite.DatabaseError as e:
            self._con.rollback()
            raise DatabaseException(
                "SQLite: Error saving key [%s]" % (e))

    def loadkey(self):
        self._cur.execute("SELECT THEKEY FROM KEY")
        keyrow = self._cur.fetchone()
        if (keyrow[0] == ''):
            return None
        else:
            return keyrow[0]


class CreateTestDataBases(object):

    def __init__(self):
        config.set_defaults(default_config)
        enc = CryptoEngine.get(dbver=0.4)
        enc.callback = DummyCallback4()
        self.enc1 = copy.copy(enc)
        enc = CryptoEngine.get(dbver=0.5)
        enc.callback = DummyCallback4()
        self.enc2 = copy.copy(enc)

        self.db1 = SQLiteDatabaseNewForm('konverter-v0.4.db', dbformat=0.4)
        self.db2 = SQLiteDatabaseNewForm('konverter-v0.5.db', dbformat=0.5)
        assert self.enc1 is not self.enc2

    def open_dbs(self):
        self.db1._open()
        self.db2._open()
        self.db1.close()
        self.db2.close()

    def add_nodes_to_db1(self):
        username = 'tester'
        password = 'Password'
        url = 'example.org'
        notes = 'some notes'
        node = node_factory(username, password, url, notes,
                            ['testing1', 'testing2'])
        self.db1.addnodes([node])
        idx_created = node._id
        new_node = self.db1.getnodes([idx_created])[0]

        for key, attr in {'password': password, 'username': username,
                          'url': url, 'notes': notes}.iteritems():
                assert attr == getattr(new_node, key)
        self.db1.close()

    def add_nodes_to_db2(self):
        username = 'tester'
        password = 'Password'
        url = 'example.org'
        notes = 'some notes'
        node = node_factory(username, password, url, notes,
                            ['testing1', 'testing2'])
        self.db2.addnodes([node])
        idx_created = node._id
        new_node = self.db2.getnodes([idx_created])[0]

        for key, attr in {'password': password, 'username': username,
                          'url': url, 'notes': notes}.iteritems():
                assert attr == getattr(new_node, key)
        self.db2.close()

    def run(self):
        # before add nodes to db1 we have to create an encryption key!
        # this is handeld by the open method
        self.db1._open()
        enc1 = CryptoEngine.get(dbver=0.4)
        enc1.callback = DummyCallback4()
        key = self.db1.loadkey()
        if key is not None:
            enc1.set_cryptedkey(key)
        else:
            newkey = enc1.changepassword()
            self.db1.savekey(newkey)

        enc1c = copy.copy(enc1)
        if key is not None:
            enc1.set_cryptedkey(key)

        self.add_nodes_to_db1()
        CryptoEngine._instance = None

        self.db2._open()
        enc2 = CryptoEngine.get(dbver=0.5)
        enc2.callback = DummyCallback4()
        key = self.db2.loadkey()
        if key is not None:
            enc2.set_cryptedkey(key)
        else:
            newkey = enc2.changepassword()
            self.db2.savekey(newkey)

        enc2c = copy.copy(enc2)
        if key is not None:
            enc2.set_cryptedkey(key)

        self.add_nodes_to_db2()
        assert enc1 is not enc2
        assert enc1c is not enc2c


class TestConverter(unittest.TestCase):

    pass

if __name__ == '__main__':
    tester = CreateTestDataBases()
    tester.run()
    # afther the test databases are created, invoking
    # pwman3 -d konverter-v0.5.db
    assert "0.4" == DBConverter.detect_db_version('konverter-v0.4.db')
    assert "0.5" == DBConverter.detect_db_version('konverter-v0.5.db')

    # python scripts/pwman3 -d konverter-v0.5.db -e AES,
    # works !
