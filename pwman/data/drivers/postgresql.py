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
import binascii
import psycopg2 as pg
import psycopg2.extras

from pwman.data.database import Database, __DB_FORMAT__
from pwman.util.crypto_engine import CryptoEngine


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
            return __DB_FORMAT__

    def __init__(self, pgsqluri, dbformat=__DB_FORMAT__):
        """
        Initialise PostgresqlDatabase instance.
        """
        self._pgsqluri = pgsqluri
        self.dbversion = dbformat
        self._sub = "%s"
        self._list_nodes_sql = "SELECT NODEID FROM LOOKUP WHERE TAGID = %s "
        self._add_node_sql = ('INSERT INTO NODE(USERNAME, PASSWORD, URL, '
                              'NOTES) VALUES(%s, %s, %s, %s) RETURNING ID')
        self._insert_tag_sql = "INSERT INTO TAG(DATA) VALUES(%s) RETURNING ID"
        self._get_node_sql = "SELECT * FROM NODE WHERE ID = %s"
        self.ProgrammingError = pg.ProgrammingError
        self._data_wrapper = lambda x: pg.Binary(x)

    def _open(self):

        self._con = pg.connect(self._pgsqluri.geturl())
        self._cur = self._con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        self._create_tables()

    def add_node(self, node):
        node_tags = list(node)
        node, tags = node_tags[:4], node_tags[-1]

        self._cur.execute(self._add_node_sql, list(map(self._data_wrapper, (node))))  # noqa
        self._con.commit()
        nid = self._cur.fetchone()["id"]
        self._setnodetags(nid, tags)
        return nid

    def _get_tag(self, tagcipher):
        sql_search = "SELECT * FROM TAG"
        self._cur.execute(sql_search)
        ce = CryptoEngine.get()

        try:
            tag = ce.decrypt(tagcipher)
            encrypted = True
        except binascii.Error:
            tag = tagcipher
            encrypted = False

        rv = self._cur.fetchall()
        for value in rv:
            cipher = value['data'].tobytes()
            if encrypted and tag == ce.decrypt(cipher):
                return value['id']
            elif tag == cipher:
                return value['id']

    def _get_node_tags(self, node):
        sql = "SELECT tagid FROM LOOKUP WHERE NODEID = {}".format(self._sub)
        try:
            _id = str(node["ID"])
        except KeyError:
            # This is here because postgres coverts columns to lower case
            # if not quoted
            _id = str(node['id'])
        self._cur.execute(sql, (_id,))
        tagids = self._cur.fetchall()

        if tagids:
            sql = ("SELECT DATA FROM TAG WHERE ID IN"
                   " ({})".format(','.join([self._sub]*len(tagids))))
            tagids = [str(t["tagid"]) for t in tagids]
            self._cur.execute(sql, (tagids))
            tags = self._cur.fetchall()
            for t in tags:
                yield t['data'].tobytes()

    def _create_tables(self):
        if self._check_tables():
            return
        try:
            # note: future versions should quote column names
            # USERNAME -> \"USERNAME\" BYTEA NOT NULL
            self._cur.execute("CREATE TABLE NODE(ID SERIAL PRIMARY KEY, "
                              "USERNAME BYTEA NOT NULL, "
                              "PASSWORD BYTEA NOT NULL, "
                              "URL BYTEA NOT NULL, "
                              "NOTES BYTEA NOT NULL,"
                              "MDATE BYTEA"
                              ")")

            self._cur.execute("CREATE TABLE TAG"
                              "(ID  SERIAL PRIMARY KEY,"
                              "DATA BYTEA NOT NULL)")

            self._cur.execute("CREATE TABLE LOOKUP ("
                              "nodeid INTEGER NOT NULL REFERENCES NODE(ID),"
                              "tagid INTEGER NOT NULL REFERENCES TAG(ID)"
                              ")")

            self._cur.execute("CREATE TABLE CRYPTO "
                              "(SEED BYTEA, DIGEST BYTEA)")

            self._cur.execute("CREATE TABLE DBVERSION("
                              "VERSION TEXT NOT NULL)")

            self._cur.execute("INSERT INTO DBVERSION VALUES(%s)",
                              (self.dbversion,))

            self._con.commit()
        except Exception:  # pragma: no cover
            self._con.rollback()

    def savekey(self, key):
        salt, digest = key.split('$6$')
        try:
            salt, digest = salt.encode(), digest.encode()
        except AttributeError:
            pass

        sql = "INSERT INTO CRYPTO(SEED, DIGEST) VALUES({},{})".format(self._sub,  # noqa
                                                                      self._sub)  # noqa
        self._cur.execute("DELETE FROM CRYPTO")
        self._cur.execute(sql, list(map(self._data_wrapper, (salt, digest))))
        self._digest = digest
        self._salt = salt
        self._con.commit()

    def loadkey(self):
        """
        return _keycrypted
        """
        sql = "SELECT * FROM CRYPTO"
        try:
            self._cur.execute(sql)
            rec = self._cur.fetchone()
            return rec['seed'].tobytes() + b'$6$' + rec['digest'].tobytes()
        except TypeError:  # pragma: no cover
            return None

    def lazy_list_node_ids(self, filter=None):
        """return a generator that yields the node ids"""
        # self._con.set_trace_callback(print)
        if not filter:
            sql_all = "SELECT ID FROM NODE"
            self._cur.execute(sql_all)
            for node_id in self._cur.fetchall():
                yield node_id.get("id")
        else:
            tagid = self._get_tag(filter)
            if not tagid:
                yield []  # pragma: no cover

            self._cur.execute(self._list_nodes_sql, (tagid,))
            for node_id in self._cur.fetchall():
                 yield node_id.get("nodeid")

    def getnodes(self, ids):
        if ids:
            sql = ("SELECT * FROM NODE WHERE ID IN ({})"
                   "".format(','.join(self._sub for i in ids)))
        else:
            sql = "SELECT * FROM NODE"
        self._cur.execute(sql, (ids))
        nodes = self._cur.fetchall()
        if not nodes:
            return []

        nodes_w_tags = []

        for node in nodes:
            _n = {k: node[k] for k in node.keys()}
            tags = [t for t in self._get_node_tags(node)]
            dn = {}
            for k, v in node.items():
                if isinstance(v, memoryview,):
                    dn[k] = v.tobytes()
                else:
                    dn[k] = v

            dn['tags'] = tags
            nodes_w_tags.append(dn)

        return nodes_w_tags

    def listtags(self):
        self._clean_orphans()
        get_tags = "select DATA from TAG"
        self._cur.execute(get_tags)
        tags = self._cur.fetchall()
        if tags:
            return [t['data'].tobytes() for t in tags]
        return []  # pragma: no cover
