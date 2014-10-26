# ===========================================================================
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
# Copyright (C) 2013, 2014 Oz Nahum Tiram <nahumoz@gmail.com>
# ============================================================================
from __future__ import print_function
from pwman.util.crypto_engine import CryptoEngine, zerome
import re
import sys
import os
import time
import select as uselect
import ast
from pwman.util.config import get_pass_conf
from pwman.ui import tools
from pwman.ui.tools import CliMenuItem
from colorama import Fore
from pwman.data.nodes import NewNode, Node
from pwman.ui.tools import CMDLoop
import getpass
from pwman.data.tags import TagNew
import csv

if sys.version_info.major > 2:
    raw_input = input

from .base import HelpUI


class BaseCommands(HelpUI):

    def do_copy(self, args):
        """copy item to clipboard"""
        pass

    def do_exit(self, args):
        """close the text console"""
        pass

    def do_export(self, args):
        """export the database to a given format"""
        pass

    def do_forget(self, args):
        """drop saved key forcing the user to re-enter the master
        password"""
        pass

    def do_cls(self, args):  # pragma: no cover
        """clear the screen"""
        os.system("clear")

    def do_edit(self, args):
        """edit a node"""
        pass

    def do_clear(self, args):
        """remove db filter"""
        pass

    def do_passwd(self, args):
        """change the master password of the database"""
        pass

    def do_tags(self, args):
        """print all existing tags """
        pass

    def _get_tags(self, default=None, reader=raw_input):
        """
        Tags are simply return as a list
        """
        # TODO: add method to read tags from db, so they
        # could be used for tab completer
        print("Tags: ", end="")
        sys.stdout.flush()
        taglist = sys.stdin.readline()
        tagstrings = taglist.split()
        tags = [tn for tn in tagstrings]
        return tags

    def do_listn(self, args):
        """list all existing nodes in database"""
        self.do_cls('')
        self.do_filter(args)
        nodeids = self._db.listnodes()
        nodes = self._db.getnodes(nodeids)
        _nodes_inst = []
        # user, pass, url, notes
        for node in nodes:
            _nodes_inst.append(Node.from_encrypted_entries(
                node[1],
                'xxxxx',
                node[2],
                'yyyyy',
                []))
        # TOOD: after geting the nodes,
        #       one needs to get their prospective tags
        for node in _nodes_inst:
            print(node)


    def do_filter(self, args):
        pass

    def _get_input(self, prompt):
        print(prompt, end="")
        sys.stdout.flush()
        return sys.stdin.readline()

    def _get_secret(self):
        # TODO: enable old functionallity
        if sys.stdin.isatty():
            p = getpass.getpass()
        else:
            p = sys.stdin.readline().rstrip()
        return p

    def do_new(self, args):
        node = {}
        node['username'] = self._get_input("Username: ")
        node['password'] = self._get_secret()
        node['url'] = self._get_input("Url: ")
        node['notes'] = self._get_input("Notes: ")
        node['tags'] = self._get_tags()
        node = Node(clear_text=True, **node)
        self._db.add_node(node)
        return node
