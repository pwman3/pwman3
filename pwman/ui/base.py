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
# Copyright (C) 2013 Oz Nahum <nahumoz@gmail.com>
# ============================================================================
# pylint: disable=I0011
"""
Define the base CLI interface for pwman3
"""
from __future__ import print_function
import sys

if sys.version_info.major > 2:  # pragma: no cover
    raw_input = input


class HelpUIMixin(object):  # pragma: no cover
    """
    this class holds all the UI help functionality.
    in PwmanCliNew. The later inherits from this class
    and allows it to print help messages to the console.
    """
    def usage(self, string):
        print ("Usage: %s" % (string))

    def help_open(self):
        self.usage("open <ID>")
        print ("Launch default browser with 'xdg-open url',\n",
               "the url must contain http:// or https://.")

    def help_o(self):
        self.help_open()

    def help_copy(self):
        self.usage("copy <ID>")
        print ("Copy password to X clipboard (xsel required)")

    def help_cp(self):
        self.help_copy()

    def help_cls(self):
        self.usage("cls")
        print ("Clear the Screen from information.")

    def help_list(self):
        self.usage("list <tag> ...")
        print ("List nodes that match current or specified filter.",
               " ls is an alias.")

    def help_EOF(self):
        self.help_exit()

    def help_delete(self):
        self.usage("delete <ID|tag> ...")
        print ("Deletes nodes. rm is an alias.")
        self._mult_id_help()

    def help_h(self):
        self.help_help()

    def help_help(self):
        self.usage("help [topic]")
        print ("Prints a help message for a command.")

    def help_e(self):
        self.help_edit()

    def help_n(self):
        self.help_new()

    def help_p(self):
        self.help_print()

    def help_l(self):
        self.help_list()

    def help_edit(self):
        self.usage("edit <ID|tag> ... ")
        print ("Edits a nodes.")

    def help_import(self):
        self.usage("import [filename] ...")
        print ("Not implemented...")

    def help_export(self):
        self.usage("export [{'filename': 'foo.csv', 'delimiter':'|'}] ")
        print("All nodes under the current filter are exported.")

    def help_new(self):
        self.usage("new")
        print ("Creates a new node.,",
               "You can override default config settings the following way:\n",
               "pwman> n {'leetify':False, 'numerics':True}")

    def help_rm(self):
        self.help_delete()

    def help_print(self):
        self.usage("print <ID|tag> ...")
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
        self.usage("exit")
        print("Exits the application.")

    def help_passwd(self):
        self.usage("passwd")
        print("Changes the password on the database. ")

    def help_forget(self):
        self.usage("forget")
        print("Forgets the database password. Your password will need to ",
              "be reentered before accessing the database again.")

    def help_clear(self):
        self.usage("clear")
        print("Clears the filter criteria. ")

    def help_filter(self):
        self.usage("filter <tag> ...")
        print("Filters nodes on tag. Arguments can be zero or more tags. ",
              "Displays current tags if called without arguments.")

    def help_tags(self):
        self.usage("tags")
        print("Displays all tags in used in the database.")


class AliasesMixin(object):  # pragma: no cover
    """
    Define all the alias you want here...
    """
    def do_cp(self, args):
        self.do_copy(args)

    def do_e(self, arg):
        self.do_edit(arg)

    def do_EOF(self, args):
        return self.do_exit(args)

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

    def do_h(self, arg):
        self.do_help(arg)

    def do_n(self, arg):
        self.do_new(arg)
