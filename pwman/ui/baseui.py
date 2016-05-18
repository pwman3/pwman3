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
import ast
import csv
import time
import re
import select as uselect
from colorama import Fore
from pwman.data.nodes import Node
from pwman.ui import tools
from pwman.util.crypto_engine import CryptoEngine
from pwman.util.crypto_engine import zerome
from pwman.ui.tools import CliMenuItem
from pwman.ui.tools import CMDLoop, get_or_create_pass


if sys.version_info.major > 2:  # pragma: no cover
    raw_input = input


def _heard_enter():  # pragma: no cover
    i, o, e = uselect.select([sys.stdin], [], [], 0.0001)
    for s in i:
        if s == sys.stdin:
            sys.stdin.readline()
            return True
        return False


def _wait_until_enter(predicate, timeout, period=0.25):  # pragma: no cover
    mustend = time.time() + timeout
    while time.time() < mustend:
        cond = predicate()
        if cond:
            break
        time.sleep(period)


class HelpUIMixin(object):  # pragma: no cover

    """
    this class holds all the UI help functionality.
    in PwmanCliNew. The later inherits from this class
    and allows it to print help messages to the console.
    """

    def _usage(self, string):
        print ("Usage: %s" % (string))

    def help_open(self):
        self._usage("open|o <ID>")
        print ("Launch default browser with 'xdg-open url',\n",
               "the url must contain http:// or https://.")

    def help_copy(self):
        self._usage("copy|cp <ID>")
        print ("Copy password to X clipboard (xsel required)")

    def help_cls(self):
        self._usage("cls")
        print ("Clear the Screen from information.")

    def help_list(self):
        self._usage("list|ls <tag> ...")
        print ("List nodes that match current or specified filter.",
               " ls is an alias.")

    def help_delete(self):
        self._usage("delete|rm <ID|tag> ...")
        print ("Deletes nodes.")
        self._mult_id_help()

    def help_help(self):
        self._usage("help|h [topic]")
        print ("Prints a help message for a command.")

    def help_edit(self):
        self._usage("edit <ID|tag> ... ")
        print ("Edits a nodes.")

    def help_export(self):
        self._usage("export [{'filename': 'foo.csv', 'delimiter':'|'}] ")
        print("All nodes under the current filter are exported.")

    def help_new(self):
        self._usage("new")
        print ("Creates a new node.,",
               "You can override default config settings the following way:\n",
               "pwman> n {'leetify':False, 'numerics':True}")

    def help_print(self):
        self._usage("print <ID|tag> ...")
        print ("Displays a node. ")
        self._mult_id_help()

    def _mult_id_help(self):
        print("Multiple ids and nodes can be specified, separated by a space.",
              " A range of ids can be specified in the format n-N. e.g. ",
              " '10-20' would specify all nodes having ids from 10 to 20 ",
              " inclusive. Tags are considered one-by-one. e.g. 'foo 2 bar'",
              " would yield to all nodes with tag 'foo', node 2 and all ",
              " nodes with tag 'bar'.")

    def help_exit(self):
        self._usage("exit|EOF")
        print("Exits the application.")

    def help_passwd(self):
        self._usage("passwd")
        print("Changes the password on the database. ")

    def help_forget(self):
        self._usage("forget")
        print("Forgets the database password. Your password will need to ",
              "be reentered before accessing the database again.")

    def help_tags(self):
        self._usage("tags")
        print("Displays all tags in used in the database.")

    def help_info(self):
        print("Show information about the current database.")


class AliasesMixin(object):  # pragma: no cover

    """
    Define all the alias you want here...
    """

    def do_cp(self, args):
        self.do_copy(args)

    def do_EOF(self, args):  # pragma: no cover
        self.do_exit(args)

    def do_ls(self, args):
        self.do_list(args)

    def do_p(self, arg):
        self.do_print(arg)

    def do_rm(self, arg):
        self.do_delete(arg)

    def do_o(self, args):
        self.do_open(args)

    def do_e(self, args):
        self.do_edit(args)

    def do_h(self, arg):
        self.do_help(arg)

    def do_n(self, arg):
        self.do_new(arg)


class BaseCommands(HelpUIMixin, AliasesMixin):

    @property
    def _xsel(self):  # pragma: no cover
        if self.hasxsel:
            return True

    def do_EOF(self, args):
        return self.do_exit(args)

    def _get_ids(self, args):
        """
        Command can get a single ID or
        a range of IDs, with begin-end.
        e.g. 1-3 , will get 1 to 3.
        """
        ids = []
        rex = re.compile("^(?P<begin>\d+)(?:-(?P<end>\d+))?$")
        rex = rex.match(args)
        if hasattr(rex, 'groupdict'):
            try:
                begin = int(rex.groupdict()['begin'])
                end = int(rex.groupdict()['end'])
                if not end > begin:
                    print("Start node should be smaller than end node")
                    return ids
                ids += range(begin, end + 1)
                return ids
            except TypeError:
                ids.append(int(begin))
        else:
            print("Could not understand your input...")
        return ids

    def error(self, exception):  # pragma: no cover
        if (isinstance(exception, KeyboardInterrupt)):
            print('')
        else:
            print("Error: {0} ".format(exception))

    def do_copy(self, args):  # pragma: no cover
        """copy item to clipboard"""
        if not self.hasxsel:
            return
        if not args.isdigit():
            print("Copy accepts only IDs ...")
            return
        ids = args.split()
        if len(ids) > 1:
            print("Can copy only 1 password at a time...")
            return

        ce = CryptoEngine.get()
        nodes = self._db.getnodes(ids)

        for node in nodes:
            password = ce.decrypt(node[2])
            tools.text_to_clipboards(password)
            flushtimeout = self.config.get_value('Global', 'cp_timeout')
            flushtimeout = flushtimeout or 10
            print("erasing in {} sec...".format(flushtimeout))
            time.sleep(int(flushtimeout))
            tools.text_to_clipboards("")

    def do_open(self, args):  # pragma: no cover
        ids = self._get_ids(args)
        if not args:
            self.help_open()
            return

        nodes = self._db.getnodes(ids)
        ce = CryptoEngine.get()

        for node in nodes:
            url = ce.decrypt(node[3])
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            os.umask(22)
            tools.open_url(url)

            umask = self.config.get_value("Global", "umask")
            if re.search(r'^\d{4}$', umask):
                os.umask(int(umask))

    def do_exit(self, args):  # pragma: no cover
        """close the text console"""
        self._db.close()
        return True

    def do_cls(self, args):  # pragma: no cover
        """clear the screen"""
        os.system("clear")

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
                tags = ','.join(t.strip() for t in tags)
                r = list([n.username, n.url, n.password, n.notes])
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

        return rows, cols

    def _format_line(self, tag_pad, nid="ID", user="USER", url="URL",
                     tags="TAGS"):
        return ("{ID:<3} {USER:<{us}}{URL:<{ur}}{Tags:<{tg}}"
                "".format(ID=nid, USER=user,
                          URL=url, Tags=tags, us=25,
                          ur=25, tg=20))

    def _print_node_line(self, node, rows, cols):
        tagstring = ','.join([t for t in node.tags])
        fmt = self._format_line(cols, node._id, node.username,
                                node.url[:20] + '...' if (len(node.url) > 22)
                                else node.url,
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

    def do_edit(self, args, menu=None):
        ids = self._get_ids(args)
        for i in ids:
            i = int(i)
            node = self._db.getnodes([i])
            if not node:
                print("Node not found ...")
                return
            node = node[0]
            node = node[1:5] + [node[5:]]
            node = Node.from_encrypted_entries(*node)
            if not menu:
                menu = CMDLoop(self.config)
                print ("Editing node %d." % (i))
                menu.add(CliMenuItem("Username", node.username))
                menu.add(CliMenuItem("Password",  node.password))
                menu.add(CliMenuItem("Url", node.url))
                menunotes = CliMenuItem("Notes", node.notes)
                menu.add(menunotes)
                menu.add(CliMenuItem("Tags", ','.join(node.tags)))
            menu.run(node)
            self._db.editnode(i, **node.to_encdict())
            # when done with node erase it
            zerome(node._password)

    def do_list(self, args):
        """
        list all existing nodes in database
        """
        rows, cols = self._prep_term()
        nodeids = self._get_node_ids(args)
        raw_nodes = self._db.getnodes(nodeids)
        _nodes_inst = self._db_entries_to_nodes(raw_nodes)
        head = self._format_line(cols - 32)
        print(tools.typeset(head, Fore.YELLOW, False))
        for idx, node in enumerate(_nodes_inst):
            self._print_node_line(node, rows, cols)

    def _get_input(self, prompt):
        print(prompt, end="")
        sys.stdout.flush()
        return sys.stdin.readline().strip()

    def _get_secret(self):
        if sys.stdin.isatty():  # pragma: no cover
            p = get_or_create_pass()
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
        if not nodes:  # pragma: no cover
            print("Node not found ...")
            return

        node = self._db_entries_to_nodes(nodes)[0]
        print(node)
        flushtimeout = self.config.get_value('Global', 'cls_timeout')
        flushtimeout = flushtimeout or 10

        print("Type Enter to flush screen or wait %s sec. " % flushtimeout)

        _wait_until_enter(_heard_enter, float(flushtimeout))
        self.do_cls('')

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

    def do_info(self, args):
        print("Currently connected to: {}".format(
              self.config.get_value("Database", "dburi")))
