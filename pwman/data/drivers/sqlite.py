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
#============================================================================
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
#============================================================================

"""SQLite Database implementation."""
from pwman.data.database import Database, DatabaseException
from pwman.data.nodes import Node
from pwman.data.nodes import NewNode
from pwman.data.tags import Tag
import sys
if sys.version_info > (2, 5):
    import sqlite3 as sqlite
else:
    try:
        from pysqlite2 import dbapi2 as sqlite
    except ImportError:
        raise DatabaseException("python-sqlite2 not installed")

import pwman.util.config as config

import cPickle


def check_db_version():
    """
    check the data base version query the right table
    """
    try:
        filename = config.get_value('Database', 'filename')
        con = sqlite.connect(filename)
        cur = con.cursor()
        cur.execute("PRAGMA TABLE_INFO(DBVERSION)")
        row = cur.fetchone()
        if row is None:
            return "0.3"
        try:
            return row[-2]
        except IndexError:
            raise DatabaseException("Something seems fishy with the DB")

    except sqlite.DatabaseError, e:
        raise DatabaseException("SQLite: %s" % (e))


class SQLiteDatabaseNewForm(Database):
    """SQLite Database implementation"""

    def __init__(self, filename=None):
        """Initialise SQLitePwmanDatabase instance."""
        Database.__init__(self)
        if filename:
            self._filename = filename
        else:
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

    def listtags(self, alltags=False):
        sql = ''
        params = []
        if len(self._filtertags) == 0 or alltags:
            sql = "SELECT DATA FROM TAGS ORDER BY DATA ASC"
        else:
            sql = ("SELECT TAGS.DATA FROM LOOKUP"
                   + " INNER JOIN TAGS ON LOOKUP.TAG = TAGS.ID"
                   + " WHERE NODE IN (")
            first = True
            # if using the command filter, the code crashes ...
            #
            for t in self._filtertags:
                if not first:
                    sql += " INTERSECT "
                else:
                    first = False

                sql += ("SELECT NODE FROM LOOKUP LEFT JOIN TAGS ON TAG = "
                        + " TAGS.ID WHERE TAGS.DATA = ?")
                params.append(t._name)
            sql += ") EXCEPT SELECT DATA FROM TAGS WHERE "
            first = True
            for t in self._filtertags:
                if not first:
                    sql += " OR "
                else:
                    first = False
                sql += "TAGS.DATA = ?"
                params.append(t._name)
        try:
            self._cur.execute(sql, params)
            tags = []
            row = self._cur.fetchone()
            while row is not None:
                tagstring = str(row[0])
                tags.append(tagstring)
                row = self._cur.fetchone()
            return tags
        except sqlite.DatabaseError, e:
            raise DatabaseException("SQLite: %s" % (e))
        except sqlite.InterfaceError, e:
            import ipdb
            ipdb.set_trace()  # XXX BREAKPOINT

    def parse_node_string(self, string):
        nodestring = string.split("##")
        keyvals = {}
        for pair in nodestring[:-1]:
            key, val = pair.split(":")
            keyvals[key.lstrip('##')] = val
        tags = nodestring[-1]
        tags = tags.split("tags:", 1)[1]
        tags = tags.split("tag:")
        tags = [tag.split('**endtag**')[0] for tag in tags]
        return keyvals, tags

    def getnodes(self, ids):
        """
        object should always be: (ipwman.data.nodes
        """
        nodes = []
        for i in ids:
                sql = "SELECT DATA FROM NODES WHERE ID = ?"
                self._cur.execute(sql, [i])
                row = self._cur.fetchone()
                if row is not None:
                    nodestring = str(row[0])
                    nodeargs, tags = self.parse_node_string(nodestring)
                    node = NewNode(**nodeargs)
                    node.tags = tags
                    node.set_id(i)
                    nodes.append(node)
        return nodes

    def editnode(self, id, node):
        try:
            sql = "UPDATE NODES SET DATA = ? WHERE ID = ?"
            #sql = "INSERT OR UPDATE NODES SET DATA = ? WHERE ID = ?"
            self._cur.execute(sql, [node.dump_edit_to_db()[0], id])
        except sqlite.DatabaseError, e:
            raise DatabaseException("SQLite: %s" % (e))
        self._setnodetags(node)
        self._checktags()
        self._commit()

    def addnodes(self, nodes):
        """
        This method injects the data as PWMAN object using cPickle.
        To make pwman more secure, either this method has to replaced.
        Or whenever stuff is read from the database, there must be a
        security check that it contains the correct objects!
        Nodes passed to this methos are instances!
        """
        for n in nodes:
            sql = "INSERT INTO NODES(DATA) VALUES(?)"
            # if not isinstance(n, Node): raise DatabaseException(
            #    "Tried to insert foreign object into database [%s]", n)
            value = n.dump_to_db()
            try:
                self._cur.execute(sql, value)
            except sqlite.DatabaseError, e:
                raise DatabaseException("SQLite: %s" % (e))
            idx = self._cur.lastrowid
            n._id = idx
            self._setnodetags(n)
            self._commit()

    def removenodes(self, nodes):
        for n in nodes:
            # if not isinstance(n, Node): raise DatabaseException(
            #    "Tried to delete foreign object from database [%s]", n)
            try:
                sql = "DELETE FROM NODES WHERE ID = ?"
                self._cur.execute(sql, [n._id])

            except sqlite.DatabaseError, e:
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
                sql += ("SELECT NODE FROM LOOKUP LEFT JOIN TAGS ON TAG = "
                        " TAGS.ID WHERE TAGS.DATA = ? ")
                params.append(t._name)
        try:
            self._cur.execute(sql, params)
            ids = []
            row = self._cur.fetchone()
            while row is not None:
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
        for tag in tags:
            sql = "SELECT ID FROM TAGS WHERE DATA = ?"
            try:
                if isinstance(tag, str):
                    self._cur.execute(sql, [tag])
                else:
                    self._cur.execute(sql, [tag._name])
                row = self._cur.fetchone()
                if (row is not None):
                    ids.append(row[0])
                else:
                    sql = "INSERT INTO TAGS(DATA) VALUES(?)"
                    if isinstance(tag, str):
                        self._cur.execute(sql, [tag])
                    else:
                        self._cur.execute(sql, [tag._name])

                    ids.append(self._cur.lastrowid)
            except sqlite.DatabaseError, e:
                raise DatabaseException("SQLite: %s" % (e))
        return ids

    def _deletenodetags(self, node):
        try:
            sql = "DELETE FROM LOOKUP WHERE NODE = ?"
            self._cur.execute(sql, [node._id])
        except sqlite.DatabaseError, e:
            raise DatabaseException("SQLite: %s" % (e))
        self._commit()

    def _setnodetags(self, node):
        self._deletenodetags(node)
        ids = self._tagids(node.tags)
        for i in ids:
            sql = "INSERT OR REPLACE INTO LOOKUP VALUES(?, ?)"
            params = [node._id, i]

            try:
                self._cur.execute(sql, params)
            except sqlite.DatabaseError, e:
                raise DatabaseException("SQLite: %s" % (e))
        self._commit()

    def _checktags(self):
        try:
            sql = "DELETE FROM TAGS WHERE ID NOT IN (SELECT TAG FROM" \
                + " LOOKUP GROUP BY TAG)"
            self._cur.execute(sql)
        except sqlite.DatabaseError, e:
            raise DatabaseException("SQLite: %s" % (e))
        self._commit()

    def _checktables(self):
        """
        Check if the Pwman tables exist.
        TODO: This method should check the version of the
        database. If it finds an old format it should
        exis, and prompt the user to convert the database
        to the new version with a designated script.
        """
        self._cur.execute("PRAGMA TABLE_INFO(NODES)")
        if (self._cur.fetchone() is None):
            # table doesn't exist, create it
            # SQLite does have constraints implemented at the moment
            # so datatype will just be a string
            self._cur.execute("CREATE TABLE NODES (ID INTEGER PRIMARY KEY"
                              + " AUTOINCREMENT,DATA BLOB NOT NULL)")
            self._cur.execute("CREATE TABLE TAGS"
                              + "(ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                              + "DATA BLOB NOT NULL UNIQUE)")
            self._cur.execute("CREATE TABLE LOOKUP"
                              + "(NODE INTEGER NOT NULL, TAG INTEGER NOT NULL,"
                              + " PRIMARY KEY(NODE, TAG))")

            self._cur.execute("CREATE TABLE KEY"
                              + "(THEKEY TEXT NOT NULL DEFAULT '')")
            self._cur.execute("INSERT INTO KEY VALUES('')")
            # create a table to hold DB version info
            self._cur.execute("CREATE TABLE DBVERSION"
                              + "(DBVERSION TEXT NOT NULL DEFAULT '0.4')")
            self._cur.execute("INSERT INTO DBVERSION VALUES('0.4')")
            try:
                self._con.commit()
            except DatabaseException, e:
                self._con.rollback()
                raise e

    def savekey(self, key):
        """
        This function is saving the key to table KEY.
        The key already arrives as an encrypted string.
        It is the same self._keycrypted from
        crypto py (check with id(self._keycrypted) and
        id(key) here.
        """
        sql = "UPDATE KEY SET THEKEY = ?"
        values = [key]
        self._cur.execute(sql, values)
        try:
            self._con.commit()
        except sqlite.DatabaseError, e:
            self._con.rollback()
            raise DatabaseException(
                "SQLite: Error saving key [%s]" % (e))

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


class SQLiteDatabase(Database):
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

    def listtags(self, alltags=False):
        sql = ''
        params = []
        if len(self._filtertags) == 0 or alltags:
            sql = "SELECT DATA FROM TAGS ORDER BY DATA ASC"
        else:
            sql = ("SELECT TAGS.DATA FROM LOOKUP"
                   + " INNER JOIN TAGS ON LOOKUP.TAG = TAGS.ID"
                   + " WHERE NODE IN (")
            first = True
            # if using the command filter, the code crashes ...
            #
            for t in self._filtertags:
                if not first:
                    sql += " INTERSECT "
                else:
                    first = False

                sql += ("SELECT NODE FROM LOOKUP LEFT JOIN TAGS ON TAG " +
                        + " = TAGS.ID "
                        + " WHERE TAGS.DATA = ?")
                params.append(cPickle.dumps(t))
            sql += ") EXCEPT SELECT DATA FROM TAGS WHERE "
            first = True
            for t in self._filtertags:
                if not first:
                    sql += " OR "
                else:
                    first = False
                sql += "TAGS.DATA = ?"
                params.append(t)
        try:
            print params
            self._cur.execute(sql, params)
            tags = []
            row = self._cur.fetchone()
            while (row is not None):
                tag = cPickle.loads(str(row[0]))
                tags.append(tag)
                row = self._cur.fetchone()
            return tags
        except sqlite.DatabaseError, e:
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
            except sqlite.DatabaseError, e:
                raise DatabaseException("SQLite: %s" % (e))
        return nodes

    def editnode(self, id, node):
        if not isinstance(node, Node):
            raise DatabaseException(
                "Tried to insert foreign object into database [%s]" % node)
        try:
            sql = "UPDATE NODES SET DATA = ? WHERE ID = ?"
            self._cur.execute(sql, [cPickle.dumps(node), id])

        except sqlite.DatabaseError, e:
            raise DatabaseException("SQLite: %s" % (e))
        self._setnodetags(node)
        self._checktags()
        self._commit()

    def addnodes(self, nodes):
        for n in nodes:
            sql = "INSERT INTO NODES(DATA) VALUES(?)"
            if not isinstance(n, Node):
                raise DatabaseException(
                    "Tried to insert foreign object into database [%s]", n)
            value = cPickle.dumps(n)
            try:
                self._cur.execute(sql, [value])
            except sqlite.DatabaseError, e:
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

            except sqlite.DatabaseError, e:
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
                sql += ("SELECT NODE FROM LOOKUP LEFT JOIN TAGS "
                        + " ON TAG = TAGS.ID"
                        + " WHERE TAGS.DATA = ? ")

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

    def _deletenodetags(self, node):
        try:
            sql = "DELETE FROM LOOKUP WHERE NODE = ?"
            self._cur.execute(sql, [node.get_id()])

        except sqlite.DatabaseError, e:
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
            except sqlite.DatabaseError, e:
                raise DatabaseException("SQLite: %s" % (e))
        self._commit()

    def _checktags(self):
        try:
            sql = "DELETE FROM TAGS WHERE ID NOT IN (SELECT TAG FROM " \
                  + "LOOKUP GROUP BY TAG)"
            self._cur.execute(sql)
        except sqlite.DatabaseError, e:
            raise DatabaseException("SQLite: %s" % (e))
        self._commit()

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

    def savekey(self, key):
        """
        This function is saving the key to table KEY.
        The key already arrives as an encrypted string.
        It is the same self._keycrypted from
        crypto py (check with id(self._keycrypted) and
        id(key) here.
        """
        sql = "UPDATE KEY SET THEKEY = ?"
        values = [key]
        self._cur.execute(sql, values)
        try:
            self._con.commit()
        except sqlite.DatabaseError, e:
            self._con.rollback()
            raise DatabaseException(
                "SQLite: Error saving key [%s]" % (e))

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
