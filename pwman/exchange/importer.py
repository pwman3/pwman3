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

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import cElementTree as ET

from pwman.data.nodes import Node
from pwman.data.tags import Tag

class Importer:
    def types(self):
        return ["pwman3", "pwman1"]
    types = classmethod(types)
    
    def get(self, type):
        if type == "pwman3":
            return Pwman3Importer()
        if type == "pwman1":
            return Pwman1Importer()
    get = classmethod(get)
        
    def import_data(self, db, file):
        pass

class Pwman1Importer(Importer):
    def __init__(self):
        self.tagstack = []
        self.nodes = []
        
    def parse_list(self, db, list):
        lists = list.findall("PwList")
        for l in lists:
            name = l.get("name").lower().replace(' ', '')
            self.tagstack.append(name)
            self.parse_list(db, l)
            self.tagstack.pop()
        items = list.findall("PwItem")
        tags = []
        for t in self.tagstack:
            tags.append(Tag(t))
            
        for i in items:
            username = i.findtext("user")
            password = i.findtext("passwd")
            url = i.findtext("host")
            notes = "%s | %s" % (i.findtext("name"), i.findtext("launch"))
            n = Node(username, password, url, notes)
            n.set_tags(tags)
            self.nodes.append(n)
            
    def import_data(self, db, file):
        tree = ET.parse(file)
        root = tree.getroot()
        list = root.find("PwList")
        self.parse_list(db, list)
        db.addnodes(self.nodes)

class Pwman3Importer(Importer):
    def import_data(self, db, file):
        tree = ET.parse(file)
        root = tree.getroot()
        nodes = root.findall("Node")
        nodesarray = []
        for n in nodes:
            username = n.findtext("username")
            password = n.findtext("password")
            url = n.findtext("url")
            notes = n.findtext("notes")

            node = Node(username, password, url, notes)
            tagnames = n.find("tags").findall("name")
            tags = []
            for t in tagnames:
                tags.append(Tag(t.text))
            node.set_tags(tags)
            nodesarray.append(node)
        db.addnodes(nodesarray)
            
