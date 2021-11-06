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
Windows UI components
"""

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
    #  ctypes.windll.kernel32.GlobalUnlock(pcontents)
    ctypes.windll.user32.CloseClipboard()
    return data


def winSetClipboard(text):

    GMEM_DDESHARE = 0x2000
    ctypes.windll.user32.OpenClipboard(0)
    ctypes.windll.user32.EmptyClipboard()
    hCd = ctypes.windll.kernel32.GlobalAlloc(GMEM_DDESHARE,
                                             len(bytes(text))+1)
    pchData = ctypes.windll.kernel32.GlobalLock(hCd)

    ctypes.cdll.msvcrt.strcpy(ctypes.c_char_p(pchData), bytes(text))

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
        node_id = self._db.get_node(args)
        node = self._db_entry_to_node(node_id)
        print(node)
        flushtimeout = self.config.get_value('Global', 'cls_timeout')
        flushtimeout = int(flushtimeout) if flushtimeout else 10

        if flushtimeout > 0:
            flushtimeout = flushtimeout or 10
            print("Type Enter to flush screen or wait %d sec. " % flushtimeout)

            _wait_until_enter(heardEnterWin, flushtimeout)
            self.do_cls('')

    def do_copy(self, args):
        ids = self._get_ids(args)
        if len(ids) > 1:
            print("Can copy only 1 password at a time...")
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
            winSetClipboard(b"")

    def do_cls(self, args):
        os.system('cls')
