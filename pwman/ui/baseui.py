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
import sys
import os
import getpass
import ast
import csv
import time
from colorama import Fore
from pwman.data.nodes import Node
from pwman.ui import tools
from pwman.util.crypto_engine import CryptoEngine
from .base import HelpUIMixin, AliasesMixin

if sys.version_info.major > 2:  # pragma: no cover
    raw_input = input


class BaseCommands(HelpUIMixin, AliasesMixin):

    @property
    def _xsel(self):
        if self.hasxsel:
            return True

    def error(self, exception):  # pragma: no cover
        if (isinstance(exception, KeyboardInterrupt)):
            print('')
        else:
            print("Error: {0} ".format(exception))

    def do_copy(self, args):  # pragma: no cover
        """copy item to clipboard"""
        if not self._xsel:
            return
        if not args.isdigit():
            print("Copy accepts only IDs ...")
            return

        ids = args.split()
        if len(ids) > 1:
            print("Can copy only 1 password at a time...")
            return

        nodes = self._db.getnodes(ids)
        for node in nodes:
            ce = CryptoEngine.get()
            password = ce.decrypt(node[2])
            tools.text_to_clipboards(password)
            print("erasing in 10 sec...")
            time.sleep(10)  # TODO: this should be configurable!
            tools.text_to_clipboards("")

    def do_open(self, args):  # pragma: no cover
        ids = self.get_ids(args)
        if not args:
            self.help_open()
            return

        nodes = self._db.getnodes(ids)
        for node in nodes:
            ce = CryptoEngine.get()
            url = ce.decrypt(node[3])
            tools.open_url(url)

    def do_exit(self, args):  # pragma: no cover
        """close the text console"""
        self._db.close()
        return True

    def do_cls(self, args):  # pragma: no cover
        """clear the screen"""
        os.system("clear")

    def do_edit(self, args):
        """edit a node"""
        pass

    def do_export(self, args):
        """export the database to a given format"""
        try:
            args = ast.literal_eval(args)
        except Exception:
            args = {}

        filename = args.get('filename', 'pwman-export.csv')
        delim = args.get('delimiter', ';')
        nodeids = self._db.listnodes()
        nodes = self._db.getnodes(nodeids)
        with open(filename, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=delim)
            writer.writerow(['Username', 'URL', 'Password', 'Notes',
                             'Tags'])
            for node in nodes:
                n = Node.from_encrypted_entries(node[1], node[2], node[3],
                                                node[4],
                                                node[5:])
                tags = n.tags
                tags = ','.join(t.strip().decode() for t in tags)
                r = list(map(bytes.decode, [n.username, n.url, n.password,
                                            n.notes]))
                writer.writerow(r + [tags])

        print("Successfuly exported database to {}".format(
            os.path.join(os.getcwd(), filename)))

    def do_forget(self, args):
        """
        drop saved key forcing the user to re-enter the master
        password
        """
        enc = CryptoEngine.get()
        enc.forget()

    def do_passwd(self, args):  # pragma: no cover
        """change the master password of the database"""
        pass

    def do_tags(self, args):
        """
        print all existing tags
        """
        ce = CryptoEngine.get()
        print("Tags:")
        tags = self._db.listtags()
        for t in tags:
            print(ce.decrypt(t).decode())

    def _get_tags(self, default=None, reader=raw_input):
        """
        Read tags from user input.
        Tags are simply returned as a list
        """
        # TODO: add method to read tags from db, so they
        # could be used for tab completer
        print("Tags: ", end="")
        sys.stdout.flush()
        taglist = sys.stdin.readline()
        tagstrings = taglist.split()
        tags = [tn for tn in tagstrings]
        return tags

    def _prep_term(self):
        self.do_cls('')
        if sys.platform != 'win32':
            rows, cols = tools.gettermsize()
        else:  # pragma: no cover
            rows, cols = 18, 80  # fix this !

        cols -= 8
        return rows, cols

    def _format_line(self, tag_pad, nid="ID", user="USER", url="URL",
                     tags="TAGS"):
        return ("{ID:<3} {USER:<{us}}{URL:<{ur}}{Tags:<{tg}}"
                "".format(ID=nid, USER=user,
                          URL=url, Tags=tags, us=12,
                          ur=20, tg=tag_pad - 32))

    def _print_node_line(self, node, rows, cols):
        tagstring = ','.join([t.decode() for t in node.tags])
        fmt = self._format_line(cols - 32, node._id, node.username.decode(),
                                node.url.decode(),
                                tagstring)
        formatted_entry = tools.typeset(fmt, Fore.YELLOW, False)
        print(formatted_entry)

    def _get_node_ids(self, args):
        filter = None
        if args:
            filter = args.split()[0]
            ce = CryptoEngine.get()
            filter = ce.encrypt(filter)
        nodeids = self._db.listnodes(filter=filter)
        return nodeids

    def _db_entries_to_nodes(self, raw_nodes):
        _nodes_inst = []
        # user, pass, url, notes
        for node in raw_nodes:
            _nodes_inst.append(Node.from_encrypted_entries(
                node[1],
                node[2],
                node[3],
                node[4],
                node[5:]))
            _nodes_inst[-1]._id = node[0]
        return _nodes_inst

    def do_list(self, args):
        """list all existing nodes in database"""
        rows, cols = self._prep_term()
        nodeids = self._get_node_ids(args)
        raw_nodes = self._db.getnodes(nodeids)
        _nodes_inst = self._db_entries_to_nodes(raw_nodes)
        head = self._format_line(cols-32)
        print(tools.typeset(head, Fore.YELLOW, False))
        for idx, node in enumerate(_nodes_inst):
            self._print_node_line(node, rows, cols)

    def _get_input(self, prompt):
        print(prompt, end="")
        sys.stdout.flush()
        return sys.stdin.readline().strip()

    def _get_secret(self):
        # TODO: enable old functionallity, with password generator.
        if sys.stdin.isatty():  # pragma: no cover
            p = getpass.getpass()
        else:
            p = sys.stdin.readline().rstrip()
        return p

    def _do_new(self, args):
        node = {}
        node['username'] = self._get_input("Username: ")
        node['password'] = self._get_secret()
        node['url'] = self._get_input("Url: ")
        node['notes'] = self._get_input("Notes: ")
        node['tags'] = self._get_tags()
        node = Node(clear_text=True, **node)
        self._db.add_node(node)
        return node

    def do_new(self, args):  # pragma: no cover
        # The cmd module stops if and of do_* return something
        # else than None ...
        # This is bad for testing, so everything that is do_*
        # should call _do_* method which is testable
        self._do_new(args)

    def do_print(self, args):
        if not args.isdigit():
            print("print accepts only a single ID ...")
            return
        nodes = self._db.getnodes([args])
        node = self._db_entries_to_nodes(nodes)[0]
        print(node)

    def _do_rm(self, args):
        for i in args.split():
            if not i.isdigit():
                print("%s is not a node ID" % i)
                return None

        for i in args.split():
            ans = tools.getinput(("Are you sure you want to delete node {}"
                                  " [y/N]?".format(i)))
            if ans.lower() == 'y':
                self._db.removenodes([i])

    def do_delete(self, args):  # pragma: no cover
        CryptoEngine.get()
        self._do_rm(args)
