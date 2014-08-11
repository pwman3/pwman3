""""
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
# Copyright (C) 2012 Oz Nahum <nahumoz@gmail.com>
# ============================================================================
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
# ============================================================================
"""
from __future__ import print_function
import time
import ctypes
import ast
import os
try:
    import msvcrt
except ImportError:
    pass

from colorama import Fore
import pwman.util.config as config
from pwman.ui.cli import PwmanCliNew
from pwman.data.nodes import NewNode
from pwman.ui import tools
from pwman.util.crypto_engine import zerome


def winGetClipboard():
    ctypes.windll.user32.OpenClipboard(0)
    pcontents = ctypes.windll.user32.GetClipboardData(1) # 1 is CF_TEXT
    data = ctypes.c_char_p(pcontents).value
    #ctypes.windll.kernel32.GlobalUnlock(pcontents)
    ctypes.windll.user32.CloseClipboard()
    return data

def winSetClipboard(text):
    text = str(text)
    GMEM_DDESHARE = 0x2000
    ctypes.windll.user32.OpenClipboard(0)
    ctypes.windll.user32.EmptyClipboard()
    try:
        # works on Python 2 (bytes() only takes one argument)
        hCd = ctypes.windll.kernel32.GlobalAlloc(GMEM_DDESHARE, len(bytes(text))+1)
    except TypeError:
        # works on Python 3 (bytes() requires an encoding)
        hCd = ctypes.windll.kernel32.GlobalAlloc(GMEM_DDESHARE, len(bytes(text, 'ascii'))+1)
    pchData = ctypes.windll.kernel32.GlobalLock(hCd)
    try:
        # works on Python 2 (bytes() only takes one argument)
        ctypes.cdll.msvcrt.strcpy(ctypes.c_char_p(pchData), bytes(text))
    except TypeError:
        # works on Python 3 (bytes() requires an encoding)
        ctypes.cdll.msvcrt.strcpy(ctypes.c_char_p(pchData), bytes(text, 'ascii'))
    ctypes.windll.kernel32.GlobalUnlock(hCd)
    ctypes.windll.user32.SetClipboardData(1, hCd)
    ctypes.windll.user32.CloseClipboard()

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
            node = NewNode()
            node.username = username
            node.password = password
            node.url = url
            node.notes = notes
            tags = self.get_tags()
            node.tags = tags
            self._db.addnodes([node])
            print("Password ID: %d" % (node._id))
            # when done with node erase it
            zerome(password)
        except Exception as e:
            self.error(e)

    def print_node(self, node):
        width = tools._defaultwidth
        print("Node {}.".format(node._id))
        print("{} {}".format(tools.typeset("Username:", Fore.RED).ljust(width),
                             node.username))
        print ("{} {}".format(tools.typeset("Password:", Fore.RED).ljust(width),
                              node.password))
        print("{} {}".format(tools.typeset("Url:", Fore.RED).ljust(width), node.url))
        print("{} {}".format(tools.typeset("Notes:", Fore.RED).ljust(width), node.notes))
        print("{}".format(tools.typeset("Tags: ", Fore.RED)), end=" ")
        for t in node.tags:
            print(t)

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
            print("Press any key to flush screen (autoflash "
                  "in %d sec.)" % flushtimeout)
            waituntil_enter(heardEnterWin, flushtimeout)

    def do_copy(self, args):
        ids = self.get_ids(args)
        if len(ids) > 1:
            print ("Can copy only 1 password at a time...")
            return None
        try:
            node = self._db.getnodes(ids)
            winSetClipboard(node[0].password)
            print("copied password for {}@{} clipboard".format(
                  node[0].username, node[0].url))
            print("erasing in 10 sec...")
            time.sleep(10)
            winSetClipboard("")
        except Exception as e:
            self.error(e)

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
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            os.system("start "+url)
        except Exception as e:
            self.error(e)

    def do_cls(self, args):
        os.system('cls')
