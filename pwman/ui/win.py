""""
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


from pwman.ui.cli import PwmanCliNew
from pwman.data.nodes import NewNode
from pwman.ui import tools
import time
import msvcrt
import pwman.util.config as config
import ast
from pwman.util.crypto import zerome
from colorama import Fore


class PwmanCliWinNew(PwmanCliNew):
    """
    windows ui class
    """
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
            node.tags = tags
            self._db.addnodes([node])
            print "Password ID: %d" % (node._id)
            # when done with node erase it
            zerome(password)
        except Exception, e:
            self.error(e)

    def print_node(self, node):
        width = str(tools._defaultwidth)
        print "Node %d." % (node.get_id())
        print ("%" + width+"s %s") % (tools.typeset("Username:", Fore.RED),
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

        def heardEnterWin():
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
            print "Press any key to flush screen (autoflash "\
                + "in %d sec.)" % flushtimeout
            waituntil_enter(heardEnterWin, flushtimeout)
