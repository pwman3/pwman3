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
# Copyright (C) 2013, 2014 Oz Nahum Tiram <nahumoz@gmail.com>
# ============================================================================
from __future__ import print_function
from pwman.util.crypto_engine import CryptoEngine, zerome
import re
import sys
import os
import time
import select as uselect
import ast
from pwman.util.config import get_pass_conf
from pwman.ui import tools
from pwman.ui.tools import CliMenuItem
from colorama import Fore
from pwman.data.nodes import NewNode, Node
from pwman.ui.tools import CMDLoop
import getpass
from pwman.data.tags import TagNew
import csv

if sys.version_info.major > 2:
    raw_input = input

from base import HelpUI


class BaseCommands(HelpUI):

    def do_copy(self, args):
        """copy item to clipboard"""
        pass

    def do_exit(self, args):
        """close the text console"""
        pass

    def do_export(self, args):
        """export the database to a given format"""
        pass

    def do_forget(self, args):
        """drop saved key forcing the user to re-enter the master
        password"""
        pass

    def do_cls(self, args):
        """clear the screen"""
        pass

    def do_edit(self, args):
        """edit a node"""
        pass

    def do_clear(self, args):
        """remove db filter"""
        pass

    def do_passwd(self, args):
        """change the master password of the database"""
        pass

    def do_tags(self, args):
        """print all existing tags """


