"""
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
# Copyright (C) 2012-2014 Oz Nahum Tiram <nahumoz@gmail.com>
# ============================================================================
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
# ============================================================================
"""
from __future__ import print_function
import ctypes
import os
import time

try:
    import msvcrt
except ImportError:
    pass

import colorama

from pwman.ui.cli import PwmanCli
from pwman.util.crypto_engine import CryptoEngine


colorama.init()


def heardEnterWin():
    c = msvcrt.kbhit()
    if c == 1:
        ret = msvcrt.getch()
        if ret is not None:
            return True
    return False


def _wait_until_enter(predicate, timeout, period=0.25):  # pragma: no cover
    mustend = time.time() + timeout
    while time.time() < mustend:
        cond = predicate()
        if cond:
            break
        time.sleep(period)


def winGetClipboard():
    ctypes.windll.user32.OpenClipboard(0)
    pcontents = ctypes.windll.user32.GetClipboardData(1)  # 1 is CF_TEXT
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
        hCd = ctypes.windll.kernel32.GlobalAlloc(GMEM_DDESHARE,
                                                 len(bytes(text))+1)
    except TypeError:
        # works on Python 3 (bytes() requires an encoding)
        hCd = ctypes.windll.kernel32.GlobalAlloc(GMEM_DDESHARE,
                                                 len(bytes(text, 'ascii'))+1)
    pchData = ctypes.windll.kernel32.GlobalLock(hCd)
    try:
        # works on Python 2 (bytes() only takes one argument)
        ctypes.cdll.msvcrt.strcpy(ctypes.c_char_p(pchData), bytes(text))
    except TypeError:
        # works on Python 3 (bytes() requires an encoding)
        ctypes.cdll.msvcrt.strcpy(ctypes.c_char_p(pchData),
                                  bytes(text, 'ascii'))
    ctypes.windll.kernel32.GlobalUnlock(hCd)
    ctypes.windll.user32.SetClipboardData(1, hCd)
    ctypes.windll.user32.CloseClipboard()


class PwmanCliWin(PwmanCli):
    """
    windows ui class
    """
    def do_print(self, args):
        if not args.isdigit():
            print("print accepts only a single ID ...")
            return
        nodes = self._db.getnodes([args])
        node = self._db_entries_to_nodes(nodes)[0]
        print(node)
        flushtimeout = self.config.get_value('Global', 'cls_timeout')
        flushtimeout = flushtimeout or 10

        print("Type Enter to flush screen or wait %s sec. " % flushtimeout)

        _wait_until_enter(heardEnterWin, float(flushtimeout))
        self.do_cls('')

    def do_copy(self, args):
        ids = self._get_ids(args)
        if len(ids) > 1:
            print ("Can copy only 1 password at a time...")
            return None

        ce = CryptoEngine.get()
        nodes = self._db.getnodes(ids)

        for node in nodes:
            password = ce.decrypt(node[2])
            winSetClipboard(password)
            flushtimeout = self.config.get_value('Global', 'cp_timeout')
            flushtimeout = flushtimeout or 10
            print("erasing in {} sec...".format(flushtimeout))
            time.sleep(int(flushtimeout))
            winSetClipboard("")

    def do_open(self, args):
        ids = self._get_ids(args)
        if not args:
            self.help_open()
            return
        if len(ids) > 1:
            print ("Can open only 1 link at a time ...")
            return None

        ce = CryptoEngine.get()
        nodes = self._db.getnodes(ids)

        for node in nodes:
            url = ce.decrypt(node[3])
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            os.system("start "+url)

    def do_cls(self, args):
        os.system('cls')
