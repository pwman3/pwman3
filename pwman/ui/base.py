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
from __future__ import print_function
from pwman.util.crypto import CryptoEngine
from pwman.util.crypto import zerome
import pwman.util.config as config
import re
import sys
import os
import time
import select as uselect
import ast
from pwman.ui import tools
from pwman.ui.tools import CliMenuItem
from colorama import Fore
from pwman.data.nodes import NewNode
from pwman.ui.tools import CMDLoop
import getpass
from pwman.data.tags import TagNew
import csv


def get_pass_conf():
    numerics = config.get_value("Generator", "numerics").lower() == 'true'
    # TODO: allow custom leetifying through the config
    leetify = config.get_value("Generator", "leetify").lower() == 'true'
    special_chars = config.get_value("Generator", "special_chars"
                                     ).lower() == 'true'
    return numerics, leetify, special_chars


class HelpUI(object):
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
               " l is an alias.")

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

    def help_save(self):
        self.usage("save [filename]")
        print("Saves the current configuration to [filename]. If no filename ",
              "is given, the configuration is saved to the file from which ",
              "the initial configuration was loaded.")

    def help_set(self):
        self.usage("set [configoption] [value]")
        print("Sets a configuration option. If no value is specified, the ",
              "current value for [configoption] is output. If neither ",
              "[configoption] nor [value] are specified, the whole current ",
              "configuration is output. [configoption] must be of the ",
              "format <section>.<option>")

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


# pylint: disable=R0904
class BaseCommands(BaseUI, HelpUI):
    """
    Inherit from the old class, override
    all the methods related to tags, and
    newer Node format, so backward compatability is kept...
    Commands defined here, can have aliases definded in Aliases.
    You can define the aliases here too, but it makes
    the class code really long and unclear.
    """
    def error(self, exception):
        if (isinstance(exception, KeyboardInterrupt)):
            print('')
        else:
            print("Error: {0} ".format(exception))

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

    def do_exit(self, args):
        """exit the ui"""
        self._db.close()
        return True

    def do_export(self, args):
        try:
            args = ast.literal_eval(args)
        except Exception:
            args = {}

        filename = args.get('filename', 'pwman-export.csv')
        delim = args.get('delimiter', ';')
        nodeids = self._db.listnodes()
        nodes = self._db.getnodes(nodeids)
        with open(filename, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=delim)
            writer.writerow(['Username', 'URL', 'Password', 'Notes', 'Tags'])
            for n in nodes:
                tags = n.tags
                tags = filter(None, tags)
                tags = ','.join(t.strip() for t in tags)
                writer.writerow([n.username, n.url, n.password, n.notes,
                                 tags])

        print("Successfuly exported database to {}".format(
            os.path.join(os.getcwd(), filename)))

    def do_forget(self, args):
        try:
            enc = CryptoEngine.get()
            enc.forget()
        except Exception, e:
            self.error(e)

    def do_set(self, args):
        argstrs = args.split()
        try:
            if len(argstrs) == 0:
                conf = config.get_conf()
                for s in conf.keys():
                    for n in conf[s].keys():
                        print ("%s.%s = %s" % (s, n, conf[s][n]))
            elif len(argstrs) == 1:
                r = re.compile("(.+)\.(.+)")
                m = r.match(argstrs[0])
                if m is None or len(m.groups()) != 2:
                    print ("Invalid option format")
                    self.help_set()
                    return
                print ("%s.%s = %s" % (m.group(1), m.group(2),
                                       config.get_value(m.group(1),
                                                        m.group(2))))
            elif len(argstrs) == 2:
                r = re.compile("(.+)\.(.+)")
                m = r.match(argstrs[0])
                if m is None or len(m.groups()) != 2:
                    print ("Invalid option format")
                    self.help_set()
                    return
                config.set_value(m.group(1), m.group(2), argstrs[1])
            else:
                self.help_set()
        except Exception, e:
            self.error(e)

    def get_username(self, default="", reader=raw_input):
        return tools.getinput("Username: ", default, reader)

    def get_url(self, default="", reader=raw_input):
        return tools.getinput("Url: ", default, reader)

    def get_notes(self, default="", reader=raw_input):
        return tools.getinput("Notes: ", default, reader)

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

    def do_clear(self, args):
        try:
            self._db.clearfilter()
        except Exception, e:
            self.error(e)

    def do_cls(self, args):
        os.system('clear')

    def do_edit(self, arg, menu=None):
        ids = self.get_ids(arg)
        for i in ids:
            try:
                i = int(i)
                node = self._db.getnodes([i])[0]
                if not menu:
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

    def do_passwd(self, args):
        try:
            key = self._db.changepassword()
            self._db.savekey(key)
        except Exception, e:
            self.error(e)

    def do_save(self, args):
        argstrs = args.split()
        try:
            if len(argstrs) > 0:
                config.save(argstrs[0])
            else:
                config.save()
            print ("Config saved.")
        except Exception, e:
            self.error(e)

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
        # for t in tags:
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
        tags = [TagNew(tn) for tn in tagstrings]

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
            tags = [TagNew(ts) for ts in tagstrings]
            self._db.filter(tags)
            tags = self._db.currenttags()
            print ("Current tags: ",)
            if len(tags) == 0:
                print ("None",)
            for t in tags:
                print ("%s " % t)
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
            node = NewNode()
            node.username = username
            node.password = password
            node.url = url
            node.notes = notes
            #node = NewNode(username, password, url, notes)
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
                ans = ''
                while True:
                    ans = tools.getinput(("Are you sure you want to"
                                         " delete '%s@%s' ([y/N])?"
                                          ) % (n.username, n.url)
                                         ).lower().strip('\n')
                    if ans == '' or ans == 'y' or ans == 'n':
                        break
            if ans == 'y':
                self._db.removenodes([n])
                print ("%s@%s deleted" % (n.username, n.url))
        except Exception, e:
            self.error(e)

    def get_ids(self, args):
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
                ids += range(begin, end+1)
                return ids
            except TypeError:
                ids.append(int(begin))
        else:
            print("Could not understand your input...")
        return ids

    def get_password(self, argsgiven, numerics=False, leetify=False,
                     symbols=False, special_signs=False,
                     reader=getpass.getpass, length=None):
        return tools.getpassword("Password (Blank to generate): ",
                                 reader=reader, length=length, leetify=leetify)


class Aliases(BaseCommands):
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
