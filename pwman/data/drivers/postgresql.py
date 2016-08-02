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
        self.ProgrammingError = pg.ProgrammingError
        self._data_wrapper = lambda x: pg.Binary(x)

    def _open(self):

        self._con = pg.connect(self._pgsqluri.geturl())
        self._cur = self._con.cursor()
        self._create_tables()

    def _get_tag(self, tagcipher):
        sql_search = "SELECT * FROM TAG"
        self._cur.execute(sql_search)
        ce = CryptoEngine.get()

        try:
            tag = ce.decrypt(tagcipher)
            encrypted = True
        except Exception:
            tag = tagcipher
            encrypted = False

        rv = self._cur.fetchall()
        for idx, cipher in rv:
            cipher = cipher.tobytes()
            if encrypted and tag == ce.decrypt(cipher):
                return idx
            elif tag == cipher:
                return idx

    def _create_tables(self):
        if self._check_tables():
            return
        try:
            self._cur.execute("CREATE TABLE NODE(ID SERIAL PRIMARY KEY, "
                              "USERNAME BYTEA NOT NULL, "
                              "PASSWORD BYTEA NOT NULL, "
                              "URL BYTEA NOT NULL, "
                              "NOTES BYTEA NOT NULL"
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
            seed, digest = self._cur.fetchone()
            return seed.tobytes() + b'$6$' + digest.tobytes()
        except TypeError:  # pragma: no cover
            return None

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
            tags = [t.tobytes() for t in self._get_node_tags(node)]
            nodes_w_tags.append([node[0]] + [item.tobytes() for item in node[1:]] + tags)

        return nodes_w_tags

    def listtags(self):
        self._clean_orphans()
        get_tags = "select DATA from TAG"
        self._cur.execute(get_tags)
        tags = self._cur.fetchall()
        if tags:
            return [t[0].tobytes() for t in tags]
        return []  # pragma: no cover
