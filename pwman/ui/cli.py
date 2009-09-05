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
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
#============================================================================

import pwman
import pwman.exchange.importer as importer
import pwman.exchange.exporter as exporter
import pwman.util.generator as generator
from pwman.data.nodes import Node
from pwman.data.tags import Tag

from pwman.util.crypto import CryptoEngine, CryptoBadKeyException, \
     CryptoPasswordMismatchException
from pwman.util.callback import Callback
import pwman.util.config as config

import re
import sys
import tty
import os
import getpass
import cmd
import traceback

try:
    import readline
    _readline_available = True
except ImportError, e:
    _readline_available = False

class CLICallback(Callback):
    def getinput(self, question):
        return raw_input(question)
    
    def getsecret(self, question):
        return getpass.getpass(question + ":")

class ANSI(object):
    Reset = 0
    Bold = 1
    Underscore = 2

    Black = 30
    Red = 31
    Green = 32
    Yellow = 33
    Blue = 34
    Magenta = 35
    Cyan = 36
    White = 37

class PwmanCli(cmd.Cmd):
    def error(self, exception):
        if (isinstance(exception, KeyboardInterrupt)):
            print
        else:
#            traceback.print_exc()
            print "Error: %s " % (exception)
    
    def do_EOF(self, args):
        return self.do_exit(args)

    def do_exit(self, args):
        print
        try:
            self._db.close()
        except Exception, e:
            self.error(e)
        return True

    def get_ids(self, args):
        ids = []
        rx =re.compile(r"^(\d+)-(\d+)$")
        idstrs = args.split()
        for i in idstrs:
            m = rx.match(i)
            if m == None:
                try:
                    ids.append(int(i))
                except ValueError, e:
                    self._db.clearfilter()
                    self._db.filter([Tag(i)])
                    ids += self._db.listnodes()
            else:
                ids += range(int(m.group(1)),
                             int(m.group(2))+1)
        return ids
    
    def get_filesystem_path(self, default=""):
        return getinput("Enter filename: ", default)
    
    def get_username(self, default=""):
        return getinput("Username: ", default)

    def get_password(self, default=""):
        password = getpassword("Password (Blank to generate): ", _defaultwidth, False)
        if len(password) == 0:
            length = getinput("Password length (default 7): ", "7")
            length = int(length)

            numerics = config.get_value("Generator", "numerics") == 'true';
            leetify = config.get_value("Generator", "leetify") == 'true';
            (password, dumpme) = generator.generate_password(length, length, True, leetify, numerics)

            print "New password: %s" % (password)
            return password
        else:
            return password

    def get_url(self, default=""):
        return getinput("Url: ", default)

    def get_notes(self, default=""):
        return getinput("Notes: ", default)

    def get_tags(self, default=[]):
        defaultstr = ''

        if len(default) > 0:
            for t in default:
                defaultstr += "%s " % (t.get_name())
        else:
            tags = self._db.currenttags()
            for t in tags:
                defaultstr += "%s " % (t.get_name())

        strings = []
        tags = self._db.listtags(True)
        for t in tags:
            strings.append(t.get_name())

        def complete(text, state):
            count = 0
            for s in strings:
                if s.startswith(text):
                    if count == state:
                        return s
                    else:
                        count += 1

        taglist = getinput("Tags: ", defaultstr, complete)
        tagstrings = taglist.split()
        tags = []
        for tn in tagstrings:
            tags.append(Tag(tn))
        return tags
        
    def print_node(self, node):
        width = str(_defaultwidth)
        print "Node %d." % (node.get_id())
        print ("%"+width+"s %s") % (typeset("Username:", ANSI.Red),
                                    node.get_username())
        print ("%"+width+"s %s") % (typeset("Password:", ANSI.Red),
                                    node.get_password())
        print ("%"+width+"s %s") % (typeset("Url:", ANSI.Red),
                                    node.get_url())
        print ("%"+width+"s %s") % (typeset("Notes:", ANSI.Red),
                                    node.get_notes())
        print typeset("Tags: ", ANSI.Red),
        for t in node.get_tags():
            print "%s " % t.get_name(),
        print

    def do_tags(self, arg):
        tags = self._db.listtags()
        if len(tags) > 0:
            tags[0].get_name() # hack to get password request before output
        print "Tags: ",
        if len(tags) == 0:
            print "None",
        for t in tags:
            print "%s " % (t.get_name()),
        print

    def complete_filter(self, text, line, begidx, endidx):
        strings = []
        enc = CryptoEngine.get()
        if not enc.alive():
            return strings
        
        tags = self._db.listtags()
        for t in tags:
            name = t.get_name()
            if name.startswith(text):
                strings.append(t.get_name())
        return strings


    def do_filter(self, args):
        tagstrings = args.split()

        try:
            tags = []
            for ts in tagstrings:
                tags.append(Tag(ts))
            self._db.filter(tags)

            tags = self._db.currenttags()
            print "Current tags: ",
            if len(tags) == 0:
                print "None",
            for t in tags:
                print "%s " % (t.get_name()),
            print
        except Exception, e:
            self.error(e)

    def do_clear(self, args):
        try:
            self._db.clearfilter()
        except Exception, e:
            self.error(e)

    def do_e(self, arg):
        self.do_edit(arg)

    def do_edit(self, arg):
        ids = self.get_ids(arg)
        for i in ids:
            try:
                i = int(i)
                node = self._db.getnodes([i])[0]
                menu = CliMenu()
                print "Editing node %d." % (i)
                menu.add(CliMenuItem("Username", self.get_username,
                                     node.get_username,
                                     node.set_username))
                menu.add(CliMenuItem("Password", self.get_password,
                                     node.get_password,
                                     node.set_password))
                menu.add(CliMenuItem("Url", self.get_url,
                                     node.get_url,
                                     node.set_url))
                menu.add(CliMenuItem("Notes", self.get_notes,
                                     node.get_notes,
                                     node.set_notes))
                menu.add(CliMenuItem("Tags", self.get_tags,
                                     node.get_tags,
                                     node.set_tags))

                menu.run()
                self._db.editnode(i, node)
            except Exception, e:
                self.error(e)


    def do_import(self, arg):
        try:
            args = arg.split()
            if len(args) == 0:
                types = importer.Importer.types()
                type = select("Select filetype:", types)
                imp = importer.Importer.get(type)
                file = getinput("Select file:")
                imp.import_data(self._db, file)
            else:
                for i in args:
                    types = importer.Importer.types()
                    type = select("Select filetype:", types)
                    imp = importer.Importer.get(type)
                    imp.import_data(self._db, i)
        except Exception, e:
            self.error(e)

    def do_export(self, arg):
        try:
            nodes = self.get_ids(arg)
                
            types = exporter.Exporter.types()
            type = select("Select filetype:", types)
            exp = exporter.Exporter.get(type)
            file = getinput("Select output file:")
            if len(nodes) > 0:
                b = getyesno("Export nodes %s?" % (nodes), True)
                if not b:
                    return
                exp.export_data(self._db, file, nodes)
            else:
                nodes = self._db.listnodes()
                tags = self._db.currenttags()
                tagstr = ""
                if len(tags) > 0:
                    tagstr = " for "
                    for t in tags:
                        tagstr += "'%s' " % (t.get_name())

                b = getyesno("Export all nodes%s?" % (tagstr), True)
                if not b:
                    return
                exp.export_data(self._db, file, nodes)
            print "Data exported."
        except Exception, e:
            self.error(e)

    def do_h(self, arg):
        self.do_help(arg)

    def do_n(self, arg):
        self.do_new(arg)

    def do_new(self, arg):
        try:
            username = self.get_username()
            password = self.get_password()
            url = self.get_url()
            notes = self.get_notes()
            node = Node(username, password, url, notes)
            tags = self.get_tags()
            node.set_tags(tags)
            self._db.addnodes([node])
            print "Password ID: %d" % (node.get_id())
        except Exception, e:
            self.error(e)

    def do_p(self, arg):
        self.do_print(arg)

    def do_print(self, arg):
        for i in self.get_ids(arg):
            try:
                node = self._db.getnodes([i])
                self.print_node(node[0])
            except Exception, e:
                self.error(e)

    def do_rm(self, arg):
        self.do_delete(arg)
        
    def do_delete(self, arg):
         ids = self.get_ids(arg)
         try:
             nodes = self._db.getnodes(ids)
             for n in nodes:
                 b = getyesno("Are you sure you want to delete '%s@%s'?"
                              % (n.get_username(), n.get_url()), False)
                 if b == True:
                     self._db.removenodes([n])
                     print "%s@%s deleted" % (n.get_username(), n.get_url())
         except Exception, e:
             self.error(e)

    def do_l(self, args):
        self.do_list(args)

    def do_ls(self, args):
        self.do_list(args)
        
    def do_list(self, args):
        if len(args.split()) > 0:
            self.do_clear('')
            self.do_filter(args)
        try:
            nodeids = self._db.listnodes()
            nodes = self._db.getnodes(nodeids)
            i = 0
            for n in nodes:
                tags=n.get_tags()
                tagstring = ''
                first = True
                for t in tags:
                    if not first:
                        tagstring += ", "
                    else:
                        first=False
                    tagstring += t.get_name()
                name = "%s@%s" % (n.get_username(), n.get_url())
                if len(name) > 30:
                    name = name[:27] + "..."
                if len(tagstring) > 20:
                    tagstring = tagstring[:17] + "..."
                    
                print typeset("%5d. %-30s %-20s" % (n.get_id(), name, tagstring),
                              ANSI.Yellow, False)
                i += 1
                if i > 23:
                    i = 0
                    c = getonechar("Press <Space> for more, or 'Q' to cancel")
                    if c == 'q':
                        break
        except Exception, e:
            self.error(e)

    def do_forget(self, args):
        try:
            enc = CryptoEngine.get()
            enc.forget()
        except Exception,e:
            self.error(e)
            
    def do_passwd(self, args):
        try:
            self._db.changepassword()
        except Exception, e:
            self.error(e)

    def do_set(self, args):
        argstrs = args.split()
        try:
            if len(argstrs) == 0:
                conf = config.get_conf()
                for s in conf.keys():
                    for n in conf[s].keys():
                        print "%s.%s = %s" % (s, n, conf[s][n])
            elif len(argstrs) == 1:
                r = re.compile("(.+)\.(.+)")
                m = r.match(argstrs[0])
                if m is None or len(m.groups()) != 2:
                    print "Invalid option format"
                    self.help_set()
                    return
                print "%s.%s = %s" % (m.group(1), m.group(2),
                                      config.get_value(m.group(1), m.group(2)))
            elif len(argstrs) == 2:
                r = re.compile("(.+)\.(.+)")
                m = r.match(argstrs[0])
                if m is None or len(m.groups()) != 2:
                    print "Invalid option format"
                    self.help_set()
                    return
                config.set_value(m.group(1), m.group(2), argstrs[1])
            else:
                self.help_set()
        except Exception, e:
            self.error(e)

    def do_save(self, args):
        argstrs = args.split()
        try:
            if len(argstrs) > 0:
                config.save(argstrs[0])
            else:
                config.save()
            print "Config saved."
        except Exception, e:
            self.error(e)
    
    ##
    ## Help functions
    ##
    def usage(self, string):
        print "Usage: %s" % (string)
        
    def help_ls(self):
        self.help_list()
        
    def help_list(self):
        self.usage("list <tag> ...")
        print "List nodes that match current or specified filter. ls is an alias."

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
        print "Exports a list of ids to an external format. If no IDs or tags are specified, then all nodes under the current filter are exported."
        self._mult_id_help()
        
    def help_new(self):
        self.usage("new")
        print "Creates a new node."
    
    def help_rm(self):
        self.help_delete()
    
    def help_print(self):
        self.usage("print <ID|tag> ...")
        print "Displays a node. ",
        self._mult_id_help()

    def _mult_id_help(self):
        print "Multiple ids and nodes can be specified, separated by a space. A range of ids can be specified in the format n-N. e.g. '10-20' would specify all nodes having ids from 10 to 20 inclusive. Tags are considered one-by-one. e.g. 'foo 2 bar' would yield to all nodes with tag 'foo', node 2 and all nodes with tag 'bar'."
    
    def help_exit(self):
        self.usage("exit")
        print "Exits the application."

    def help_save(self):
        self.usage("save [filename]")
        print "Saves the current configuration to [filename]. If no filename is given, the configuration is saved to the file from which the initial configuration was loaded."

    def help_set(self):
        self.usage("set [configoption] [value]")
        print "Sets a configuration option. If no value is specified, the current value for [configoption] is output. If neither [configoption] nor [value] are specified, the whole current configuration is output. [configoption] must be of the format <section>.<option>"
        
    def help_ls(self):
        self.help_list()
    
    def help_passwd(self):
        self.usage("passwd")
        print "Changes the password on the database. "

    def help_forget(self):
        self.usage("forget")
        print "Forgets the database password. Your password will need to be reentered before accessing the database again."

    def help_clear(self):
        self.usage("clear")
        print "Clears the filter criteria. "

    def help_filter(self):
        self.usage("filter <tag> ...")
        print "Filters nodes on tag. Arguments can be zero or more tags. Displays current tags if called without arguments."

    def help_tags(self):
        self.usage("tags")
        print "Displays all tags in used in the database."
        
    def postloop(self):
        try:
            readline.write_history_file(self._historyfile)
        except Exception, e:
            pass
    
    def __init__(self, db):
        cmd.Cmd.__init__(self)
        self.intro = "%s %s (c) %s <%s>" % (pwman.appname, pwman.version,
                                            pwman.author, pwman.authoremail)
        self._historyfile = config.get_value("Readline", "history")

        try:
            enc = CryptoEngine.get()
            enc.set_callback(CLICallback())
            self._db = db
            self._db.open()
        except Exception, e:
            self.error(e)
            sys.exit(1)

        try:
            readline.read_history_file(self._historyfile)
        except Exception, e:
            pass

        self.prompt = "pwman> "


_defaultwidth = 10

def getonechar(question, width=_defaultwidth):
    question = "%s " % (question)
    print question.ljust(width),
    sys.stdout.flush()
        
    fd = sys.stdin.fileno()
    tty_mode = tty.tcgetattr(fd)
    tty.setcbreak(fd)
    try:
        ch = os.read(fd, 1)
    finally:
        tty.tcsetattr(fd, tty.TCSAFLUSH, tty_mode)
    print ch
    return ch
    
def getyesno(question, defaultyes=False, width=_defaultwidth):
    if (defaultyes):
        default = "[Y/n]"
    else:
        default = "[y/N]"
    ch = getonechar("%s %s" % (question, default), width)
    if (ch == '\n'):
        if (defaultyes):
            return True
        else:
            return False
    elif (ch == 'y' or ch == 'Y'):
        return True
    elif (ch == 'n' or ch == 'N'):
        return False
    else:
        return getyesno(question, defaultyes, width)


def getinput(question, default="", completer=None, width=_defaultwidth):
    if (not _readline_available):
        return raw_input(question.ljust(width))
    else:
        def defaulter(): readline.insert_text(default)
        readline.set_startup_hook(defaulter)
        oldcompleter = readline.get_completer()
        readline.set_completer(completer)
        
        x = raw_input(question.ljust(width))

        readline.set_completer(oldcompleter)
        readline.set_startup_hook()
        return x

def getpassword(question, width=_defaultwidth, echo=False):
    if echo:
        print question.ljust(width),
        return sys.stdin.readline().rstrip()
    else:
        
        while 1:
            a1 = getpass.getpass(question.ljust(width))
            if len(a1) == 0:
                return a1;
            a2 = getpass.getpass("[Repeat] %s" % (question.ljust(width)))
            if a1 == a2:
                return a1
            else:
                print "Passwords don't match. Try again."
        
        
def typeset(text, color, bold=False, underline=False):
    if not config.get_value("Global", "colors") == 'yes':
        return text
    if (bold):
        bold = "%d;" %(ANSI.Bold)
    else:
        bold = ""
    if (underline):
        underline = "%d;" % (ANSI.Underline)
    else:
        underline = ""
    return "\033[%s%s%sm%s\033[%sm" % (bold, underline, color,
                                       text, ANSI.Reset)

def select(question, possible):
    for i in range(0, len(possible)):
        print ("%d - %-"+str(_defaultwidth)+"s") % (i+1, possible[i])
    while 1:
        input = getonechar(question)
        if input.isdigit() and int(input) in range(1, len(possible)+1):
            return possible[int(input)-1]
        
class CliMenu(object):
    def __init__(self):
        self.items = []
        
    def add(self, item):
        if (isinstance(item, CliMenuItem)):
            self.items.append(item)
        else:
            print item.__class__

    def run(self):
        while True:
            i = 0
            for x in self.items:
                i = i + 1
                current = x.getter()
                currentstr = ''
                if type(current) == list:
                    for c in current:
                        currentstr += ("%s " % (c))
                else:
                    currentstr = current
                    
                print ("%d - %-"+str(_defaultwidth)+"s %s") % (i, x.name+":",
                                                               currentstr)
            print "%c - Finish editing" % ('X')
            option = getonechar("Enter your choice:")
            try:
                # substract 1 because array subscripts start at 1
                selection = int(option) - 1 
                value = self.items[selection].editor(self.items[selection].getter())
                self.items[selection].setter(value)
            except (ValueError,IndexError):
                if (option.upper() == 'X'):
                    break
                print "Invalid selection"
                
class CliMenuItem(object):
    def __init__(self, name, editor, getter, setter):
        self.name = name
        self.editor = editor
        self.getter = getter
        self.setter = setter
