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
# Copyright (C) 2013 Oz Nahum <nahumoz@gmail.com>
#============================================================================

import os
import shutil
import os.path
import time
import getpass
from pwman.util.crypto import CryptoEngine
import pwman.data.factory
from pwman.util.callback import Callback
from pwman.data.nodes import NewNode
import sys

_NEWVERSION = 0.4


class CLICallback(Callback):
    def getinput(self, question):
        return raw_input(question)

    def getsecret(self, question):
        return getpass.getpass(question + ":")


class PwmanConvertDB(object):
    """
    Class to migrate from DB in version 0.3 to
    DB used in later versions.
    """

    def __init__(self, args, config):
        self.dbname = config.get_value('Database', 'filename')
        self.dbtype = config.get_value("Database", "type")
        print "Will convert the following Database: %s " % self.dbname
        if os.path.exists(config.get_value("Database", "filename")):
            dbver = pwman.data.factory.check_db_version(self.dbtype)
            self.dbver = float(dbver.strip("\'"))
        backup = '.backup-%s'.join(os.path.splitext(self.dbname)) % \
            time.strftime(
                '%Y-%m-%d-%H:%M')
        shutil.copy(self.dbname, backup)
        print "backup created in ", backup

    def read_old_db(self):
        "read the old db and get all nodes"
        self.db = pwman.data.factory.create(self.dbtype, self.dbver)
        enc = CryptoEngine.get()
        enc.set_callback(CLICallback())
        self.db.open()
        self.oldnodes = self.db.listnodes()
        self.oldnodes = self.db.getnodes(self.oldnodes)

    def create_new_db(self):
        dest = '-newdb'.join(os.path.splitext(self.dbname))
        if os.path.exists('-newdb'.join(os.path.splitext(self.dbname))):
            print "%s already exists, please move this file!" % dest
            sys.exit(2)

        self.newdb_name = '-newdb'.join(os.path.splitext(self.dbname))

        self.newdb = pwman.data.factory.create(self.dbtype, _NEWVERSION,
                                               self.newdb_name)
        self.newdb._open()

    def convert_nodes(self):
        """convert old nodes instances to new format"""
        self.NewNodes = []
        for node in self.oldnodes:
            username = node.get_username()
            password = node.get_password()
            url = node.get_url()
            notes = node.get_notes()
            tags = node.get_tags()
            tags_strings = [tag.get_name() for tag in tags]
            newNode = NewNode(username=username,
                              password=password,
                              url=url,
                              notes=notes,
                              tags=tags_strings
                              )
            self.NewNodes.append(newNode)

    def save_new_nodes_to_db(self):
        self.newdb.addnodes(self.NewNodes)
        self.newdb._commit()

    def save_old_key(self):
        enc = CryptoEngine.get()
        self.oldkey = enc.get_cryptedkey()
        self.newdb.savekey(self.oldkey)

    def print_success(self):
        print """pwman successfully converted the old database to the new
format.\nPlease run `pwman3 -d %s` to make sure your password and
data are still correct. If you are convinced that no harm was done,
update your config file to indicate the permanent location
to your new database.
If you found errors, please report a bug in Pwman homepage in github.
""" % self.newdb_name

    def run(self):
        self.read_old_db()
        self.create_new_db()
        self.convert_nodes()
        self.save_new_nodes_to_db()
        self.save_old_key()
        self.print_success()
