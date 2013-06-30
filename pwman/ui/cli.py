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
import pwman
import pwman.exchange.importer as importer
import pwman.exchange.exporter as exporter
import pwman.util.generator as generator
from pwman.data.nodes import Node
from pwman.data.nodes import NewNode
from pwman.data.tags import Tag
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
from pwman.ui.tools import CliMenu
from pwman.ui.tools import CliMenuItem
from pwman.ui.tools import CLICallback
from colorama import Fore

try:
    import readline
    _readline_available = True
except ImportError, e:
    _readline_available = False


# pylint: disable=R0904
class PwmanCli(cmd.Cmd):
    """
    UI class for MacOSX
    """
    def error(self, exception):
        if (isinstance(exception, KeyboardInterrupt)):
            print
        else:
#            traceback.print_exc()
            print "Error: %s " % (exception)

    def do_EOF(self, args):
        return self.do_exit(args)

    def do_exit(self, args):
        """exit the ui"""
        print
        # try:
        #    print "goodbye"
        self._db.close()
        # except DatabaseException, e:
        #    self.error(e)
        return True

    def get_ids(self, args):
        ids = []
        rex = re.compile(r"^(\d+)-(\d+)$")
        idstrs = args.split()
        for i in idstrs:
            m = rex.match(i)
            if m is None:
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
        return tools.getinput("Enter filename: ", default)

    def get_username(self, default=""):
        return tools.getinput("Username: ", default)

    def get_password(self, argsgiven, numerics=False, leetify=False,
                     symbols=False, special_signs=False):
        """
        in the config file:
        numerics -> numerics
        leetify -> symbols
        special_chars -> special_signs
        """
        if argsgiven == 1:
            length = tools.getinput("Password length (default 7): ", "7")
            length = len(length)
            password, dumpme = generator.generate_password(length, length,
                                                           True, leetify,
                                                           numerics,
                                                           special_signs)
            print "New password: %s" % (password)
            return password
        # no args given
        password = tools.getpassword("Password (Blank to generate): ",
                                     tools._defaultwidth, False)
        if len(password) == 0:
            length = tools.getinput("Password length (default 7): ", "7")
            if length:
                length = int(length)
            else:
                length = 7
            password, dumpme = generator.generate_password(length, length,
                                                           True, leetify,
                                                           numerics,
                                                           special_signs)
        print "New password: %s" % (password)
        return password

    def get_url(self, default=""):
        return tools.getinput("Url: ", default)

    def get_notes(self, default=""):
        return tools.getinput("Notes: ", default)

    def get_tags(self, default=None):
        defaultstr = ''

        if default:
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

        taglist = tools.getinput("Tags: ", defaultstr, complete)
        tagstrings = taglist.split()
        tags = []
        for tn in tagstrings:
            tags.append(Tag(tn))
        return tags

    def print_node(self, node):
        width = str(tools._defaultwidth)
        print "Node %d." % (node.get_id())
        print ("%"+width+"s %s") % (tools.typeset("Username:", Fore.RED),
                                    node.get_username())
        print ("%"+width+"s %s") % (tools.typeset("Password:", Fore.RED),
                                    node.get_password())
        print ("%"+width+"s %s") % (tools.typeset("Url:", Fore.RED),
                                    node.get_url())
        print ("%"+width+"s %s") % (tools.typeset("Notes:", Fore.RED),
                                    node.get_notes())
        print tools.typeset("Tags: ", Fore.RED),
        for t in node.get_tags():
            print " %s \n" % t.get_name(),

        def heardEnter():
            inpt, out, err = uselect.select([sys.stdin], [], [], 0.0001)
            for stream in inpt:
                if stream == sys.stdin:
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

        flushtimeout = int(config.get_value("Global", "cls_timeout"))
        if flushtimeout > 0:
            print "Type Enter to flush screen (autoflash in "\
                  + "%d sec.)" % flushtimeout
            waituntil_enter(heardEnter, flushtimeout)

    def do_tags(self, arg):
        tags = self._db.listtags()
        if len(tags) > 0:
            tags[0].get_name()  # hack to get password request before output
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
                # when done with node erase it
                zerome(node._password)
            except Exception, e:
                self.error(e)

    def do_import(self, arg):
        try:
            args = arg.split()
            if len(args) == 0:
                types = importer.Importer.types()
                intype = tools.select("Select filetype:", types)
                imp = importer.Importer.get(intype)
                infile = tools.getinput("Select file:")
                imp.import_data(self._db, infile)
            else:
                for i in args:
                    types = importer.Importer.types()
                    intype = tools.select("Select filetype:", types)
                    imp = importer.Importer.get(intype)
                    imp.import_data(self._db, i)
        except Exception, e:
            self.error(e)

    def do_export(self, arg):
        try:
            nodes = self.get_ids(arg)

            types = exporter.Exporter.types()
            ftype = tools.select("Select filetype:", types)
            exp = exporter.Exporter.get(ftype)
            out_file = tools.getinput("Select output file:")
            if len(nodes) > 0:
                b = tools.getyesno("Export nodes %s?" % (nodes), True)
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
                b = tools.getyesno("Export all nodes%s?" % (tagstr), True)
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
        pwman> n {'leetify':False, 'numerics':True, 'special_chars':True}
        Password (Blank to generate):
        """
        errmsg = """could not parse config override, please input some"""\
                 + """ kind of dictionary, e.g.: n {'leetify':False, """\
                 + """'numerics':True, 'special_chars':True}"""
        try:
            username = self.get_username()
            if args:
                try:
                    args = ast.literal_eval(args)
                except Exception:
                    raise Exception(errmsg)
                if not isinstance(args, dict):
                    raise Exception(errmsg)
                password = self.get_password(1, **args)
            else:
                numerics = config.get_value("Generator",
                                            "numerics").lower() == 'true'
                # TODO: allow custom leetifying through the config
                leetify = config.get_value("Generator",
                                           "leetify").lower() == 'true'
                special_chars = config.get_value("Generator",
                                                 "special_chars").lower() == \
                    'true'
                password = self.get_password(0,
                                             numerics=numerics,
                                             symbols=leetify,
                                             special_signs=special_chars)
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
                b = tools.getyesno("Are you sure you want to delete '%s@%s'?"
                                   % (n.get_username(), n.get_url()), False)
                if b is True:
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
                rows, cols = tools.gettermsize()
            else:
                rows, cols = 18, 80
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
                print tools.typeset(fmt % (n.get_id(), name, tagstring),
                                    Fore.YELLOW, False)
                i += 1
                if i > rows-2:
                    i = 0
                    c = tools.getonechar("Press <Space> for more, "
                                         "or 'Q' to cancel")
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
                tools.text_to_clipboards(node[0].get_password())
                print "copied password for {}@{} clipboard".format(
                    node[0].get_username(), node[0].get_url())

                print "erasing in 10 sec..."
                time.sleep(10)
                tools.text_to_clipboards("")
            except Exception, e:
                self.error(e)
        else:
            print "Can't copy to clipboard, no xsel found in the system!"

    def do_cp(self, args):
        self.do_copy(args)

    def do_open(self, args):
        ids = self.get_ids(args)
        if not args:
            self.help_open()
            return
        if len(ids) > 1:
            print "Can open only 1 link at a time ..."
            return None
        try:
            node = self._db.getnodes(ids)
            url = node[0].get_url()
            tools.open_url(url)
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
        _dbwarning = "\n*** WARNNING: You are using the old database format" \
            + " which is unsecure." \
            + " It's highly recommended to switch to the new database " \
            + "format." \
            + " Check the help (pwman3 -h) or look at the manpage which" \
            + " explains how to proceed. ***"

        cmd.Cmd.__init__(self)
        self.intro = "%s %s (c) visit: %s %s" % (pwman.appname, pwman.version,
                                                 pwman.website, _dbwarning)
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
        self.prompt = "!pwman> "


class PwmanCliNew(PwmanCli):
    """
    inherit from the old class, override
    all the methods related to tags, and
    newer Node format, so backward compatability is kept...
    """

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

    def print_node(self, node):
        width = str(tools._defaultwidth)
        print "Node %d." % (node.get_id())
        print ("%"+width+"s %s") % (tools.typeset("Username:", Fore.RED),
                                    node.get_username())
        print ("%"+width+"s %s") % (tools.typeset("Password:", Fore.RED),
                                    node.get_password())
        print ("%"+width+"s %s") % (tools.typeset("Url:", Fore.RED),
                                    node.get_url())
        print ("%"+width+"s %s") % (tools.typeset("Notes:", Fore.RED),
                                    node.get_notes())
        print tools.typeset("Tags: ", Fore.RED),
        for t in node.get_tags():
            print " %s " % t
        print

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

        flushtimeout = int(config.get_value("Global", "cls_timeout"))
        if flushtimeout > 0:
            print "Type Enter to flush screen (autoflash in "\
                  + "%d sec.)" % flushtimeout
            waituntil_enter(heardEnter, flushtimeout)

    def do_tags(self, arg):
        tags = self._db.listtags()
        # request password
        enc = CryptoEngine.get()
        if not enc.alive():
            enc._getcipher()
        print "Tags: ",
        if len(tags) == 0:
            print "None",
        for t in tags:
            print "%s " % t,
        print

    def get_tags(self, default=None):
        defaultstr = ''

        if default:
            for t in default:
                defaultstr += "%s " % (t)
        else:
            tags = self._db.currenttags()
            for t in tags:
                defaultstr += "%s " % (t)

        strings = []
        tags = self._db.listtags(True)
        for t in tags:
            # strings.append(t.get_name())
            strings.append(t)

        def complete(text, state):
            count = 0
            for s in strings:
                if s.startswith(text):
                    if count == state:
                        return s
                    else:
                        count += 1

        taglist = tools.getinput("Tags: ", defaultstr, complete)
        tagstrings = taglist.split()
        tags = []
        for tn in tagstrings:
            _Tag = Tag(tn)
            tags.append(_Tag)
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
                tags = n.get_tags()
                tags = filter(None, tags)
                tagstring = ''
                first = True
                for t in tags:
                    if not first:
                        tagstring += ", "
                    else:
                        first = False
                    tagstring += t

                name = "%s@%s" % (n.get_username(), n.get_url())

                name_len = cols * 2 / 3
                tagstring_len = cols / 3
                if len(name) > name_len:
                    name = name[:name_len-3] + "..."
                if len(tagstring) > tagstring_len:
                    tagstring = tagstring[:tagstring_len-3] + "..."
                fmt = "%%5d. %%-%ds %%-%ds" % (name_len, tagstring_len)
                formatted_entry = tools.typeset(fmt % (n.get_id(),
                                                name, tagstring),
                                                Fore.YELLOW, False)
                print formatted_entry
                i += 1
                if i > rows-2:
                    i = 0
                    c = tools.getonechar("Press <Space> for more,"
                                         " or 'Q' to cancel")
                    if c == 'q':
                        break

        except Exception, e:
            self.error(e)

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

    def do_new(self, args):
        """
        can override default config settings the following way:
        Pwman3 0.2.1 (c) visit: http://github.com/pwman3/pwman3
        pwman> n {'leetify':False, 'numerics':True, 'special_chars':True}
        Password (Blank to generate):
        """
        errmsg = """could not parse config override, please input some"""\
                 + """ kind of dictionary, e.g.: n {'leetify':False, """\
                 + """'numerics':True, 'special_chars':True}"""
        try:
            username = self.get_username()
            if args:
                try:
                    args = ast.literal_eval(args)
                except Exception:
                    raise Exception(errmsg)
                if not isinstance(args, dict):
                    raise Exception(errmsg)
                password = self.get_password(1, **args)
            else:
                numerics = config.get_value(
                    "Generator", "numerics").lower() == 'true'
                # TODO: allow custom leetifying through the config
                leetify = config.get_value(
                    "Generator", "leetify").lower() == 'true'
                special_chars = config.get_value(
                    "Generator", "special_chars").lower() == 'true'
                password = self.get_password(0,
                                             numerics=numerics,
                                             symbols=leetify,
                                             special_signs=special_chars)
            url = self.get_url()
            notes = self.get_notes()
            node = NewNode(username, password, url, notes)
            tags = self.get_tags()
            node.set_tags(tags)
            self._db.addnodes([node])
            print "Password ID: %d" % (node.get_id())
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
