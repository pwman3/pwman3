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
# Copyright (C) 2015 Oz Nahum Tiram <nahumoz@gmail.com>
# ============================================================================

from pwman.data.database import Database, __DB_FORMAT__
import pymongo


class MongoDB(Database):

    @classmethod
    def check_db_version(cls, dburi):
        pass

    def __init__(self, mongodb_uri, dbformat=__DB_FORMAT__):
        self.uri = mongodb_uri

    def _open(self):
        self._con = pymongo.Connection(self.uri)
        self._db = self._con.get_default_database()

        counters = self._db.counters.find()
        if not counters.count():
            self._db.counters.insert({'_id': 'nodeid', 'seq': 0})

    def _get_next_node_id(self):
        # for newer pymongo versions ...
        # return_document=ReturnDocument.AFTER
        nodeid = self._db.counters.find_and_modify(
            {'_id': 'nodeid'}, {'$inc': {'seq': 1}}, new=True,
            fields={'seq': 1, '_id': 0})
        return nodeid['seq']

    def getnodes(self, ids):
        pass

    def listnodes(self, filter=None):
        pass

    def add_node(self, node):
        nid = self._get_next_node_id()
        return nid

    def listtags(self):
        pass

    def editnode(self, nid, **kwargs):
        pass

    def removenodes(self, nid):
        pass

    def fetch_crypto_info(self):
        pass

    def savekey(self, key):
        coll = self._db['crypto']
        salt, digest = key.split('$6$')
        coll.insert({'salt': salt, 'key': digest})

    def loadkey(self):
        coll = self._db['crypto']
        key = coll.find_one({}, {'_id': 0})
        key = key['salt'] + '$6$' + key['key']
        return key

    def close(self):
        pass
