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
# pylint: disable=I0011
"""
Define the base CLI interface for pwman3
"""
from pwman.util.crypto import CryptoUnsupportedException


class HelpUI(object):
    """
    this class holds all the UI help functionality.
    in PwmanCliNew. The later inherits from this class
    and allows it to print help messages to the console.
    """
    def usage(self, string):
        print "Usage: %s" % (string)

    def help_open(self):
        self.usage("open <ID>")
        print "Launch default browser with 'xdg-open url',\n" \
              + "the url must contain http:// or https://."

    def help_o(self):
        self.help_open()

    def help_copy(self):
        self.usage("copy <ID>")
        print "Copy password to X clipboard (xsel required)"

    def help_cp(self):
        self.help_copy()

    def help_cls(self):
        self.usage("cls")
        print "Clear the Screen from information."

    def help_list(self):
        self.usage("list <tag> ...")
        print "List nodes that match current or specified filter." \
              + " l is an alias."

    def help_EOF(self):
        self.help_exit()

    def help_delete(self):
        self.usage("delete <ID|tag> ...")
        print "Deletes nodes. rm is an alias."
        self._mult_id_help()

    def help_h(self):
        self.help_help()

    def help_help(self):
        self.usage("help [topic]")
        print "Prints a help message for a command."

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
        print "Edits a nodes."
        self._mult_id_help()

    def help_import(self):
        self.usage("import [filename] ...")
        print "Imports a nodes from a file."

    def help_export(self):
        self.usage("export <ID|tag> ... ")
        print "Exports a list of ids to an external format. If no IDs or" \
              + " tags are specified, then all nodes under the current" \
              + " filter are exported."
        self._mult_id_help()

    def help_new(self):
        self.usage("new")
        print """Creates a new node.,
You can override default config settings the following way:
pwman> n {'leetify':False, 'numerics':True}"""

    def help_rm(self):
        self.help_delete()

    def help_print(self):
        self.usage("print <ID|tag> ...")
        print "Displays a node. ",
        self._mult_id_help()

    def _mult_id_help(self):
        print "Multiple ids and nodes can be specified, separated by a space."\
              + "A range of ids can be specified in the format n-N. e.g. " \
              + "'10-20' would specify all nodes having ids from 10 to 20 " \
              + "inclusive. Tags are considered one-by-one. e.g. 'foo 2 bar'" \
              + " would yield to all nodes with tag 'foo', node 2 and all "\
              + "nodes with tag 'bar'."

    def help_exit(self):
        self.usage("exit")
        print "Exits the application."

    def help_save(self):
        self.usage("save [filename]")
        print "Saves the current configuration to [filename]. If no filename "\
              + "is given, the configuration is saved to the file from which "\
              + "the initial configuration was loaded."

    def help_set(self):
        self.usage("set [configoption] [value]")
        print "Sets a configuration option. If no value is specified, the "\
              + "current value for [configoption] is output. If neither "\
              + "[configoption] nor [value] are specified, the whole current "\
              + "configuration is output. [configoption] must be of the "\
              + "format <section>.<option>"

    def help_passwd(self):
        self.usage("passwd")
        print "Changes the password on the database. "

    def help_forget(self):
        self.usage("forget")
        print "Forgets the database password. Your password will need to " \
              + "be reentered before accessing the database again."

    def help_clear(self):
        self.usage("clear")
        print "Clears the filter criteria. "

    def help_filter(self):
        self.usage("filter <tag> ...")
        print "Filters nodes on tag. Arguments can be zero or more tags. " \
              + "Displays current tags if called without arguments."

    def help_tags(self):
        self.usage("tags")
        print "Displays all tags in used in the database."


class BaseUI(object):
    """
    this class holds all the UI functionality
    in PwmanCliNew. The later inherits from this class
    and allows it to print messages to the console.
    """

    def _do_filter(self, args):
        pass

    def _tags(self, enc):
        """
        read tags from TAGS table in DB,
        this method has a working unittest
        """
        tags = self._db.listtags()
        if tags:
            _tags = [''] * len(tags)
            for t in tags:
                try:
                    _tags.append(enc.decrypt(t))
                except (ValueError, Exception), e:
                    _tags.append(t)
                    del(e)
            _tags = filter(None, _tags)
            return _tags
