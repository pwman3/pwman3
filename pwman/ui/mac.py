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
# pylint: disable=I0011
from __future__ import print_function

import time
# all mac os  related classes
from pwman.ui.cli import PwmanCli
from pwman.ui import tools
from pwman.util.crypto_engine import CryptoEngine

# pylint: disable=R0904


class PwmanCliMac(PwmanCli):
    """
    inherit from PwmanCli, override the right functions...
    """
    def do_copy(self, args):
        ids = self._get_ids(args)
        if len(ids) > 1:
            print("Can only 1 password at a time...")
            return None

        nodes = self._db.getnodes(ids)
        ce = CryptoEngine.get()

        for node in nodes:
            password = ce.decrypt(node[2])
            tools.text_to_mcclipboard(password)
            flushtimeout = self.config.get_value('Global', 'cp_timeout')
            flushtimeout = flushtimeout or 10
            print("erasing in {} sec...".format(flushtimeout))
            time.sleep(int(flushtimeout))
            tools.text_to_mcclipboard("")

    def do_open(self, args):
        ids = self._get_ids(args)
        if not args:
            self.help_open()
            return
        if len(ids) > 1:
            print("Can open only 1 link at a time ...")
            return None

        ce = CryptoEngine.get()
        nodes = self._db.getnodes(ids)

        for node in nodes:
            url = ce.decrypt(node[3])
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            tools.open_url(url, macosx=True)
