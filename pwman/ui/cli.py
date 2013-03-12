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
"""
Define the CLI interface for pwman3 and the helper functions
"""

import pwman
import pwman.exchange.importer as importer
import pwman.exchange.exporter as exporter
import pwman.util.generator as generator
from pwman.data.nodes import Node
from pwman.data.tags import Tag
from pwman.util.crypto import CryptoEngine
#, CryptoBadKeyException, \
#     CryptoPasswordMismatchException
from pwman.util.callback import Callback
import pwman.util.config as config
import re
import sys
import os
import struct
import getpass
import cmd
#import traceback
import time
import select as uselect
import subprocess as sp
import ast

if sys.platform != 'win32':
    import tty
    import termios
    import fcntl

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
        #try:
        #    print "goodbye"
        self._db.close()
        #except DatabaseException, e:
        #    self.error(e)
        return True

    def get_ids(self, args):
        ids = []
        rex = re.compile(r"^(\d+)-(\d+)$")
        idstrs = args.split()
        for i in idstrs:
            m = rex.match(i)
            if m == None:
                try:
                    ids.append(int(i))
                except ValueError:
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

    def get_password(self, numerics=False,leetify=False):
        """
        numerics -> numerics
        leetify -> symbols
        """
        # TODO: add key word for specialsigns = False
        password = getpassword("Password (Blank to generate): ", _defaultwidth, \
            False)
        if len(password) == 0:
            length = getinput("Password length (default 7): ", "7")
            length = int(length)

            numerics = config.get_value("Generator", "numerics") == 'true'
            leetify = config.get_value("Generator", "leetify") == 'true'
                                 generate_password(minlen, maxlen, capitals = True, symbols = False, numerics = False)
            (password, dumpme) = generator.generate_password(length, length, \
                True, leetify, numerics)

            print "New password: %s" % (password)
            return password
        else:
            return password

    def get_url(self, default=""):
        return getinput("Url: ", default)

    def get_notes(self, default=""):
        return getinput("Notes: ", default)

    def get_tags(self, default="tag"):
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
            print " %s " % t.get_name(),
        print

        def heardEnter():
            i, o, e = uselect.select([sys.stdin], [], [], 0.0001)
            for s in i:
                if s == sys.stdin:
                    sys.stdin.readline()
                    return True
                return False

        def heardEnterWin():
            import msvcrt
            c = msvcrt.kbhit()
            if c == 1:
                ret = msvcrt.getch()
                if ret is not None:
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
        
        flushtimeout = int(config.get_value("Global", "cls_timeout"))
        if flushtimeout > 0:
            if sys.platform != 'win32':
                print "Type Enter to flush screen (autoflash in 5 sec.)"
                waituntil_enter(heardEnter, flushtimeout)
            else:
                print "Press any key to flush screen (autoflash in 5 sec.)"
                waituntil_enter(heardEnterWin, flushtimeout)

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
                intype = select("Select filetype:", types)
                imp = importer.Importer.get(intype)
                infile = getinput("Select file:")
                imp.import_data(self._db, infile)
            else:
                for i in args:
                    types = importer.Importer.types()
                    intype = select("Select filetype:", types)
                    imp = importer.Importer.get(intype)
                    imp.import_data(self._db, i)
        except Exception, e:
            self.error(e)

    def do_export(self, arg):
        try:
            nodes = self.get_ids(arg)

            types = exporter.Exporter.types()
            ftype = select("Select filetype:", types)
            exp = exporter.Exporter.get(ftype)
            out_file = getinput("Select output file:")
            if len(nodes) > 0:
                b = getyesno("Export nodes %s?" % (nodes), True)
                if not b:
                    return
                exp.export_data(self._db, out_file, nodes)
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
                exp.export_data(self._db, out_file, nodes)
            print "Data exported."
        except Exception, e:
            self.error(e)

    def do_h(self, arg):
        self.do_help(arg)

    def do_n(self, arg):
        self.do_new(arg)

    def do_new(self, args):
        """
        can override default config settings the following way:
        Pwman3 0.2.1 (c) visit: http://github.com/pwman3/pwman3
        pwman> n {'leetify':False, 'numerics':True}
        Password (Blank to generate):
        """
        try:
            username = self.get_username()
            if args:
                args = ast.literal_eval(args)
                password = self.get_password(**args)
            else:
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
            if sys.platform != 'win32':
                rows, cols = gettermsize()
            else:
                rows, cols = 18, 80 # fix this !
            nodeids = self._db.listnodes()
            nodes = self._db.getnodes(nodeids)
            cols -= 8
            i = 0
            for n in nodes:
                tags = n.get_tags()
                tagstring = ''
                first = True
                for t in tags:
                    if not first:
                        tagstring += ", "
                    else:
                        first = False
                    tagstring += t.get_name()
                name = "%s@%s" % (n.get_username(), n.get_url())

                name_len = cols * 2 / 3
                tagstring_len = cols / 3
                if len(name) > name_len:
                    name = name[:name_len-3] + "..."
                if len(tagstring) > tagstring_len:
                    tagstring = tagstring[:tagstring_len-3] + "..."

                fmt = "%%5d. %%-%ds %%-%ds" % (name_len, tagstring_len)
                print typeset(fmt % (n.get_id(), name, tagstring),
                              ANSI.Yellow, False)
                i += 1
                if i > rows-2:
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
        except Exception, e:
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

    def do_cls(self, args):
        os.system('clear')

    def do_copy(self, args):
        if self.hasxsel:
            ids = self.get_ids(args)
            if len(ids) > 1:
                print "Can copy only 1 password at a time..."
                return None
            try:
                node = self._db.getnodes(ids)
                text_to_clipboards(node[0].get_password())
                print "copied password for %s@%s clipboard... erasing in 10 sec..." % \
                (node[0].get_username(), node[0].get_url())
                time.sleep(10)
                text_to_clipboards("")
            except Exception, e:
                self.error(e)
        else:
            print "Can't copy to clipboard, no xsel found in the system!"

    def do_cp(self, args):
        self.do_copy(args)

    def do_open(self, args):
        ids = self.get_ids(args)
        if len(ids) > 1:
            print "Can open only 1 link at a time ..."
            return None
        try:
            node = self._db.getnodes(ids)
            url = node[0].get_url()
            open_url(url)
        except Exception, e:
            self.error(e)

    def do_o(self, args):
        self.do_open(args)
    ##
    ## Help functions
    ##
    def usage(self, string):
        print "Usage: %s" % (string)

    def help_open(self):
        self.usage("open <ID>")
        print "Launch default browser with 'xdg-open url',\n\
the url must contain http:// or https://."

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
        except Exception:
            pass

    def __init__(self, db, hasxsel):
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
            enc.set_callback(CLICallback())
            self._db = db
            self._db.open()
        except Exception, e:
            self.error(e)
            sys.exit(1)

        try:
            readline.read_history_file(self._historyfile)
        except IOError, e:
            pass

        self.prompt = "pwman> "



class PwmanCliMac(PwmanCli):
    """
    inherit from PwmanCli, override the right functions...
    """
    def do_copy(self, args):
        ids = self.get_ids(args)
        if len(ids) > 1:
            print "Can only 1 password at a time..."
        try:
            node = self._db.getnodes(ids)
            node[0].get_password()
            text_to_mcclipboard(node[0].get_password())
            print "copied password for %s@%s clipboard... erasing in 10 sec..." % \
            (node[0].get_username(), node[0].get_url())
            time.sleep(10)
            text_to_clipboards("")
        except Exception, e:
            self.error(e)

    def do_cp(self, args):
        self.do_copy(args)

    def do_open(self, args):
        ids = self.get_ids(args)
        if len(ids) > 1:
            print "Can open only 1 link at a time ..."
            return None
        try:
            node = self._db.getnodes(ids)
            url = node[0].get_url()
            open_url(url, macosx=True)
        except Exception, e:
            self.error(e)

    def do_o(self, args):
        self.do_open(args)

    ##
    ## Help functions
    ##
    def help_open(self):
        self.usage("open <ID>")
        print "Launch default browser with 'open url',\n\
the url must contain http:// or https://."

    def help_o(self):
        self.help_open()

    def help_copy(self):
        self.usage("copy <ID>")
        print "Copy password to Cocoa clipboard using pbcopy)"

    def help_cp(self):
        self.help_copy()

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

def gettermsize():
    s = struct.pack("HHHH", 0, 0, 0, 0)
    f = sys.stdout.fileno()
    x = fcntl.ioctl(f, termios.TIOCGWINSZ, s)
    rows, cols, width, height = struct.unpack("HHHH", x)
    return rows, cols

def getinput(question, default="", completer=None, width=_defaultwidth):
    if (not _readline_available):
        return raw_input(question.ljust(width))
    else:
        def defaulter(): 
            """define default behavior startup"""
            readline.insert_text(default)

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
                return a1
            a2 = getpass.getpass("[Repeat] %s" % (question.ljust(width)))
            if a1 == a2:
                return a1
            else:
                print "Passwords don't match. Try again."


def typeset(text, color, bold=False, underline=False):
    if not config.get_value("Global", "colors") == 'yes':
        return text
    if (bold):
        bold = "%d ;" % (ANSI.Bold)
    else:
        bold = ""
    if (underline):
        underline = "%d;" % (ANSI.Underscore)
    else:
        underline = ""
    return "\033[%s%s%sm%s\033[%sm" % (bold, underline, color,
                                       text, ANSI.Reset)

def select(question, possible):
    for i in range(0, len(possible)):
        print ("%d - %-"+str(_defaultwidth)+"s") % (i+1, possible[i])
    while 1:
        uinput = getonechar(question)
        if uinput.isdigit() and int(uinput) in range(1, len(possible)+1):
            return possible[int(uinput)-1]

def text_to_clipboards(text):
    """
    copy text to clipboard
    credit:
    https://pythonadventures.wordpress.com/tag/xclip/
    """
    # "primary":
    try:
        xsel_proc = sp.Popen(['xsel', '-pi'], stdin=sp.PIPE)
        xsel_proc.communicate(text)
        # "clipboard":
        xsel_proc = sp.Popen(['xsel', '-bi'], stdin=sp.PIPE)
        xsel_proc.communicate(text)
    except OSError, e:
        print e, "\nExecuting xsel failed, is it installed ?\n \
please check your configuration file ... "


def text_to_mcclipboard(text):
    """
    copy text to mac os x clip board
    credit:
    https://pythonadventures.wordpress.com/tag/xclip/
    """
    # "primary":
    try:
        pbcopy_proc = sp.Popen(['pbcopy'], stdin=sp.PIPE)
        pbcopy_proc.communicate(text)
    except OSError, e:
        print e, "\nExecuting pbcoy failed..."


def open_url(link, macosx=False):
    """
    launch xdg-open or open in MacOSX with url
    """
    uopen = "xdg-open"
    if macosx:
        uopen = "open"
    try:
        sp.Popen([uopen, link], stdin=sp.PIPE)
    except OSError, e:
        print "Executing open_url failed with:\n", e


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
            except (ValueError, IndexError):
                if (option.upper() == 'X'):
                    break
                print "Invalid selection"

class CliMenuItem(object):
    def __init__(self, name, editor, getter, setter):
        self.name = name
        self.editor = editor
        self.getter = getter
        self.setter = setter
