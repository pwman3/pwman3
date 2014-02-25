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
from __future__ import print_function
import pwman
from pwman.util.crypto import CryptoEngine
import pwman.util.config as config
import sys
import cmd
from pwman.ui.base import Aliases, BaseCommands

try:
    import readline
    _readline_available = True
except ImportError, e:  # pragma: no cover
    _readline_available = False


class PwmanCliNew(cmd.Cmd, Aliases, BaseCommands):
    """
    Inherit from the BaseCommands and Aliases
    """
    def __init__(self, db, hasxsel, callback):
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
            enc._callback = callback()
            self._db = db
            #  this cascades down all the way to setting the database key
            self._db.open()
        except Exception, e:  # pragma: no cover
            self.error(e)
            sys.exit(1)

        try:
            readline.read_history_file(self._historyfile)
        except IOError, e:  # pragma: no cover
            pass

        self.prompt = "pwman> "
