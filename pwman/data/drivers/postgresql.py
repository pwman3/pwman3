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
    from urllib import urlparse
else:
    from urlparse import urlparse
import psycopg2 as pg
import cPickle
import pwman.util.config as config
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


    create table version

    CREATE TABLE DB_VERSION(DBVERSION TEXT NOT NULL DEFAULT '');

    Check if db_version exists

    SELECT 1
    FROM information_schema.tables where table_name = 'db_version';

    get information:

    SELECT dbversion FROM DB_VERSION;
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

    def listtags(self, all=False):
        sql = ''
        params = {}
        i = 0
        if len(self._filtertags) == 0 or all:
            sql = "SELECT DATA FROM %sTAGS ORDER BY DATA ASC" % (self._prefix)
        else:
            sql = ("SELECT %sTAGS.DATA FROM %sLOOKUP"
                   + " INNER JOIN %sTAGS ON %sLOOKUP.TAG = %sTAGS.ID"
                   + " WHERE NODE IN (") % (self._prefix, self._prefix,
                                            self._prefix,
                                            self._prefix, self._prefix)
            first = True

            i += 1
            paramname = "tag%d" % (i)
            for t in self._filtertags:
                if not first:
                    sql += " INTERSECT "
                else:
                    first = False

                sql += ("SELECT NODE FROM %sLOOKUP LEFT JOIN %sTAGS ON TAG "
                        "= %sTAGS.ID "
                        " WHERE %sTAGS.DATA = %%(%s)s" % (self._prefix,
                                                          self._prefix,
                                                          self._prefix,
                                                          self._prefix,
                                                          paramname))
                params[paramname] = cPickle.dumps(t)
            sql += ") EXCEPT SELECT DATA FROM %sTAGS WHERE " % self._prefix
            first = True
            for t in self._filtertags:
                if not first:
                    sql += " OR "
                else:
                    first = False
                sql += "%sTAGS.DATA = %%(%s)s" % (self._prefix, paramname)
        try:
            cursor = self._get_cur()
            cursor.execute(sql, params)

            tags = []
            row = cursor.fetchone()
            while row:
                tag = cPickle.loads(str(row[0]))
                tags.append(tag)
                row = cursor.fetchone()
            return tags
        except pgdb.DatabaseError as e:
            raise DatabaseException("Postgresql: %s" % (e))

    def getnodes(self, ids):
        nodes = []
        idstr = ""
        first = True
        if len(ids) == 0:
            idstr = "-1"

        for i in ids:
            if first:
                idstr += "%d" % (i)
                first = False
            else:
                idstr += ", %d" % (i)

        sql = ("SELECT ID,DATA FROM %sNODES WHERE ID IN (%s)"
               "" % (self._prefix, pgdb.escape_string(idstr)))
        try:
            cursor = self._get_cur()
            cursor.execute(sql)

            row = cursor.fetchone()
            while row:
                node = cPickle.loads(str(row[1]))
                node.set_id(row[0])
                nodes.append(node)
                row = cursor.fetchone()
        except pgdb.DatabaseError as e:
            raise DatabaseException("Postgresql: %s" % (e))
        return nodes

    def editnode(self, id, node):
        if not isinstance(node, Node):
            raise DatabaseException("Tried to insert foreign object into "
                                    "database [%s]" % node)
        try:
            cursor = self._get_cur()
            sql = ("UPDATE %sNODES SET DATA = %%(data)s WHERE ID = %%(id)d"
                   "" % (self._prefix))
            cursor.execute(sql, {"data": cPickle.dumps(node),
                                 "id": id})

        except pgdb.DatabaseError as e:
            raise DatabaseException("Postgresql: %s" % (e))
        self._setnodetags(node)
        self._checktags()
        self._commit()

    def add_node(self, node):
        sql = ("INSERT INTO NODE(USERNAME, PASSWORD, URL, NOTES)"
               "VALUES(%s, %s, %s, %s)")
        node_tags = list(node)
        node, tags = node_tags[:4], node_tags[-1]
        self._cur.execute(sql, (node))
        #self._setnodetags(self._cur.lastrowid, tags)
        self._con.commit()

    def removenodes(self, nodes):
        cursor = self._get_cur()
        for n in nodes:
            if not isinstance(n, Node):
                raise DatabaseException("Tried to delete foreign object"
                                        "from database [%s]", n)
            try:
                sql = "DELETE FROM %sNODES WHERE ID = %%(id)d" % (self._prefix)
                cursor.execute(sql, {"id": n.get_id()})

            except pgdb.DatabaseError as e:
                raise DatabaseException("Postgresql: %s" % (e))
            self._deletenodetags(n)

        self._checktags()
        self._commit()

    def listnodes(self):
        sql = ''
        params = {}
        i = 0
        cursor = self._get_cur()
        if len(self._filtertags) == 0:
            sql = "SELECT ID FROM %sNODES ORDER BY ID ASC" % (self._prefix)
        else:
            first = True
            for t in self._filtertags:
                if not first:
                    sql += " INTERSECT "
                else:
                    first = False
                i += 1
                paramname = "tag%d" % (i)

                sql += (("SELECT NODE FROM %sLOOKUP LEFT JOIN %sTAGS ON"
                         " TAG = %sTAGS.ID"
                         " WHERE %sTAGS.DATA = %%(%s)s ") % (self._prefix,
                                                             self._prefix,
                                                             self._prefix,
                                                             self._prefix,
                                                             paramname))
                params[paramname] = cPickle.dumps(t)
        try:
            cursor.execute(sql, params)

            ids = []
            row = cursor.fetchone()
            while row:
                ids.append(row[0])
                row = cursor.fetchone()
            return ids
        except pgdb.DatabaseError as e:
            raise DatabaseException("Postgresql: %s" % (e))

    def _commit(self):
        try:
            self._con.commit()
        except pgdb.DatabaseError as e:
            self._con.rollback()
            raise DatabaseException(
                "Postgresql: Error commiting data to db [%s]" % (e))

    def _tagids(self, tags):
        ids = []
        cursor = self._get_cur()
        for t in tags:
            pickled = cPickle.dumps(t)
            try:
                ids.append(self._tagidcache[pickled])
                continue
            except KeyError as e:
                pass  # not in cache
            sql = "SELECT ID FROM %sTAGS WHERE DATA = %%(tag)s" % (
                self._prefix)
            if not isinstance(t, Tag):
                raise DatabaseException("Tried to insert foreign object"
                                        " into database [%s]", t)
            data = {"tag": pickled}

            try:
                cursor.execute(sql, data)
                row = cursor.fetchone()
                if row:
                    ids.append(row[0])
                    self._tagidcache[pickled] = row[0]
                else:
                    sql = "INSERT INTO %sTAGS(DATA) VALUES(%%(tag)s)" % (
                        self._prefix)
                    cursor.execute(sql, data)
                    id = self._lastrowid("TAGS")
                    ids.append(id)
                    self._tagidcache[pickled] = id
            except pgdb.DatabaseError as e:
                raise DatabaseException("Postgresql: %s" % (e))
        return ids

    def _deletenodetags(self, node):
        try:
            cursor = self._get_cur()
            sql = "DELETE FROM %sLOOKUP WHERE NODE = %%(node)d" % (
                self._prefix)
            cursor.execute(sql, {"node": node.get_id()})

        except pgdb.DatabaseError as e:
            raise DatabaseException("Postgresql: %s" % (e))

    def _setnodetags(self, node):
        self._deletenodetags(node)
        ids = self._tagids(node.get_tags())

        for i in ids:
            sql = "INSERT INTO %sLOOKUP VALUES(%%(node)d, %%(tag)d)" % (
                self._prefix)
            params = {"node": node.get_id(), "tag": i}

            try:
                cursor = self._get_cur()
                cursor.execute(sql, params)
            except pgdb.DatabaseError as e:
                raise DatabaseException("Postgresql: %s" % (e))

    def _checktags(self):
        self._tagidcache.clear()
        try:
            cursor = self._get_cur()
            sql = ("DELETE FROM %sTAGS WHERE ID NOT IN "
                   + "(SELECT TAG FROM %sLOOKUP GROUP BY TAG)") % (self._prefix,
                                                                   self._prefix)
            cursor.execute(sql)
        except pgdb.DatabaseError as e:
            raise DatabaseException("Postgresql: %s" % (e))
        self._commit()

    def _lastrowid(self, name):
        cursor = self._get_cur()
        cursor.execute("SELECT LAST_VALUE FROM %s%s_ID_SEQ" % (self._prefix,
                                                               name))
        row = cursor.fetchone()
        if not row:
            return 0
        else:
            return row[0]

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
