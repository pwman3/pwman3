# ============================================================================
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
# ============================================================================
# Copyright (C) 2012, 2013, 2014 Oz Nahum Tiram <nahumoz@gmail.com>
# ============================================================================
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
# ============================================================================

"""SQLite Database implementation."""
from pwman.data.database import Database, DatabaseException
from pwman.data.database import __DB_FORMAT__
from pwman.data.nodes import NewNode
from pwman.data.tags import TagNew
from pwman.util.crypto_engine import CryptoEngine
import sqlite3 as sqlite
import itertools


class SQLiteDatabaseNewForm(Database):
    """SQLite Database implementation"""

    @classmethod
    def check_db_version(cls, fname):
        """
        check the data base version.
        """
        con = sqlite.connect(fname)
        cur = con.cursor()
        cur.execute("PRAGMA TABLE_INFO(DBVERSION)")
        row = cur.fetchone()
        if not row:
            return "0.3"  # pragma: no cover
        try:
            return row[-2]
        except IndexError:  # pragma: no cover
            raise DatabaseException("Something seems fishy with the DB")

    def __init__(self, filename, dbformat=__DB_FORMAT__):
        """Initialise SQLitePwmanDatabase instance."""
        super(SQLiteDatabaseNewForm, self).__init__()
        self._filename = filename
        self.dbformat = dbformat

    def _open(self):
        try:
            self._con = sqlite.connect(self._filename)
            self._cur = self._con.cursor()
            self._checktables()
        except sqlite.DatabaseError as e:  # pragma: no cover
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
                params.append(t._name.decode()+u'%')
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

        except sqlite.DatabaseError as e:  # pragma: no cover
            raise DatabaseException("SQLite: %s" % (e))
        except sqlite.InterfaceError as e:  # pragma: no cover
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
        except sqlite.DatabaseError as e:  # pragma: no cover
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
            except sqlite.DatabaseError as e:  # pragma: no cover
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

            except sqlite.DatabaseError as e:  # pragma: no cover
                raise DatabaseException("SQLite: %s" % (e))
            self._deletenodetags(n)

        self._checktags()
        self._commit()

    def listnodes(self):
        sql = ''
        params = []
        if not self._filtertags:
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
                # this is wrong, it will work when tags are stored as plain
                # text
                # p = t.name.strip()
                p = '%'+p+'%'
                params = [p]

        try:
            self._cur.execute(sql, params)
            rows = self._cur.fetchall()
            ids = [row[0] for row in rows]
            return ids
        except sqlite.DatabaseError as e:  # pragma: no cover
            raise DatabaseException("SQLite: %s" % (e))

    def _commit(self):
        try:
            self._con.commit()
        except sqlite.DatabaseError as e:  # pragma: no cover
            self._con.rollback()
            raise DatabaseException(
                "SQLite: Error commiting data to db [%s]" % (e))

    def _create_tag(self, tag):
        """add tags to db"""
        # sql = "INSERT OR REPLACE INTO TAGS(DATA) VALUES(?)"
        sql = "INSERT OR IGNORE INTO TAGS(DATA) VALUES(?)"

        if isinstance(tag, str):
            self._cur.execute(sql, [tag])
        elif isinstance(tag, TagNew):
            self._cur.execute(sql, [tag._name])
        else:
            self._cur.execute(sql, [tag.decode()])

    def _deletenodetags(self, node):
        try:
            sql = "DELETE FROM LOOKUP WHERE NODE = ?"
            self._cur.execute(sql, [node._id])
        except sqlite.DatabaseError as e:  # pragma: no cover
            raise DatabaseException("SQLite: %s" % (e))
        self._commit()

    def _update_tag_lookup(self, node, tag_id):
        sql = "INSERT OR REPLACE INTO LOOKUP VALUES(?, ?)"
        params = [node._id, tag_id]
        try:
            self._cur.execute(sql, params)
        except sqlite.DatabaseError as e:  # pragma: no cover
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
                elif isinstance(tag, TagNew):
                    self._cur.execute(sql, [tag._name.decode()+u'%'])
                else:
                    self._cur.execute(sql, [tag.decode()+u'%'])

                values = self._cur.fetchall()
                if values:  # tags already exist in the database
                    ids.extend(list(itertools.chain(*values)))
                else:
                    self._create_tag(tag)
                    ids.append(self._cur.lastrowid)
            except sqlite.DatabaseError as e:  # pragma: no cover
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
        except sqlite.DatabaseError as e:  # pragma: no cover
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
                              " AUTOINCREMENT,DATA BLOB NOT NULL)")
            self._cur.execute("CREATE TABLE TAGS"
                              "(ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                              "DATA BLOB NOT NULL UNIQUE)")
            self._cur.execute("CREATE TABLE LOOKUP"
                              "(NODE INTEGER NOT NULL, TAG INTEGER NOT NULL,"
                              " PRIMARY KEY(NODE, TAG))")

            self._cur.execute("CREATE TABLE KEY"
                              "(THEKEY TEXT NOT NULL DEFAULT '')")
            self._cur.execute("INSERT INTO KEY VALUES('')")
            # create a table to hold DB version info
            self._cur.execute("CREATE TABLE DBVERSION"
                              "(DBVERSION TEXT NOT NULL DEFAULT '%s')" %
                              self.dbformat)
            self._cur.execute("INSERT INTO DBVERSION VALUES('%s')" %
                              self.dbformat)
            try:
                self._con.commit()
            except DatabaseException as e:  # pragma: no cover
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
        except sqlite.DatabaseError as e:  # pragma: no cover
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


class SQLite(SQLiteDatabaseNewForm):

    def __init__(self, filename, dbformat=0.6):
        """Initialise SQLitePwmanDatabase instance."""
        self._filename = filename
        self.dbformat = dbformat

    def _open(self):
        self._con = sqlite.connect(self._filename)
        self._cur = self._con.cursor()

    def listnodes(self, filter=None):
        if not filter:
            sql_all = "SELECT ID FROM NODE"
            self._cur.execute(sql_all)
            ids = self._cur.fetchall()
            return ids
        else:
            tagid = self._get_tag(filter)
            sql_filter = "SELECT NODEID FROM LOOKUP WHERE TAGID = ? "
            self._cur.execute(sql_filter, (tagid))
            ids = self._cur.fetchall()
            return ids

    def _create_tables(self):
        self._cur.execute("PRAGMA TABLE_INFO(NODE)")
        if self._cur.fetchone() is not None:
            return

        self._cur.execute("CREATE TABLE NODE (ID INTEGER PRIMARY KEY "
                          "AUTOINCREMENT, "
                          "USER TEXT NOT NULL, "
                          "PASSWORD TEXT NOT NULL, "
                          "URL TEXT NOT NULL,"
                          "NOTES TEXT NOT NULL)")

        self._cur.execute("CREATE TABLE TAG"
                          "(ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                          "DATA BLOB NOT NULL UNIQUE)")

        self._cur.execute("CREATE TABLE LOOKUP ("
                          "nodeid INTEGER NOT NULL, "
                          "tagid INTEGER NOT NULL, "
                          "FOREIGN KEY(nodeid) REFERENCES NODE(ID),"
                          "FOREIGN KEY(tagid) REFERENCES TAG(ID))")

        self._cur.execute("CREATE TABLE CRYPTO"
                          "(SEED TEXT,"
                          " DIGEST TEXT)")

        # create a table to hold DB version info
        self._cur.execute("CREATE TABLE DBVERSION"
                          "(DB VERSION TEXT NOT NULL DEFAULT '%s')" %
                          self.dbformat)
        self._cur.execute("INSERT INTO DBVERSION VALUES('%s')" %
                          self.dbformat)
        try:
            self._con.commit()
        except DatabaseException as e:  # pragma: no cover
            self._con.rollback()
            raise e

    def fetch_crypto_info(self):
        self._cur.execute("SELECT * FROM CRYPTO")
        keyrow = self._cur.fetchone()
        return keyrow

    def save_crypto_info(self, seed, digest):
        """save the random seed and the digested key"""
        self._cur.execute("DELETE  FROM CRYPTO")
        self._cur.execute("INSERT INTO CRYPTO VALUES(?, ?)", [seed, digest])
        self._con.commit()

    def add_node(self, node):
        sql = ("INSERT INTO NODE(USER, PASSWORD, URL, NOTES)"
               "VALUES(?, ?, ?, ?)")
        node_tags = list(node)
        node, tags = node_tags[:4], node_tags[-1]
        self._cur.execute(sql, (node))
        self._setnodetags(self._cur.lastrowid, tags)
        self._con.commit()

    def _get_tag(self, tagcipher):
        sql_search = "SELECT ID FROM TAG WHERE DATA = ?"
        self._cur.execute(sql_search, ([tagcipher]))
        rv = self._cur.fetchone()
        return rv

    def _get_or_create_tag(self, tagcipher):
        rv = self._get_tag(tagcipher)
        if rv:
            return rv[0]
        else:
            sql_insert = "INSERT INTO TAG(DATA) VALUES(?)"
            self._cur.execute(sql_insert, ([tagcipher]))
            return self._cur.lastrowid

    def _update_tag_lookup(self, nodeid, tid):
        sql_lookup = "INSERT INTO LOOKUP(nodeid, tagid) VALUES(?,?)"
        self._cur.execute(sql_lookup, (nodeid, tid))
        self._con.commit()

    def _setnodetags(self, nodeid, tags):
        for tag in tags:
            tid = self._get_or_create_tag(tag)
            self._update_tag_lookup(nodeid, tid)

    def getnodes(self, ids):
        sql = "SELECT * FROM NODE WHERE ID IN (%s)" % ','.join('?'*len(ids))
        self._cur.execute(sql, (ids))
        nodes = self._cur.fetchall()
        return nodes

    def editnode(self, nid, **kwargs):
        tags = kwargs.pop('tags', None)
        sql = ("UPDATE NODE SET %s WHERE ID = ? "
               "" % ','.join('%s=?' % k for k in list(kwargs)))
        self._cur.execute(sql, (list(kwargs.values()) + [nid]))
        if tags:
            #  update all old node entries in lookup
            #  create new entries
            # clean all old tags
            sql_clean = "DELETE FROM LOOKUP WHERE NODEID=?"
            self._cur.execute(sql_clean, str(nid))
            # TODO, update tags lookup
            self._setnodetags(nid, tags)

        self._con.commit()

    def _clean_orphands(self):
        clean = ("delete from tag where not exists "
                 "(select 'x' from lookup l where l.tagid = tag.id)")

        self._cur.execute(clean)
        self._con.commit()

    def close(self):
        self._clean_orphands()
        self._cur.close()
        self._con.close()
