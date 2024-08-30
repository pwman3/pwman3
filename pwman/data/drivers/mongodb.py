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
from pwman.util.crypto_engine import CryptoEngine

import pymongo


class MongoDB(Database):

    @classmethod
    def check_db_version(cls, dburi):
        return __DB_FORMAT__

    def __init__(self, mongodb_uri, dbformat=__DB_FORMAT__):
        self.uri = mongodb_uri.geturl()

    def _open(self):
        self._con = pymongo.MongoClient(self.uri)
        self._db = self._con.get_default_database()

        counters = self._db.counters.count_documents({})
        if not counters:
            self._db.counters.insert_one({'_id': 'nodeid', 'seq': 0})

    def _get_next_node_id(self):
        # for newer pymongo versions ...
        # return_document=ReturnDocument.AFTER
        nodeid = self._db.counters.find_one_and_update(
            {'_id': 'nodeid'}, {'$inc': {'seq': 1}}, new=True,
            fields={'seq': 1, '_id': 0})
        return nodeid['seq']

    def getnodes(self, ids):
        if ids:
            ids = list(map(int, ids))
            node_dicts = self._db.nodes.find({'_id': {'$in': ids}})
        else:
            node_dicts = self._db.nodes.find({})
        nodes = []
        for node in node_dicts:
            n = [node['_id'],
                 node['username'],
                 node['password'],
                 node['url'],
                 node['notes']]

            [n.append(t) for t in node['tags']]
            nodes.append(n)

        return nodes

    def listnodes(self, filter_=None):
        if not filter_:
            nodes = self._db.nodes.find({}, {'_id': 1})
            return [node["_id"] for node in nodes]
        else:
            matching = []
            ce = CryptoEngine.get()
            nodes = list(self._db.nodes.find({}, {'_id': 1, 'tags': 1}))
            for node in nodes:
                node['tags'] = [ce.decrypt(t) for t in node['tags']]
                if filter_ in node['tags']:
                    matching.append(node)
            return [node["_id"] for node in matching]

    def add_node(self, node):
        nid = self._get_next_node_id()
        node = node.to_encdict()
        node['_id'] = nid
        self._db.nodes.insert_one(node)
        return nid

    def listtags(self):
        tags = self._db.nodes.distinct('tags')
        return tags

    def editnode(self, nid, **kwargs):
        self._db.nodes.find_one_and_update({'_id': nid}, kwargs)

    def removenodes(self, nid):
        nid = list(map(int, nid))
        self._db.nodes.delete_one({'_id': {'$in': nid}})

    def fetch_crypto_info(self):
        pass

    def savekey(self, key):
        coll = self._db['crypto']
        salt, digest = key.split('$6$')
        coll.insert_one({'salt': salt, 'key': digest})

    def loadkey(self):
        coll = self._db['crypto']
        try:
            key = coll.find_one({}, {'_id': 0})
            key = key['salt'] + '$6$' + key['key']
        except TypeError:
            key = None
        return key

    def close(self):
        self._con.close()
