#============================================================================
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
#============================================================================
# Copyright (C) 2012 Oz Nahum <nahumoz@gmail.com>
#============================================================================
#============================================================================
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
#============================================================================

"""Postgresql Database implementation."""
from pwman.data.database import Database, DatabaseException
from pwman.data.nodes import Node
from pwman.data.tags import Tag

import pgdb
import pwman.util.config as config
import cPickle

class PostgresqlDatabase(Database):
    """Postgresql Database implementation"""
    
    def __init__(self):
        """Initialise PostgresqlDatabase instance."""
        Database.__init__(self)

        self._tagidcache = {}
        
        config.add_defaults({"Database" : {"server": "localhost",
                                           "port"  : "5432",
                                           "database" : "pwman",
                                           "table_prefix" : "pwman_"}})
        try:
            self._server = config.get_value('Database', 'server')
            self._port = config.get_value('Database', 'port')
            self._user = config.get_value('Database', 'user')
            self._password = config.get_value('Database', 'password')
            self._database = config.get_value('Database', 'database')
            self._prefix = config.get_value('Database', 'table_prefix')
        except KeyError, e:
            raise DatabaseException(
                "Postgresql: missing parameter [%s]" % (e))

    def _open(self):
        try:
            self._con = None
#            server = "%s:%s" % (self._server, self._port)
#            self._con = pgdb.connect(host = server,
#                                     database = self._database,
#                                     user = self._user,
#                                     password = self._password)
#            self._cur = self._con.cursor()
            self._checktables()
        except pgdb.DatabaseError, e:
            raise DatabaseException("Postgresql: %s" % (e))

    def _get_cur(self):
        try:
            if (self._con != None):
                return self._con.cursor()
        except pgdb.DatabaseError, e:
            pass
        server = "%s:%s" % (self._server, self._port)
        self._con = pgdb.connect(host = server,
                                 database = self._database,
                                 user = self._user,
                                 password = self._password)
        self._cur = self._con.cursor()
        return self._cur

    def close(self):
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
                   +" INNER JOIN %sTAGS ON %sLOOKUP.TAG = %sTAGS.ID"
                   +" WHERE NODE IN (") % (self._prefix, self._prefix, self._prefix,
                                           self._prefix, self._prefix)
            first = True

            i += 1
            paramname = "tag%d" % (i)
            for t in self._filtertags:
                if not first:
                    sql += " INTERSECT "
                else:
                    first = False
                
                sql += ("SELECT NODE FROM %sLOOKUP LEFT JOIN %sTAGS ON TAG = %sTAGS.ID "
                        + " WHERE %sTAGS.DATA = %%(%s)s") % (self._prefix, self._prefix,
                                                             self._prefix, self._prefix,
                                                             paramname)
                params[paramname] = cPickle.dumps(t)
            sql += ") EXCEPT SELECT DATA FROM %sTAGS WHERE " %(self._prefix)
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
            while (row != None):
                tag = cPickle.loads(str(row[0]))
                tags.append(tag)
                row = cursor.fetchone()
            return tags
        except pgdb.DatabaseError, e:
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
            
        sql = "SELECT ID,DATA FROM %sNODES WHERE ID IN (%s)" % (self._prefix,
                                                                pgdb.escape_string(idstr))
        try:
            cursor = self._get_cur()
            cursor.execute(sql)
            
            row = cursor.fetchone()
            while row != None:
                node = cPickle.loads(str(row[1]))
                node.set_id(row[0])
                nodes.append(node)
                row = cursor.fetchone()
        except pgdb.DatabaseError, e:
            raise DatabaseException("Postgresql: %s" % (e))
        return nodes

    def editnode(self, id, node):
        if not isinstance(node, Node): raise DatabaseException(
                "Tried to insert foreign object into database [%s]" % node)
        try:
            cursor = self._get_cur()
            sql = "UPDATE %sNODES SET DATA = %%(data)s WHERE ID = %%(id)d" % (self._prefix)
            cursor.execute(sql, {"data":cPickle.dumps(node),
                                 "id": id})
            
        except pgdb.DatabaseError, e:
            raise DatabaseException("Postgresql: %s" % (e))
        self._setnodetags(node)
        self._checktags()
        self._commit()

    def addnodes(self, nodes):
        cursor = self._get_cur()
        for n in nodes:
            sql = "INSERT INTO %sNODES(DATA) VALUES(%%(data)s)" % (self._prefix)
            if not isinstance(n, Node): raise DatabaseException(
                "Tried to insert foreign object into database [%s]", n)
            values = {"data": cPickle.dumps(n)}
            try:
                cursor.execute(sql, values)
            except pgdb.DatabaseError, e:
                raise DatabaseException("Postgresql: %s" % (e))
            id = self._lastrowid("NODES")
            n.set_id(id)

            self._setnodetags(n)
        self._commit()
            
    def removenodes(self, nodes):
        cursor = self._get_cur()
        for n in nodes:
            if not isinstance(n, Node): raise DatabaseException(
                "Tried to delete foreign object from database [%s]", n)
            try:
                sql = "DELETE FROM %sNODES WHERE ID = %%(id)d" % (self._prefix)
                cursor.execute(sql, {"id": n.get_id()})
                
            except pgdb.DatabaseError, e:
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

                sql += (("SELECT NODE FROM %sLOOKUP LEFT JOIN %sTAGS ON TAG = %sTAGS.ID"
                         + " WHERE %sTAGS.DATA = %%(%s)s ") % (self._prefix, self._prefix,
                                                               self._prefix, self._prefix,
                                                               paramname))
                params[paramname] = cPickle.dumps(t)
        try:
            cursor.execute(sql, params)

            ids = []
            row = cursor.fetchone()
            while (row != None):
                ids.append(row[0])
                row = cursor.fetchone()
            return ids
        except pgdb.DatabaseError, e:
            raise DatabaseException("Postgresql: %s" % (e))

    def _commit(self):
        try:
            self._con.commit()
        except pgdb.DatabaseError, e:
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
            except KeyError, e:
                pass # not in cache
            sql = "SELECT ID FROM %sTAGS WHERE DATA = %%(tag)s" % (self._prefix)
            if not isinstance(t, Tag): raise DatabaseException(
                "Tried to insert foreign object into database [%s]", t)
            data = {"tag" : pickled }
            
            try:
                cursor.execute(sql, data)
                row = cursor.fetchone()
                if (row != None):
                    ids.append(row[0])
                    self._tagidcache[pickled] = row[0]
                else:
                    sql = "INSERT INTO %sTAGS(DATA) VALUES(%%(tag)s)" % (self._prefix)
                    cursor.execute(sql, data)
                    id = self._lastrowid("TAGS")
                    ids.append(id)
                    self._tagidcache[pickled] = id
            except pgdb.DatabaseError, e:
                raise DatabaseException("Postgresql: %s" % (e))
        return ids

    def _deletenodetags(self, node):
        try:
            cursor = self._get_cur()
            sql = "DELETE FROM %sLOOKUP WHERE NODE = %%(node)d" % (self._prefix)
            cursor.execute(sql, {"node":node.get_id()})
            
        except pgdb.DatabaseError, e:
            raise DatabaseException("Postgresql: %s" % (e))
        
    def _setnodetags(self, node):
        self._deletenodetags(node)
        ids = self._tagids(node.get_tags())
        
        for i in ids:
            sql = "INSERT INTO %sLOOKUP VALUES(%%(node)d, %%(tag)d)" % (self._prefix)
            params = {"node": node.get_id(), "tag": i}
            
            try:
                cursor = self._get_cur()
                cursor.execute(sql, params)
            except pgdb.DatabaseError, e:
                raise DatabaseException("Postgresql: %s" % (e))

    def _checktags(self):
        self._tagidcache.clear()
        try:
            cursor = self._get_cur()
            sql = ("DELETE FROM %sTAGS WHERE ID NOT IN "
                   + "(SELECT TAG FROM %sLOOKUP GROUP BY TAG)") % (self._prefix,
                                                                   self._prefix)
            cursor.execute(sql)
        except pgdb.DatabaseError, e:
            raise DatabaseException("Postgresql: %s" % (e))
        self._commit()

    def _lastrowid(self, name):
        cursor = self._get_cur()
        cursor.execute("SELECT LAST_VALUE FROM %s%s_ID_SEQ" % (self._prefix, name))
        row = cursor.fetchone()
        if row == None:
            return 0;
        else:
            return row[0]
        
    def _checktables(self):
        """ Check if the Pwman tables exist """
        cursor = self._get_cur()
        cursor.execute(
            "SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '%snodes'"
            % (self._prefix))

        if (cursor.fetchone() == None):
            # table doesn't exist, create it
            cursor.execute(("CREATE TABLE %sNODES" 
                               +"(ID SERIAL PRIMARY KEY, DATA TEXT NOT NULL)")
                              % (self._prefix))
            cursor.execute(("CREATE TABLE %sTAGS"
                               + "(ID SERIAL PRIMARY KEY,"
                               + "DATA TEXT NOT NULL UNIQUE)")
                              % (self._prefix))
            cursor.execute(("CREATE TABLE %sLOOKUP"
                               + "(NODE INTEGER NOT NULL, TAG INTEGER NOT NULL,"
                               + " PRIMARY KEY(NODE, TAG))")
                              % (self._prefix))

            cursor.execute(("CREATE TABLE %sKEY"
                               + "(THEKEY TEXT NOT NULL DEFAULT '')")
                              % (self._prefix));
            cursor.execute("INSERT INTO %sKEY VALUES('')" % (self._prefix));
            
            try:
                self._con.commit()
            except pgdb.DatabaseError, e:
                self._con.rollback()
                raise e

    def savekey(self, key):
        sql = "UPDATE %sKEY SET THEKEY = %%(key)s" % (self._prefix)
        values = {"key": key}
        cursor = self._get_cur()
        cursor.execute(sql, values)
        try:
            self._con.commit()
        except pgdb.DatabaseError, e:
            self._con.rollback()
            raise DatabaseException(
                "Postgresql: Error saving key [%s]" % (e))
        
        
    def loadkey(self):
        cursor = self._get_cur()
        cursor.execute("SELECT THEKEY FROM %sKEY" % (self._prefix));
        keyrow = cursor.fetchone()
        if (keyrow[0] == ''):
            return None
        else:
            return keyrow[0]
