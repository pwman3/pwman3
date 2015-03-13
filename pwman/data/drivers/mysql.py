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
# Copyright (C) 2012-2015 Oz Nahum <nahumoz@gmail.com>
# ============================================================================
#mysql -u root -p
#create database pwmantest
#create user 'pwman'@'localhost' IDENTIFIED BY '123456';
#grant all on pwmantest.* to 'pwman'@'localhost';

"""MySQL Database implementation."""
from __future__ import print_function
from pwman.data.database import Database, __DB_FORMAT__

import pymysql as mysql
mysql.install_as_MySQLdb()
#else:
#    import MySQLdb as mysql


class MySQLDatabase(Database):

    @classmethod
    def check_db_version(cls, dburi):
        port = 3306
        credentials, host = dburi.netloc.split('@')
        user, passwd = credentials.split(':')
        if ':' in host:
            host, port = host.split(':')
            port = int(port)
        con = mysql.connect(host=host, port=port, user=user, passwd=passwd,
                            db=dburi.path.lstrip('/'))
        cur = con.cursor()
        try:
            cur.execute("SELECT VERSION FROM DBVERSION")
            version = cur.fetchone()
            cur.close()
            con.close()
            return version[-1]
        except mysql.ProgrammingError:
            con.rollback()

    def __init__(self, mysqluri, dbformat=__DB_FORMAT__):
        self.dburi = mysqluri
        self.dbversion = dbformat

    def _open(self):

        port = 3306
        credentials, host = self.dburi.netloc.split('@')
        user, passwd = credentials.split(':')
        if ':' in host:
            host, port = host.split(':')
            port = int(port)

        self._con = mysql.connect(host=host, port=port, user=user,
                                  passwd=passwd,
                                  db=self.dburi.path.lstrip('/'))
        self._cur = self._con.cursor()
        self._create_tables()

    def _create_tables(self):

        try:
            self._cur.execute("SELECT 1 from DBVERSION")
            version = self._cur.fetchone()
            if version:
                return
        except mysql.ProgrammingError:
            self._con.rollback()

        try:
            self._cur.execute("CREATE TABLE NODE(ID SERIAL PRIMARY KEY, "
                              "USERNAME TEXT NOT NULL, "
                              "PASSWORD TEXT NOT NULL, "
                              "URL TEXT NOT NULL, "
                              "NOTES TEXT NOT NULL"
                              ")")

            self._cur.execute("CREATE TABLE TAG"
                              "(ID  SERIAL PRIMARY KEY,"
                              "DATA VARCHAR(255) NOT NULL UNIQUE)")

            self._cur.execute("CREATE TABLE LOOKUP ("
                              "nodeid INTEGER NOT NULL REFERENCES NODE(ID),"
                              "tagid INTEGER NOT NULL REFERENCES TAG(ID)"
                              ")")

            self._cur.execute("CREATE TABLE CRYPTO "
                              "(SEED TEXT, DIGEST TEXT)")

            self._cur.execute("CREATE TABLE DBVERSION("
                              "VERSION TEXT NOT NULL "
                              ")")

            self._cur.execute("INSERT INTO DBVERSION VALUES(%s)",
                              (self.dbversion,))

            self._con.commit()
        except mysql.ProgrammingError:  # pragma: no cover
            self._con.rollback()

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

    def add_node(self, node):
        sql = ("INSERT INTO NODE(USERNAME, PASSWORD, URL, NOTES)"
               "VALUES(%s, %s, %s, %s)")
        node_tags = list(node)
        node, tags = node_tags[:4], node_tags[-1]
        self._cur.execute(sql, (node))
        nid = self._cur.lastrowid
        self._setnodetags(nid, tags)
        self._con.commit()

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

    def _setnodetags(self, nodeid, tags):
        for tag in tags:
            tid = self._get_or_create_tag(tag)
            self._update_tag_lookup(nodeid, tid)

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
            sql_insert = "INSERT INTO TAG(DATA) VALUES(%s)"
            self._cur.execute(sql_insert, ([tagcipher]))
            return self._cur.lastrowid

    def _update_tag_lookup(self, nodeid, tid):
        sql_lookup = "INSERT INTO LOOKUP(nodeid, tagid) VALUES(%s, %s)"
        self._cur.execute(sql_lookup, (nodeid, tid))
        self._con.commit()

    def fetch_crypto_info(self):
        self._cur.execute("SELECT * FROM CRYPTO")
        row = self._cur.fetchone()
        return row

    def listtags(self):
        self._clean_orphans()
        get_tags = "select DATA from TAG"
        self._cur.execute(get_tags)
        tags = self._cur.fetchall()
        if tags:
            return [t[0] for t in tags]
        return []  # pragma: no cover

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

    def save_crypto_info(self, seed, digest):
        """save the random seed and the digested key"""
        self._cur.execute("DELETE  FROM CRYPTO")
        self._cur.execute("INSERT INTO CRYPTO VALUES(%s, %s)", (seed, digest))
        self._con.commit()

    def loadkey(self):
        sql = "SELECT * FROM CRYPTO"
        try:
            self._cur.execute(sql)
            seed, digest = self._cur.fetchone()
            return seed + u'$6$' + digest
        except TypeError:  # pragma: no cover
            return None

    def _clean_orphans(self):
        clean = ("delete from TAG where not exists "
                 "(select 'x' from LOOKUP l where l.TAGID = TAG.ID)")
        self._cur.execute(clean)

    def removenodes(self, nid):
        # shall we do this also in the sqlite driver?
        sql_clean = "DELETE FROM LOOKUP WHERE NODEID=%s"
        self._cur.execute(sql_clean, nid)
        sql_rm = "delete from NODE where ID = %s"
        self._cur.execute(sql_rm, nid)
        self._con.commit()
        self._con.commit()

    def savekey(self, key):
        salt, digest = key.split('$6$')
        sql = "INSERT INTO CRYPTO(SEED, DIGEST) VALUES(%s,%s)"
        self._cur.execute("DELETE FROM CRYPTO")
        self._cur.execute(sql, (salt, digest))
        self._digest = digest.encode('utf-8')
        self._salt = salt.encode('utf-8')
        self._con.commit()
