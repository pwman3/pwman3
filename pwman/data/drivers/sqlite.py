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
from pwman.data.database import Database
from pwman.data.database import __DB_FORMAT__
import sqlite3 as sqlite


class SQLite(Database):

    @classmethod
    def check_db_version(cls, fname):
        """
        check the database version.
        """
        con = sqlite.connect(fname)
        cur = con.cursor()
        cur.execute("PRAGMA TABLE_INFO(DBVERSION)")
        row = cur.fetchone()
        try:
            return row[-2]
        except TypeError:
            return str(__DB_FORMAT__)

    def __init__(self, filename, dbformat=__DB_FORMAT__):
        """Initialise SQLitePwmanDatabase instance."""
        self._filename = filename
        self.dbformat = dbformat

    def _open(self):
        self._con = sqlite.connect(self._filename)
        self._cur = self._con.cursor()
        self._create_tables()

    def listnodes(self, filter=None):
        """return a list of node ids"""
        if not filter:
            sql_all = "SELECT ID FROM NODE"
            self._cur.execute(sql_all)
            ids = self._cur.fetchall()
            return [id[0] for id in ids]
        else:
            tagid = self._get_tag(filter)
            if not tagid:
                return []
            sql_filter = "SELECT NODEID FROM LOOKUP WHERE TAGID = ? "
            self._cur.execute(sql_filter, (tagid))
            ids = self._cur.fetchall()
            return [id[0] for id in ids]

    def listtags(self):
        self._clean_orphans()
        get_tags = "select data from tag"
        self._cur.execute(get_tags)
        tags = self._cur.fetchall()
        if tags:
            return [t[0] for t in tags]
        return []

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
                          "(VERSION TEXT NOT NULL DEFAULT '%s')" %
                          self.dbformat)
        self._cur.execute("INSERT INTO DBVERSION VALUES('%s')" %
                          self.dbformat)
        try:
            self._con.commit()
        except Exception as e:  # pragma: no cover
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

    def _get_node_tags(self, node):
        sql = "SELECT tagid FROM LOOKUP WHERE NODEID = ?"
        tagids = self._cur.execute(sql, (str(node[0]),)).fetchall()
        sql = ("SELECT DATA FROM TAG WHERE ID IN (%s)"
               "" % ','.join('?'*len(tagids)))
        tagids = [str(id[0]) for id in tagids]
        self._cur.execute(sql, (tagids))
        tags = self._cur.fetchall()
        for t in tags:
            yield t[0]

    def getnodes(self, ids):
        """
        get nodes as raw ciphertext
        """
        if ids:
            sql = ("SELECT * FROM NODE WHERE ID IN ({})"
                   "".format(','.join('?'*len(ids))))
        else:
            sql = "SELECT * FROM NODE"

        self._cur.execute(sql, (ids))
        nodes = self._cur.fetchall()
        nodes_w_tags = []
        for node in nodes:
            tags = list(self._get_node_tags(node))
            nodes_w_tags.append(list(node) + tags)

        return nodes_w_tags

    def editnode(self, nid, **kwargs):
        tags = kwargs.pop('tags', None)
        sql = ("UPDATE NODE SET %s WHERE ID = ? "
               "" % ','.join('%s=?' % k for k in list(kwargs)))
        self._cur.execute(sql, (list(kwargs.values()) + [nid]))
        if tags:
            # update all old node entries in lookup
            # create new entries
            # clean all old tags
            sql_clean = "DELETE FROM LOOKUP WHERE NODEID=?"
            self._cur.execute(sql_clean, (str(nid),))
            self._setnodetags(nid, tags)

        self._con.commit()

    def removenodes(self, nids):
        sql_rm = "delete from node where id in (%s)" % ','.join('?'*len(nids))
        self._cur.execute(sql_rm, (nids))
        self._con.commit()

    def _clean_orphans(self):
        clean = ("delete from tag where not exists "
                 "(select 'x' from lookup l where l.tagid = tag.id)")

        self._cur.execute(clean)
        self._con.commit()

    def savekey(self, key):
        salt, digest = key.split('$6$')
        sql = "INSERT INTO CRYPTO(SEED, DIGEST) VALUES(?,?)"
        self._cur.execute("DELETE FROM CRYPTO")
        self._cur.execute(sql, (salt, digest))
        self._digest = digest.encode('utf-8')
        self._salt = salt.encode('utf-8')
        self._con.commit()

    def loadkey(self):
        # TODO: rename this method!
        """
        return _keycrypted
        """
        sql = "SELECT * FROM CRYPTO"
        try:
            seed, digest = self._cur.execute(sql).fetchone()
            return seed + u'$6$' + digest
        except TypeError:
            return None

    def close(self):
        self._clean_orphans()
        self._cur.close()
        self._con.close()
