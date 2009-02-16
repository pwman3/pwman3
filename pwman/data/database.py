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
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
#============================================================================

from pwman.data.nodes import Node
from pwman.util.crypto import CryptoEngine


class DatabaseException(Exception):
    pass

class Database:
    def __init__(self):
        self._filtertags = []

    def open(self):
        """Open the database."""
        self._open()

        enc = CryptoEngine.get()
        key = self.loadkey()
        if (key != None):
            enc.set_cryptedkey(key)
        else:
            self.changepassword()

    def close(self):
        pass

    def changepassword(self):
        """Change the databases password."""
        enc = CryptoEngine.get()
        newkey = enc.changepassword()
        return self.savekey(newkey)
    
    def listtags(self, all=False):
        pass

    def currenttags(self):
        return self._filtertags
    
    def filter(self, tags):
        for t in tags:
            if not (t in self._filtertags):
                self._filtertags.append(t)

    def clearfilter(self):
        self._filtertags = []

    def getnodes(self, ids):
        pass
    
    def addnodes(self, nodes):
        pass

    def editnode(self, id, node):
        pass

    def removenodes(self, nodes):
        pass

    def listnodes(self):
        pass

    def savekey(self, key):
        pass

    def loadkey(self):
        pass
    
