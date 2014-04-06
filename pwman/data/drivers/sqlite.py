#============================================================================
# This file is part of Pwman3.
#
# Pwman3 is free software; you can redistribute iut and/or modify
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
from pwman.data.nodes import NewNode
from pwman.util.crypto import CryptoEngine
import sqlite3 as sqlite
import pwman.util.config as config
import itertools

def check_db_version():
    """
    check the data base version query the right table
    """
    filename = config.get_value('Database', 'filename')
    con = sqlite.connect(filename)
    cur = con.cursor()
    cur.execute("PRAGMA TABLE_INFO(DBVERSION)")
    row = cur.fetchone()
    if row is None:
        return "0.3"  # pragma: no cover
    try:
        return row[-2]
    except IndexError:  # pragma: no cover
        raise DatabaseException("Something seems fishy with the DB")


class SQLiteDatabaseNewForm(Database):
    """SQLite Database implementation"""

    def __init__(self, filename=None):
        """Initialise SQLitePwmanDatabase instance."""
        Database.__init__(self)
        # error handling is implemented in config.get_value
        # so there's no need to try... except here...
        if not filename:
            self._filename = config.get_value('Database', 'filename')
        else:
            self._filename = filename

        if not self._filename:
            raise DatabaseException(("SQLite: missing config parameter:"
                                    " filename"))

    def _open(self):
        try:
            self._con = sqlite.connect(self._filename)
            self._cur = self._con.cursor()
            self._checktables()
        except sqlite.DatabaseError, e:  # pragma: no cover
            raise DatabaseException("SQLite: %s" % (e))

    def close(self):
        self._cur.close()
        self._con.close()

    def listtags(self, alltags=False):
        sql = ''
        params = []
        if not self._filtertags or alltags:
            sql = "SELECT DATA FROM TAGS ORDER BY DATA ASC"
        else:
            sql = ("SELECT TAGS.DATA FROM LOOKUP"
                   " INNER JOIN TAGS ON LOOKUP.TAG = TAGS.ID"
                   " WHERE NODE IN (")
            first = True
            for t in self._filtertags:
                if not first:
                    sql += " INTERSECT "  # pragma: no cover
                else:
                    first = False

                sql += ("SELECT NODE FROM LOOKUP LEFT JOIN TAGS ON TAG = "
                        " TAGS.ID WHERE TAGS.DATA LIKE ?")
                params.append(t._name+'%')
            sql += ") EXCEPT SELECT DATA FROM TAGS WHERE "
            first = True
            for t in self._filtertags:
                if not first:
                    sql += " OR "  # pragma: no cover
                else:
                    first = False
                sql += "TAGS.DATA = ?"
                params.append(t.name)

        try:
            self._cur.execute(sql, params)
            tags = [str(t[0]) for t in self._cur.fetchall()]
            return tags

        except sqlite.DatabaseError, e:  # pragma: no cover
            raise DatabaseException("SQLite: %s" % (e))
        except sqlite.InterfaceError, e:  # pragma: no cover
            raise e

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
                    args, tags = self.parse_node_string(nodestring)
                    node = NewNode()
                    node._password = args['password']
                    node._username = args['username']
                    node._url = args['url']
                    node._notes = args['notes']
                    node.tags = tags
                    node._id = i
                    nodes.append(node)
        return nodes

    def editnode(self, id, node):
        try:
            sql = "UPDATE NODES SET DATA = ? WHERE ID = ?"
            self._cur.execute(sql, [node.dump_edit_to_db()[0], id])
        except sqlite.DatabaseError, e:  # pragma: no cover
            raise DatabaseException("SQLite: %s" % (e))
        self._setnodetags(node)
        self._checktags()
        self._commit()

    def addnodes(self, nodes):
        """
        This method writes the data as an ecrypted string to
        the database
        """
        for n in nodes:
            sql = "INSERT INTO NODES(DATA) VALUES(?)"
            value = n.dump_edit_to_db()
            try:
                self._cur.execute(sql, value)
            except sqlite.DatabaseError, e:  # pragma: no cover
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

            except sqlite.DatabaseError, e:  # pragma: no cover
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
                    sql += " INTERSECT "  # pragma: no cover
                else:
                    first = False
                sql += ("SELECT NODE FROM LOOKUP LEFT JOIN TAGS ON TAG = "
                        " TAGS.ID WHERE TAGS.DATA LIKE ? ")
                # this is correct if tags are ciphertext
                p = t._name.strip()
                # this is wrong, it will work when tags are stored as plain text
                # p = t.name.strip()
                p = '%'+p+'%'
                params = [p]

        try:
            self._cur.execute(sql, params)
            rows = self._cur.fetchall()
            ids = [row[0] for row in rows]
            return ids
        except sqlite.DatabaseError, e:  # pragma: no cover
            raise DatabaseException("SQLite: %s" % (e))

    def _commit(self):
        try:
            self._con.commit()
        except sqlite.DatabaseError, e:  # pragma: no cover
            self._con.rollback()
            raise DatabaseException(
                "SQLite: Error commiting data to db [%s]" % (e))

    def _create_tag(self, tag):
        """add tags to db"""
        # sql = "INSERT OR REPLACE INTO TAGS(DATA) VALUES(?)"
        sql = "INSERT OR IGNORE INTO TAGS(DATA) VALUES(?)"

        if isinstance(tag, str):
            self._cur.execute(sql, [tag])
        else:
            self._cur.execute(sql, [tag._name])

    def _deletenodetags(self, node):
        try:
            sql = "DELETE FROM LOOKUP WHERE NODE = ?"
            self._cur.execute(sql, [node._id])
        except sqlite.DatabaseError, e:  # pragma: no cover
            raise DatabaseException("SQLite: %s" % (e))
        self._commit()

    def _update_tag_lookup(self, node, tag_id):
        sql = "INSERT OR REPLACE INTO LOOKUP VALUES(?, ?)"
        params = [node._id, tag_id]
        try:
            self._cur.execute(sql, params)
        except sqlite.DatabaseError, e:  # pragma: no cover
            raise DatabaseException("SQLite: %s" % (e))

    def _tagids(self, tags):
        ids = []
        sql = "SELECT ID FROM TAGS WHERE DATA LIKE ?"
        for tag in tags:
            try:
                if isinstance(tag, str):
                    enc = CryptoEngine.get()
                    tag = enc.encrypt(tag)
                    self._cur.execute(sql, [tag])
                else:
                    self._cur.execute(sql, [tag._name+'%'])
                values = self._cur.fetchall()
                if values:
                    ids.extend(list(itertools.chain(*values)))
                else:
                    self._create_tag(tag)
                    ids.append(self._cur.lastrowid)
            except sqlite.DatabaseError, e:  # pragma: no cover
                raise DatabaseException("SQLite: %s" % (e))
        return ids

    def _setnodetags(self, node):
        ids = self._tagids(node.tags)
        for tagid in ids:
            self._update_tag_lookup(node, tagid)
        self._commit()

    def _checktags(self):
        try:
            sql = "DELETE FROM TAGS WHERE ID NOT IN (SELECT TAG FROM" \
                + " LOOKUP GROUP BY TAG)"
            self._cur.execute(sql)
        except sqlite.DatabaseError, e:  # pragma: no cover
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
        if self._cur.fetchone() is None:
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
            except DatabaseException, e:  # pragma: no cover
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
        except sqlite.DatabaseError, e:  # pragma: no cover
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
