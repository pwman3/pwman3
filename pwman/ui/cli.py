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
# pylint: disable=I0011
"""
Define the CLI interface for pwman3 and the helper functions
"""
from __future__ import print_function
import pwman
import pwman.exchange.importer as importer
import pwman.exchange.exporter as exporter
import pwman.util.generator as generator
from pwman.data.nodes import Node
from pwman.data.nodes import NewNode
from pwman.data.tags import Tag
from pwman.data.tags import TagNew as TagN
from pwman.util.crypto import CryptoEngine
from pwman.util.crypto import zerome
import pwman.util.config as config
import re
import sys
import os
import cmd
import time
import select as uselect
import ast
from pwman.ui import tools
from pwman.ui.tools import CliMenu, CMDLoop
from pwman.ui.tools import CliMenuItem
from pwman.ui.ocli import PwmanCliOld
from colorama import Fore
from pwman.ui.base import HelpUI, BaseUI
import getpass
from pwman.ui.tools import CLICallback

try:
    import readline
    _readline_available = True
except ImportError, e:  # pragma: no cover
    _readline_available = False


def get_pass_conf():
    numerics = config.get_value("Generator", "numerics").lower() == 'true'
    # TODO: allow custom leetifying through the config
    leetify = config.get_value("Generator", "leetify").lower() == 'true'
    special_chars = config.get_value("Generator", "special_chars"
                                     ).lower() == 'true'
    return numerics, leetify, special_chars


class BaseCommands(PwmanCliOld):
    """
    Inherit from the old class, override
    all the methods related to tags, and
    newer Node format, so backward compatability is kept...
    Commands defined here, can have aliases definded in Aliases.
    You can define the aliases here too, but it makes
    the class code really long and unclear.
    """
    def do_copy(self, args):
        if self.hasxsel:
            ids = self.get_ids(args)
            if len(ids) > 1:
                print ("Can copy only 1 password at a time...")
                return None
            try:
                node = self._db.getnodes(ids)
                tools.text_to_clipboards(node[0].password)
                print ("copied password for {}@{} clipboard".format(
                       node[0].username, node[0].url))

                print ("erasing in 10 sec...")
                time.sleep(10)
                tools.text_to_clipboards("")
            except Exception, e:
                self.error(e)
        else:
            print ("Can't copy to clipboard, no xsel found in the system!")

    def do_open(self, args):
        ids = self.get_ids(args)
        if not args:
            self.help_open()
            return
        if len(ids) > 1:
            print ("Can open only 1 link at a time ...")
            return None
        try:
            node = self._db.getnodes(ids)
            url = node[0].url
            tools.open_url(url)
        except Exception, e:
            self.error(e)

    def do_edit(self, arg):
        ids = self.get_ids(arg)
        for i in ids:
            try:
                i = int(i)
                node = self._db.getnodes([i])[0]
                menu = CMDLoop()
                print ("Editing node %d." % (i))

                menu.add(CliMenuItem("Username", self.get_username,
                                     node.username,
                                     node.username))
                menu.add(CliMenuItem("Password", self.get_password,
                                     node.password,
                                     node.password))
                menu.add(CliMenuItem("Url", self.get_url,
                                     node.url,
                                     node.url))
                menunotes = CliMenuItem("Notes", self.get_notes,
                                        node.notes,
                                        node.notes)
                menu.add(menunotes)
                menu.add(CliMenuItem("Tags", self.get_tags,
                                     node.tags,
                                     node.tags))
                menu.run(node)
                self._db.editnode(i, node)
                # when done with node erase it
                zerome(node._password)
            except Exception, e:
                self.error(e)

    def print_node(self, node):
        width = str(tools._defaultwidth)
        print ("Node %d." % (node._id))
        print (("%" + width + "s %s") % (tools.typeset("Username:", Fore.RED),
                                         node.username))
        print (("%" + width + "s %s") % (tools.typeset("Password:", Fore.RED),
                                         node.password))
        print (("%" + width + "s %s") % (tools.typeset("Url:", Fore.RED),
                                         node.url))
        print (("%" + width + "s %s") % (tools.typeset("Notes:", Fore.RED),
                                         node.notes))
        print (tools.typeset("Tags: ", Fore.RED)),
        for t in node.tags:
            print (" %s " % t)
        print()

        def heardEnter():
            i, o, e = uselect.select([sys.stdin], [], [], 0.0001)
            for s in i:
                if s == sys.stdin:
                    sys.stdin.readline()
                    return True
                return False

        def waituntil_enter(somepredicate, timeout, period=0.25):
            mustend = time.time() + timeout
            while time.time() < mustend:
                cond = somepredicate()
                if cond:
                    break
                time.sleep(period)
            self.do_cls('')

        try:
            flushtimeout = int(config.get_value("Global", "cls_timeout"))
        except ValueError:
            flushtimeout = 10

        if flushtimeout > 0:
            print ("Type Enter to flush screen (autoflash in "
                   "%d sec.)" % flushtimeout)
            waituntil_enter(heardEnter, flushtimeout)

    def do_tags(self, arg):
        enc = CryptoEngine.get()
        if not enc.alive():
            enc._getcipher()
        print ("Tags: \n",)
        t = self._tags(enc)
        print ('\n'.join(t))

    def get_tags(self, default=None, reader=raw_input):
        """read tags from user"""
        defaultstr = ''
        if default:
            for t in default:
                defaultstr += "%s " % (t)
        else:
            # tags = self._db.currenttags()
            tags = self._db._filtertags
            for t in tags:
                defaultstr += "%s " % (t)

        # strings = []
        tags = self._db.listtags(True)
        #for t in tags:
            # strings.append(t.get_name())
        #    strings.append(t)

        strings = [t for t in tags]

        def complete(text, state):
            count = 0
            for s in strings:
                if s.startswith(text):
                    if count == state:
                        return s
                    else:
                        count += 1

        taglist = tools.getinput("Tags: ", defaultstr, completer=complete,
                                 reader=reader)
        tagstrings = taglist.split()
        tags = [TagN(tn) for tn in tagstrings]

        return tags

    def do_list(self, args):
        if len(args.split()) > 0:
            self.do_clear('')
            self.do_filter(args)
        try:
            if sys.platform != 'win32':
                rows, cols = tools.gettermsize()
            else:
                rows, cols = 18, 80  # fix this !
            nodeids = self._db.listnodes()
            nodes = self._db.getnodes(nodeids)

            cols -= 8
            i = 0
            for n in nodes:
                tags = n.tags
                tags = filter(None, tags)
                tagstring = ''
                first = True
                for t in tags:
                    if not first:
                        tagstring += ", "
                    else:
                        first = False
                    tagstring += t

                name = "%s@%s" % (n.username, n.url)

                name_len = cols * 2 / 3
                tagstring_len = cols / 3
                if len(name) > name_len:
                    name = name[:name_len - 3] + "..."
                if len(tagstring) > tagstring_len:
                    tagstring = tagstring[:tagstring_len - 3] + "..."
                fmt = "%%5d. %%-%ds %%-%ds" % (name_len, tagstring_len)
                formatted_entry = tools.typeset(fmt % (n._id,
                                                name, tagstring),
                                                Fore.YELLOW, False)
                print (formatted_entry)
                i += 1
                if i > rows - 2:
                    i = 0
                    c = tools.getonechar("Press <Space> for more,"
                                         " or 'Q' to cancel")
                    if c.lower() == 'q':
                        break

        except Exception, e:
            self.error(e)

    def do_filter(self, args):
        tagstrings = args.split()
        try:
            tags = [TagN(ts) for ts in tagstrings]
            self._db.filter(tags)
            tags = self._db.currenttags()
            print ("Current tags: ",)
            if len(tags) == 0:
                print ("None",)
            for t in tags:
                print ("%s " % (t.name),)
            print
        except Exception, e:
            self.error(e)

    def do_new(self, args):
        """
        can override default config settings the following way:
        Pwman3 0.2.1 (c) visit: http://github.com/pwman3/pwman3
        pwman> n {'leetify':False, 'numerics':True, 'special_chars':True}
        Password (Blank to generate):
        """
        errmsg = ("could not parse config override, please input some"
                  " kind of dictionary, e.g.: n {'leetify':False, "
                  " numerics':True, 'special_chars':True}")
        try:
            username = self.get_username()
            if args:
                try:
                    args = ast.literal_eval(args)
                except Exception:
                    raise Exception(errmsg)
                if not isinstance(args, dict):
                    raise Exception(errmsg)
                password = self.get_password(argsgiven=1, **args)
            else:
                numerics, leet, s_chars = get_pass_conf()
                password = self.get_password(argsgiven=0,
                                             numerics=numerics,
                                             symbols=leet,
                                             special_signs=s_chars)
            url = self.get_url()
            notes = self.get_notes()
            node = NewNode(username, password, url, notes)
            node.tags = self.get_tags()
            self._db.addnodes([node])
            print ("Password ID: %d" % (node._id))
            # when done with node erase it
            zerome(password)
        except Exception, e:
            self.error(e)

    def do_print(self, arg):
        for i in self.get_ids(arg):
            try:
                node = self._db.getnodes([i])
                self.print_node(node[0])
                # when done with node erase it
                zerome(node[0]._password)
            except Exception, e:
                self.error(e)

    def do_delete(self, arg):
        ids = self.get_ids(arg)
        try:
            nodes = self._db.getnodes(ids)
            for n in nodes:
                try:
                    b = tools.getyesno(("Are you sure you want to"
                                        " delete '%s@%s'?"
                                        ) % (n.username, n.url), False)
                except NameError:
                    pass
                if b is True:
                    self._db.removenodes([n])
                    print ("%s@%s deleted" % (n.username, n.url))
        except Exception, e:
            self.error(e)

    def get_password(self, argsgiven, numerics=False, leetify=False,
                     symbols=False, special_signs=False,
                     reader=getpass.getpass, length=None):
        return tools.getpassword("Password (Blank to generate): ",
                                 reader=reader, length=length, leetify=leetify)


class Aliases(BaseCommands, PwmanCliOld):
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


class PwmanCliNew(Aliases, BaseCommands):
    """
    Inherit from the BaseCommands and Aliases
    """
    def __init__(self, db, hasxsel, callback):
        """
        initialize CLI interface, set up the DB
        connecion, see if we have xsel ...
        """
        cmd.Cmd.__init__(self)
        self.intro = "%s %s (c) visit: %s" % (pwman.appname, pwman.version,
                                              pwman.website)
        self._historyfile = config.get_value("Readline", "history")
        self.hasxsel = hasxsel
        try:
            enc = CryptoEngine.get()
            enc._callback = callback()
            self._db = db
            self._db.open()
        except Exception, e:  # pragma: no cover
            self.error(e)
            sys.exit(1)

        try:
            readline.read_history_file(self._historyfile)
        except IOError, e:  # pragma: no cover
            pass

        self.prompt = "pwman> "
