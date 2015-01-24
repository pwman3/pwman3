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
# Copyright (C) 2012 Oz Nahum <nahumoz@gmail.com>
# ============================================================================
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
# ============================================================================

"""Postgresql Database implementation."""
import sys
if sys.version_info.major > 2:  # pragma: no cover
    from urllib import parse as urlparse
else:
    from urlparse import urlparse
import psycopg2 as pg
from pwman.data.database import Database, DatabaseException, __DB_FORMAT__


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
    def check_db_version(cls, user, dbname='pwman'):
        """
        Check the database version
        """
        con = pg.connect("dbname=pwman user=%s" % user)
        cur = con.cursor()
        try:
            cur.execute("SELECT VERSION from DBVERSION")
            version = cur.fetchone()
            return version
        except pg.ProgrammingError:
            con.rollback()
            raise DatabaseException("Something seems fishy with the DB")

    def __init__(self, pgsqluri, dbformat=__DB_FORMAT__):
        """
        Initialise PostgresqlDatabase instance.
        """
        self._pgsqluri = pgsqluri
        self.dbversion = dbformat

    def _open(self):

        u = urlparse(self._pgsqluri)
        self._con = pg.connect(database=u.path[1:], user=u.username,
                               password=u.password, host=u.hostname)
        self._cur = self._con.cursor()
        self._create_tables()

    def close(self):
        # TODO: implement _clean_orphands
        self._cur.close()
        self._con.close()

    def listtags(self, filter=None):
        pass

    def editnode(self, nid, **kwargs):
        pass

    def add_node(self, node):
        sql = ("INSERT INTO NODE(USERNAME, PASSWORD, URL, NOTES)"
               "VALUES(%s, %s, %s, %s)")
        node_tags = list(node)
        node, tags = node_tags[:4], node_tags[-1]
        self._cur.execute(sql, (node))
        #self._setnodetags(self._cur.lastrowid, tags)
        self._con.commit()

    def removenodes(self, nodes):
        pass

    def listnodes(self):
        pass

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
                              "nodeid SERIAL REFERENCES NODE(ID),"
                              "tagid SERIAL REFERENCES TAG(ID)"
                              ")")

            self._cur.execute("CREATE TABLE CRYPTO "
                              "(SEED TEXT, DIGEST TEXT)")

            self._cur.execute("CREATE TABLE DBVERSION("
                              "VERSION TEXT NOT NULL DEFAULT {}"
                              ")".format(__DB_FORMAT__))

            self._cur.execute("INSERT INTO DBVERSION VALUES(%s)",
                              (self.dbversion,))

            self._con.commit()
        except pg.ProgrammingError:
            self._con.rollback()

    def save_crypto_info(self, seed, digest):
        """save the random seed and the digested key"""
        self._cur.execute("DELETE  FROM CRYPTO")
        self._cur.execute("INSERT INTO CRYPTO VALUES(%s, %s)", (seed, digest))
        self._con.commit()

    def fetch_crypto_info(self):
        self._cur.execute("SELECT * FROM CRYPTO")
        row = self._cur.fetchone()
        return row

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
        except TypeError:
            return None
