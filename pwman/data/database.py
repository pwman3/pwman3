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
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
#============================================================================

from pwman.util.crypto import CryptoEngine


class DatabaseException(Exception):
    pass  # prage: no cover


class Database(object):

    def __init__(self):
        self._filtertags = []

    def open(self):
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
            enc.set_cryptedkey(key)
        else:
            self.get_user_password()

    def close(self):
        pass  # pragma: no cover

    def get_user_password(self):
        """
        get the databases password from the user
        """
        enc = CryptoEngine.get()
        newkey = enc.changepassword()
        return self.savekey(newkey)

    def changepassword(self):
        """
        Change the databases password.
        """
        enc = CryptoEngine.get()
        newkey = enc.changepassword()
        return newkey
        #  self.savekey(newkey)

    def listtags(self, all=False):
        pass  # pragma: no cover

    def currenttags(self):
        return self._filtertags

    def filter(self, tags):
        for tag in tags:
            if not (tag in self._filtertags):
                self._filtertags.append(tag)

    def clearfilter(self):
        self._filtertags = []

    def getnodes(self, ids):
        pass  # pragma: no cover

    def addnodes(self, nodes):
        pass  # pragma: no cover

    def editnode(self, id, node):
        pass  # pragma: no cover

    def removenodes(self, nodes):
        pass  # pragma: no cover

    def listnodes(self):
        pass  # pragma: no cover

    def savekey(self, key):
        pass  # pragma: no cover

    def loadkey(self):
        pass  # pragma: no cover
