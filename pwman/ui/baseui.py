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
# Copyright (C) 2013-2017 Oz Nahum Tiram <oz.tiram@gmail.com>
# ============================================================================
import ast
import csv
import datetime
import os
import re
import select as uselect
import shutil
import sys
import time

from colorama import Fore
from pwman.data.nodes import Node
from pwman.ui import tools
from pwman.util.crypto_engine import CryptoEngine
from pwman.util.crypto_engine import zerome
from pwman.ui.tools import CliMenuItem
from pwman.ui.tools import CMDLoop, get_or_create_pass


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


class HelpUIMixin:  # pragma: no cover

    """
    this class holds all the UI help functionality.
    in PwmanCliNew. The later inherits from this class
    and allows it to print help messages to the console.
    """

    def _usage(self, string):
        print("Usage: %s" % (string))

    def help_open(self):
        self._usage("open|o <ID>")
        print("Launch default browser with 'xdg-open url',\n",
              "the url must contain http:// or https://.")

    def help_copy(self):
        self._usage("copy|cp <ID>")
        print("Copy password to X clipboard (xsel required)")

    def help_cls(self):
        self._usage("cls")
        print("Clear the Screen from information.")

    def help_list(self):
        self._usage("list|ls|l [[u:<url>] [<tag>]] ...")
        print("List nodes that match current or specified filter.")
        print("You can also limit the search by a url prefixed ",
              "with `u`.\nFor example `ls u:example.com work`.",
              "\nl or ls are aliases.")

    def help_delete(self):
        self._usage("delete|rm <ID|tag> ...")
        print("Deletes nodes.")
        self._mult_id_help()

    def help_help(self):
        self._usage("help|h [topic]")
        print("Prints a help message for a command.")

    def help_edit(self):
        self._usage("edit <ID|tag> ... ")
        print("Edits a nodes.")

    def help_export(self):
        self._usage("export [{'filename': 'foo.csv', 'delimiter':'|'}] ")
        print("All nodes under the current filter are exported.")

    def help_new(self):
        self._usage("new")
        print("Creates a new node.,",
              "You can override default config settings the following way:\n",
              "pwman> n {'leetify':False, 'numerics':True}")

    def help_print(self):
        self._usage("print <ID|tag> ...")
        print("Displays a node. ")
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
        print("Changes the password on the database. (Not implemented!)")
        print("To change the password, export and re-import the database.")

    def help_forget(self):
        self._usage("forget")
        print("Forgets the database password. Your password will need to ",
              "be reentered before accessing the database again.")

    def help_tags(self):
        self._usage("tags")
        print("Displays all tags in used in the database.")

    def help_info(self):
        print("Show information about the current database.")


class AliasesMixin:  # pragma: no cover

    """
    Define all the alias you want here...
    """

    def do_cp(self, args):
        self.do_copy(args)

    def do_EOF(self, args):  # pragma: no cover
        self.do_exit(args)

    def do_l(self, args):
        self.do_list(args)

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


class BaseUtilsMixin:

    """Helper class for storing all privates, useful for testing these methods
    directly
    """

    def _get_ids(self, args):
        """
        Each command can get a single ID or
        a range of IDs, with begin-end.
        e.g. 1-3 , will get 1 to 3.
        """
        ids = []
        rex = re.compile("^(?P<begin>\\d+)(?:-(?P<end>\\d+))?$")
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

        return ids

    def _get_tags(self, default=None, reader=input, tag_IFS=","):
        """
        Read tags from user input.
        Tags are simply returned as a list
        """
        # TODO: add method to read tags from db, so they
        # could be used for tab completer
        print("Tags: ", end="")
        sys.stdout.flush()
        taglist = sys.stdin.readline()
        if isinstance(taglist, bytes):
            taglist = taglist.decode()
        return re.split(r'(?<!\\)%s' % tag_IFS, taglist)

    def _prep_term(self):
        self.do_cls('')
        rows, cols = shutil.get_terminal_size()
        return rows, cols

    def _format_line(self, tag_pad, nid="ID", user="USER", url="URL",
                     tags="TAGS"):

        user_pad = int(self.config.get_value("UI", "URL_pad").split('#')[0])
        url_pad = int(self.config.get_value("UI", "user_pad").split('#')[0])
        tag_pad = int(self.config.get_value("UI", "tag_pad").split('#')[0])
        line = self.config.get_value("UI", "line_format")

        return (line.format(ID=nid, USER=user,
                            URL=url, Tags=tags, user_pad=user_pad,
                            url_pad=url_pad, tag_pad=tag_pad))

    def _print_node_line(self, node, rows, cols, url_filter):
        if url_filter != "" and node.url.find(url_filter) == -1:
            return

        tagstring = ','.join([t.decode() for t in node.tags])

        if len(node.url) > int(self.config.get_value(
                "UI", "URL_length").split("#")[0]):
            node_url = node.url[:int(self.config.get_value("UI", "URL_length").split("#")[0])] + "..." # noqa
        else:
            node_url = node.url

        fmt = self._format_line(cols, node._id, node.username,
                                node_url,
                                tagstring)
        formatted_entry = tools.typeset(fmt, Fore.YELLOW, False)
        print(formatted_entry)

    def _get_node_ids(self, args):
        filter = None
        if args:
            filter = args.split()[0]
            ce = CryptoEngine.get()
            filter = ce.encrypt(filter)
        return self._db.listnodes(filter=filter)

    def _lazy_get_node_ids(self, args):
        filter = None
        if args:
            filter = args.split()[0]
            ce = CryptoEngine.get()
            filter = ce.encrypt(filter)
        for node_id in self._db.lazy_list_node_ids(filter=filter):
            yield node_id

    def _db_entry_to_node(self, raw_node):
        # user, pass, url, notes
        node_inst = Node.from_encrypted_entries(raw_node[1],
                                                raw_node[2],
                                                raw_node[3],
                                                raw_node[4],
                                                raw_node[5:])
        node_inst._id = raw_node[0]
        return node_inst

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
        nid = self._db.add_node(node)
        node.id = nid
        return node

    def _do_rm(self, nodes):
        for i in nodes:
            self._db.removenodes([i])

    def _get_node(self, nodeid):
        if not nodeid.isdigit():
            print("print accepts only a single ID ...")
            return

        node = self._db.get_node(nodeid)
        if not node:  # pragma: no cover
            print("Node not found ...")
            return

        node = self._db_entry_to_node(node)
        return node


class BaseCommands(HelpUIMixin, AliasesMixin, BaseUtilsMixin):

    @property
    def _xsel(self):  # pragma: no cover
        if self.hasxsel:
            return True

    def do_EOF(self, args):
        return self.do_exit(args)

    def error(self, exception):  # pragma: no cover
        if (isinstance(exception, KeyboardInterrupt)):
            print('')
        else:
            print("Error: {0} ".format(exception))

    def do_copy(self, args):  # pragma: no cover
        """copy item to clipboard. Accepts an id or `u:<URL substring>`"""
        if not self.hasxsel:
            return
        if not args.isdigit() and not args.startswith("u:"):
            return

        url_filter = ""
        m = re.search('^u:([^ ]+) ?(.*)$', args)

        if m:
            url_filter, args = m.groups()
            ids = self._db.lazy_list_node_ids()
        else:
            ids = args.split()
            if len(ids) > 1:
                print("Can copy only 1 password at a time...")
                return

        nodes = self._db.getnodes(ids)

        ce = CryptoEngine.get()
        for node in nodes:
            if ce.decrypt(node[3]).find(url_filter.encode()) != -1:
                password = ce.decrypt(node[2])
                tools.text_to_clipboards(password)
                flushtimeout = self.config.get_value('Global', 'cp_timeout')
                flushtimeout = flushtimeout or 10
                print("erasing in {} sec...".format(flushtimeout))

    def do_open(self, args):  # pragma: no cover
        ids = self._get_ids(args)
        if not args:
            self.help_open()
            return

        nodes = self._db.getnodes(ids)
        ce = CryptoEngine.get()
        for node in nodes:
            url = ce.decrypt(node[3]).decode()
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            if url:
                mask = os.umask(22)
                tools.open_url(url)
                os.umask(mask)

    def do_cls(self, args):  # pragma: no cover
        """clear the screen"""
        os.system("clear")

    def do_exit(self, args):  # pragma: no cover
        """close the text console"""
        self._db.close()
        return True

    def do_export(self, args):
        """export the database to a given format"""
        try:
            args = ast.literal_eval(args)
        except Exception:
            args = {}

        filename = args.get('filename', 'pwman-export.csv')
        delim = args.get('delimiter', ';')
        nodes = self._db.getnodes(list(self._db.lazy_list_node_ids()))

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
                r = list([n.username, n.url, n.password, n.notes])
                writer.writerow(r + [tags])

        with open(filename) as f:
            for line in f.readlines():
                print(line)

        print("Successfuly exported database to {}".format(
            os.path.join(os.getcwd(), filename)))

    def do_forget(self, args):
        """
        drop saved key forcing the user to re-enter the master
        password
        """
        enc = CryptoEngine.get()
        enc.forget()

    def do_lock_info(self, args):
        enc = CryptoEngine.get()
        if enc._cipher is None:
            print("The database is locked!")
            return

        lock = enc.lock_info()
        if lock == datetime.MAXYEAR:
            print("Never locks automatically. Use 'forget' to lock the database manually.")
        else:
            print(f"Automatic lock at: {lock.strftime('%Y-%m-%d %H:%M:%S')}.")

    def do_passwd(self, args):  # pragma: no cover
        """change the master password of the database"""
        """old_enc = CryptoEngine.get()
        CryptoEngine._instance = None
        new_enc = CryptoEngine.get()

        TODO: backup tables: NODE, TAG, CRYPTO, LOOKUP
        TODO: create new tables
        TODO: Iterate on old entries, create new entries with new crypto
        TODO: If no errors encountered remove backup tables.

        TODO: expand list nodes to accept table name
        """

    def do_tags(self, args):
        """
        print all existing tags
        """
        ce = CryptoEngine.get()
        print("Tags:")
        tags = self._db.listtags()
        for t in tags:
            print(ce.decrypt(t).decode())

    def do_edit(self, args, menu=None):
        ids = self._get_ids(args)
        for i in ids:
            i = int(i)
            node = self._db.get_node(i)
            if not node:
                print("Node not found ...")
                return
            node = node[1:5] + [node[5:]]
            node = Node.from_encrypted_entries(*node)
            if not menu:
                menu = CMDLoop(self.config)
                print("Editing node %d." % (i))
                menu.add(CliMenuItem("Username", node.username))
                menu.add(CliMenuItem("Password",  node.password))
                menu.add(CliMenuItem("Url", node.url))
                menunotes = CliMenuItem("Notes", node.notes)
                menu.add(menunotes)
                menu.add(CliMenuItem("Tags", ','.join(map(lambda x: x.decode(), node.tags))))  # noqa
            menu.run(node)
            self._db.editnode(i, **node.to_encdict())
            # when done with node erase it
            zerome(node._password)

    def do_list(self, args):
        """
        list all existing nodes in database
        """
        rows, cols = self._prep_term()
        url_filter = ""
        m = re.search('^u:([^ ]+) ?(.*)$', args)

        if m:
            url_filter, args = m.groups()

        nodeids_gen = self._lazy_get_node_ids(args)
        head = self._format_line(cols - 32)
        print(tools.typeset(head, Fore.YELLOW, False))
        for node in self._db.getnodes(nodeids_gen):
            self._print_node_line(self._db_entry_to_node(node), rows, cols,
                                  url_filter)

    def do_new(self, args):  # pragma: no cover
        # The cmd module stops if any of do_* return something
        # else than None ...
        # This is bad for testing, so everything that is do_*
        # should call _do_* method which is testable
        node = self._do_new(args)
        print(node.id)

    def do_pp(self, args):
        """print the password only"""
        node = self._get_node(args)
        print(node.password)

    def do_print(self, args):
        node = self._get_node(args)

        print(node)
        flushtimeout = self.config.get_value('Global', 'cls_timeout')
        flushtimeout = int(flushtimeout) if flushtimeout else 10

        if flushtimeout > 0:
            flushtimeout = flushtimeout or 10
            print("Type Enter to flush screen or wait %d sec. " % flushtimeout)

            _wait_until_enter(_heard_enter, flushtimeout)
            self.do_cls('')

    def do_delete(self, args):

        ce = CryptoEngine.get()
        ce.encrypt("")

        ids = self._get_ids(args)
        if not ids:
            return
        ans = tools.getinput("Are you sure you want to delete node{} {}"
                             " [y/N]?".format("s" if len(ids) > 1 else "",
                                              ",".join(ids) if len(ids) > 1 else ids[0]))  # noqa
        if ans.lower() == 'y':
            self._do_rm(ids)

    def do_info(self, args):
        print("Currently connected to: {}".format(
              self.config.get_value("Database", "dburi")))
