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
# Copyright (C) 2015 Oz Nahum <nahumoz@gmail.com>
# ============================================================================
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
# ============================================================================

"""Postgresql Database implementation."""
import psycopg2 as pg
from pwman.data.database import Database, __DB_FORMAT__


class PostgresqlDatabase(Database):

    """
    Postgresql Database implementation

    This assumes that your database admin has created a pwman database
    for you and shared the user name and password with you.

    This driver send no clear text on wire. ONLY excrypted stuff is sent
    between the client and the server.

    Encryption and decryption are happening on your localhost, not on
    the Postgresql server.
    """

    @classmethod
    def check_db_version(cls, dburi):
        """
        Check the database version
        """
        con = pg.connect(dburi)
        cur = con.cursor()
        try:
            cur.execute("SELECT VERSION from DBVERSION")
            version = cur.fetchone()
            cur.close()
            con.close()
            return version[-1]
        except pg.ProgrammingError:
            con.rollback()

    def __init__(self, pgsqluri, dbformat=__DB_FORMAT__):
        """
        Initialise PostgresqlDatabase instance.
        """
        self._pgsqluri = pgsqluri
        self.dbversion = dbformat

    def _open(self):

        self._con = pg.connect(self._pgsqluri.geturl())
        self._cur = self._con.cursor()
        self._create_tables()

    def listnodes(self, filter=None):
        if not filter:
            sql_all = "SELECT ID FROM NODE"
            self._cur.execute(sql_all)
            ids = self._cur.fetchall()
            return [id[0] for id in ids]
        else:
            tagid = self._get_tag(filter)
            if not tagid:
                return []  # pragma: no cover

            sql_filter = "SELECT NODEID FROM LOOKUP WHERE TAGID = %s "
            self._cur.execute(sql_filter, (tagid))
            self._con.commit()
            ids = self._cur.fetchall()
            return [id[0] for id in ids]

    def listtags(self):
        self._clean_orphans()
        get_tags = "select data from tag"
        self._cur.execute(get_tags)
        tags = self._cur.fetchall()
        if tags:
            return [t[0] for t in tags]
        return []  # pragma: no cover

    def _create_tables(self):

        try:
            self._cur.execute("SELECT 1 from DBVERSION")
            version = self._cur.fetchone()
            if version:
                return
        except pg.ProgrammingError:
            self._con.rollback()

        try:
            self._cur.execute("CREATE TABLE NODE(ID SERIAL PRIMARY KEY, "
                              "USERNAME TEXT NOT NULL, "
                              "PASSWORD TEXT NOT NULL, "
                              "URL TEXT NOT NULL, "
                              "NOTES TEXT NOT NULL"
                              ")")

            self._cur.execute("CREATE TABLE TAG"
                              "(ID SERIAL PRIMARY KEY,"
                              "DATA TEXT NOT NULL UNIQUE)")

            self._cur.execute("CREATE TABLE LOOKUP ("
                              "nodeid INTEGER NOT NULL REFERENCES NODE(ID),"
                              "tagid INTEGER NOT NULL REFERENCES TAG(ID)"
                              ")")

            self._cur.execute("CREATE TABLE CRYPTO "
                              "(SEED TEXT, DIGEST TEXT)")

            self._cur.execute("CREATE TABLE DBVERSION("
                              "VERSION TEXT NOT NULL DEFAULT {}"
                              ")".format(__DB_FORMAT__))

            self._cur.execute("INSERT INTO DBVERSION VALUES(%s)",
                              (self.dbversion,))

            self._con.commit()
        except pg.ProgrammingError:  # pragma: no cover
            self._con.rollback()

    def fetch_crypto_info(self):
        self._cur.execute("SELECT * FROM CRYPTO")
        row = self._cur.fetchone()
        return row

    def save_crypto_info(self, seed, digest):
        """save the random seed and the digested key"""
        self._cur.execute("DELETE  FROM CRYPTO")
        self._cur.execute("INSERT INTO CRYPTO VALUES(%s, %s)", (seed, digest))
        self._con.commit()

    def add_node(self, node):
        sql = ("INSERT INTO NODE(USERNAME, PASSWORD, URL, NOTES)"
               "VALUES(%s, %s, %s, %s) RETURNING ID")
        node_tags = list(node)
        node, tags = node_tags[:4], node_tags[-1]
        self._cur.execute(sql, (node))
        nid = self._cur.fetchone()[0]
        self._setnodetags(nid, tags)
        self._con.commit()

    def _get_tag(self, tagcipher):
        sql_search = "SELECT ID FROM TAG WHERE DATA = %s"
        self._cur.execute(sql_search, ([tagcipher]))
        rv = self._cur.fetchone()
        return rv

    def _get_or_create_tag(self, tagcipher):
        rv = self._get_tag(tagcipher)
        if rv:
            return rv[0]
        else:
            sql_insert = "INSERT INTO TAG(DATA) VALUES(%s) RETURNING ID"
            self._cur.execute(sql_insert, ([tagcipher]))
            rid = self._cur.fetchone()[0]
            return rid

    def _update_tag_lookup(self, nodeid, tid):
        sql_lookup = "INSERT INTO LOOKUP(nodeid, tagid) VALUES(%s, %s)"
        self._cur.execute(sql_lookup, (nodeid, tid))
        self._con.commit()

    def _setnodetags(self, nodeid, tags):
        for tag in tags:
            tid = self._get_or_create_tag(tag)
            self._update_tag_lookup(nodeid, tid)

    def _get_node_tags(self, node):
        sql = "SELECT tagid FROM LOOKUP WHERE NODEID = %s"
        self._cur.execute(sql, (str(node[0]),))
        tagids = self._cur.fetchall()
        if tagids:
            sql = ("SELECT DATA FROM TAG WHERE ID IN (%s)"
                   "" % ','.join(['%s']*len(tagids)))
            tagids = [str(id[0]) for id in tagids]
            self._cur.execute(sql, (tagids))
            tags = self._cur.fetchall()
            for t in tags:
                yield t[0]

    def getnodes(self, ids):
        if ids:
            sql = ("SELECT * FROM NODE WHERE ID IN ({})"
                   "".format(','.join('%s' for i in ids)))
        else:
            sql = "SELECT * FROM NODE"
        self._cur.execute(sql, (ids))
        nodes = self._cur.fetchall()
        nodes_w_tags = []
        for node in nodes:
            tags = list(self._get_node_tags(node))
            nodes_w_tags.append(list(node) + tags)

        return nodes_w_tags

    def editnode(self, nid, **kwargs):  # pragma: no cover
        tags = kwargs.pop('tags', None)
        sql = ("UPDATE NODE SET %s WHERE ID = %%s "
               "" % ','.join('%s=%%s' % k for k in list(kwargs)))
        self._cur.execute(sql, (list(kwargs.values()) + [nid]))
        if tags:
            # update all old node entries in lookup
            # create new entries
            # clean all old tags
            sql_clean = "DELETE FROM LOOKUP WHERE NODEID=?"
            self._cur.execute(sql_clean, (str(nid),))
            self._setnodetags(nid, tags)

        self._con.commit()

    def removenodes(self, nid):
        # shall we do this also in the sqlite driver?
        sql_clean = "DELETE FROM LOOKUP WHERE NODEID=%s"
        self._cur.execute(sql_clean, nid)
        sql_rm = "delete from node where id = %s"
        self._cur.execute(sql_rm, nid)
        self._con.commit()

    def _clean_orphans(self):
        clean = ("delete from tag where not exists "
                 "(select 'x' from lookup l where l.tagid = tag.id)")
        self._cur.execute(clean)
        self._con.commit()

    def savekey(self, key):
        salt, digest = key.split('$6$')
        sql = "INSERT INTO CRYPTO(SEED, DIGEST) VALUES(%s,%s)"
        self._cur.execute("DELETE FROM CRYPTO")
        self._cur.execute(sql, (salt, digest))
        self._digest = digest.encode('utf-8')
        self._salt = salt.encode('utf-8')
        self._con.commit()

    def loadkey(self):
        sql = "SELECT * FROM CRYPTO"
        try:
            self._cur.execute(sql)
            seed, digest = self._cur.fetchone()
            return seed + u'$6$' + digest
        except TypeError:  # pragma: no cover
            return None

    def close(self):  # pragma: no cover
        self._clean_orphans()
        self._cur.close()
        self._con.close()
