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
    from xml.etree.cElementTree import Element, SubElement, dump, ElementTree
except ImportError:
    from cElementTree import Element, SubElement, dump, ElementTree

from pwman.data.nodes import Node
from pwman.data.tags import Tag

class Exporter:
    def types(self):
        return ["pwman3"]
    types = classmethod(types)

    def get(self, type):
        if type == "pwman3":
            return Pwman3Exporter()
    get = classmethod(get)

    def export_data(self, db, file, nodeids):
        pass

class Pwman3Exporter(Exporter):
    def export_data(self, db, file, nodeids):
        nodeids = db.listnodes()

        nodes = db.getnodes(nodeids)
        root = Element("PwmanXmlList", version="3.0")
        for n in nodes:
            sub = SubElement(root, "Node")
            SubElement(sub, "username").text = n.get_username()
            SubElement(sub, "password").text = n.get_password()
            SubElement(sub, "url").text = n.get_url()
            SubElement(sub, "notes").text = n.get_notes()
            tagelement = SubElement(sub, "tags")
            for t in n.get_tags():
                SubElement(tagelement, "name").text = t.get_name()

        ElementTree(root).write(file)
