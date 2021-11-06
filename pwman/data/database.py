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
# Copyright (C) 2020 Oz N Tiram <oz.tiram@gmail.com>
# ============================================================================
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
# ============================================================================
import binascii
import sqlite3

from pwman.util.crypto_engine import CryptoEngine

__DB_FORMAT__ = 0.7


class DatabaseException(Exception):
    pass  # pragma: no cover


class Database:

    def __init__(self, dburi, sub, **kwargs):

        self.dburi = dburi
        self._cur = None
        self._con = None
        self._sub = sub

    def connect(self, dburi):
        raise NotImplementedError

    def execute(self, query):
        raise NotImplementedError

    def execute_many(self, queries):
        raise NotImplementedError

    def _open(self):
        raise NotImplementedError

    def open(self, dbver=None):
        """
        Open the database, by calling the _open method of the
        class inherited for the specific database.
        When done validation that the file is OK, check if it has
        encryption key, by calling
        enc = CryptoEngine.get()
        key = self.loadkey()
        """
        self._open()
        enc = CryptoEngine.get()
        key = self.loadkey()
        if key is not None:
            enc.set_salt_digest(key)
        else:
            self.get_user_password()

    def _check_tables(self):
        try:
            self._cur.execute("SELECT 1 from DBVERSION")
            version = self._cur.fetchone()
            return version
        except Exception:
            self._con.rollback()
            return 0

    def _create_tables(self):
        if self._check_tables():
            return
        try:
            self._cur.execute("CREATE TABLE NODE(ID SERIAL PRIMARY KEY, "
                              "USERNAME TEXT NOT NULL, "
                              "PASSWORD TEXT NOT NULL, "
                              "URL TEXT NOT NULL, "
                              "NOTES TEXT NOT NULL, "
                              "MDATE TEXT"
                              ")")

            self._cur.execute("CREATE TABLE TAG"
                              "(ID  SERIAL PRIMARY KEY,"
                              "DATA TEXT NOT NULL)")

            self._cur.execute("CREATE TABLE LOOKUP ("
                              "nodeid INTEGER NOT NULL REFERENCES NODE(ID),"
                              "tagid INTEGER NOT NULL REFERENCES TAG(ID)"
                              ")")

            self._cur.execute("CREATE TABLE CRYPTO "
                              "(SEED TEXT, DIGEST TEXT)")

            self._cur.execute("CREATE TABLE DBVERSION("
                              "VERSION TEXT NOT NULL)")

            self._cur.execute("INSERT INTO DBVERSION VALUES(%s)",
                              (self.dbversion,))

            self._con.commit()
        except Exception:  # pragma: no cover
            self._con.rollback()

    def get_user_password(self):
        """
        get the databases password from the user
        """
        enc = CryptoEngine.get()
        newkey = enc.changepassword()
        return self.savekey(newkey)

    def _clean_orphans(self):
        clean = ("delete from TAG where not exists "
                 "(select 'x' from LOOKUP l where l.TAGID = TAG.ID)")
        self._cur.execute(clean)
        self._con.commit()

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
        for row in rv:
            idx, cipher = row["ID"], row["DATA"]
            if encrypted and tag == ce.decrypt(cipher):
                return idx
            elif tag == cipher:
                return idx

    def _get_or_create_tag(self, tagcipher):
        rv = self._get_tag(tagcipher)
        if rv:
            return rv
        else:
            self._cur.execute(self._insert_tag_sql, list(map(self._data_wrapper, (tagcipher,))))  # noqa
            try:
                tid = self._cur.fetchone()
                return tid[0]
            except TypeError:
                return self._cur.lastrowid
            except KeyError:
                return tid["id"]

    def _update_tag_lookup(self, nodeid, tid):
        sql_lookup = "INSERT INTO LOOKUP(nodeid, tagid) VALUES({}, {})".format(
            self._sub, self._sub)
        self._cur.execute(sql_lookup, (nodeid, tid))
        self._con.commit()

    def getnodes(self, ids):
        g = self.lazy_get_nodes(ids)
        for node in g:
            tags = [t for t in self._get_node_tags(node)]
            node.update({"tags": tags})
            yield node

    def get_node(self, id):
        node = next(self.lazy_get_nodes([id]))
        tags = [t for t in self._get_node_tags(node)]
        node.update({"tags": tags})
        return node

    def lazy_get_nodes(self, ids):
        """
        iterates thought ids and yield a node for each id
        """
        query = self._get_node_sql
        for id_ in ids:
            if id_:
                self._cur.execute(query, (str(id_),))
                node = self._cur.fetchone()
                if node:
                    yield dict(node)

    def lazy_list_node_ids_with_filter(self, filter):
        tagid = self._get_tag(filter)
        if not tagid:
            yield []
        else:
            self._cur.execute(self._list_nodes_sql, (tagid,))
            for node in self._cur.fetchall():
                yield node["NODEID"]

    def lazy_list_node_ids(self):
        """return a generator that yields the node ids"""
        sql_all = "SELECT ID FROM NODE"
        self._cur.execute(sql_all)
        for node in self._cur.fetchall():
            v = node["ID"]
            yield v

    def add_node(self, node):
        node_tags = list(node)
        node, tags = node_tags[:4], node_tags[-1]
        try:
            self._cur.execute(self._add_node_sql, list(map(self._data_wrapper, (node))))  # noqa
        except sqlite3.OperationalError:
            updated_query = self._add_node_sql.replace("USER", "USERNAME")
            self._cur.execute(updated_query, list(map(self._data_wrapper, (node))))  # noqa

        self._con.commit()
        nid = self._cur.lastrowid
        self._setnodetags(nid, tags)
        return nid

    def listtags(self):
        self._clean_orphans()
        get_tags = "select DATA from TAG"
        self._cur.execute(get_tags)
        tags = self._cur.fetchall()
        if tags:
            return [t["DATA"] for t in tags]
        return []  # pragma: no cover

    # TODO: add this to test of postgresql and mysql!
    def editnode(self, nid, **kwargs):
        tags = kwargs.pop('tags', None)
        sql = ("UPDATE NODE SET {} WHERE ID = {} ".format(
            ','.join(['{}={}'.format(k, self._sub) for k in list(kwargs)]),
            self._sub))

        try:
            self._cur.execute(sql, (list(kwargs.values()) + [nid]))
        except sqlite3.OperationalError:
            updated_query = sql.replace("USER", "USERNAME")
            updated_query = sql.replace("user", "username")
            self._cur.execute(updated_query, (list(kwargs.values()) + [nid]))

        if tags:
            # update all old node entries in lookup
            # create new entries
            # clean all old tags
            sql_clean = "DELETE FROM LOOKUP WHERE NODEID={}".format(self._sub)
            self._cur.execute(sql_clean, (str(nid),))
            self._setnodetags(nid, tags)

        self._con.commit()

    def removenodes(self, nid):
        # shall we do this also in the sqlite driver?
        sql_clean = "DELETE FROM LOOKUP WHERE NODEID={}".format(self._sub)
        self._cur.execute(sql_clean, nid)
        sql_rm = "delete from NODE where ID = {}".format(self._sub)
        self._cur.execute(sql_rm, nid)
        self._con.commit()
        self._con.commit()

    def fetch_crypto_info(self):
        self._cur.execute("SELECT * FROM CRYPTO")
        row = self._cur.fetchone()
        try:
            return row["SEED"], row["DIGEST"]
        except KeyError: # probably postgresql
            return row["seed"].tobytes(), row["digest"].tobytes()

    def save_crypto_info(self, seed, digest):
        """save the random seed and the digested key"""
        self._cur.execute("DELETE  FROM CRYPTO")
        self._cur.execute("INSERT INTO CRYPTO VALUES({}, {})".format(self._sub,
                                                                     self._sub),  # noqa

                          list(map(self._data_wrapper, (seed, digest))))
        self._con.commit()

    def loadkey(self):
        """
        return _keycrypted
        """
        sql = "SELECT * FROM CRYPTO"
        try:
            self._cur.execute(sql)
            rv = self._cur.fetchone()
            return rv['SEED'] + '$6$' + rv['DIGEST']
        except TypeError:  # pragma: no cover
            return None

    def savekey(self, key):
        salt, digest = key.split('$6$')
        sql = "INSERT INTO CRYPTO(SEED, DIGEST) VALUES({},{})".format(self._sub,  # noqa
                                                                      self._sub)  # noqa
        self._cur.execute("DELETE FROM CRYPTO")
        self._cur.execute(sql, list(map(self._data_wrapper, (salt, digest))))
        self._digest = digest.encode()
        self._salt = salt.encode()
        self._con.commit()

    def close(self):  # pragma: no cover
        self._clean_orphans()
        self._cur.close()
        self._con.close()
