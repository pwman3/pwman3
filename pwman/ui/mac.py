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
# pylint: disable=I0011

"all mac os  related classes"
from pwman.ui.cli import PwmanCliNew
from pwman.ui import tools
import time

# pylint: disable=R0904


class PwmanCliMac(PwmanCliNew):
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
            tools.text_to_mcclipboard(node[0].get_password())
            print "copied password for {}@{} clipboard".format(
                node[0].get_username(), node[0].get_url())
            time.sleep(10)
            tools.text_to_clipboards("")
        except Exception, e:
            self.error(e)

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
            tools.open_url(url, macosx=True)
        except Exception, e:
            self.error(e)

    def do_o(self, args):
        self.do_open(args)

    ##
    # Help functions
    ##
    def help_open(self):
        self.usage("open <ID>")
        print "Launch default browser with 'open url',\n" \
              + "the url must contain http:// or https://."

    def help_o(self):
        self.help_open()

    def help_copy(self):
        self.usage("copy <ID>")
        print "Copy password to Cocoa clipboard using pbcopy"

    def help_cp(self):
        self.help_copy()


class PwmanCliMacNew(PwmanCliMac):
    pass
