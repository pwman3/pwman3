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
# Copyright (C) 2012, 2013, 2014, 2015 Oz Nahum <nahumoz@gmail.com>
# ============================================================================
# pylint: disable=I0011

from __future__ import print_function

import cmd
import os
import sys


if sys.version_info.major > 2:
    raw_input = input

try:
    import readline
    _readline_available = True
except ImportError as e:  # pragma: no cover
    import pyreadline as readline
    _readline_available = True


from pwman.ui.baseui import BaseCommands
from pwman import (get_conf_options, get_db_version, version, website, parser_options)
from pwman.ui.tools import CLICallback
from pwman.data import factory
from pwman.exchange.importer import Importer
from pwman.util.crypto_engine import CryptoEngine
from pwman.util.crypto_engine import AES

class PwmanCli(cmd.Cmd, BaseCommands):
    """
    Inherit from the BaseCommands and Aliases
    """

    undoc_header = "Aliases:"

    def __init__(self, db, hasxsel, callback, config_parser, **kwargs):
        """
        initialize CLI interface, set up the DB
        connecion, see if we have xsel ...
        """
        super(PwmanCli, self).__init__(**kwargs)
        self.intro = "%s %s (c) visit: %s" % ('pwman3', version, website)
        self._historyfile = config_parser.get_value("Readline", "history")
        self.hasxsel = hasxsel
        self.config = config_parser

        try:
            enc = CryptoEngine.get()
            enc.callback = callback()
            self._db = db
            #  this cascades down all the way to setting the database key
            self._db.open()
        except Exception as e:  # pragma: no cover
            self.error(e)
            sys.exit(1)

        try:
            readline.read_history_file(self._historyfile)
        except IOError as e:  # pragma: no cover
            pass

        self.prompt = "pwman> "


def get_ui_platform(platform):  # pragma: no cover
    if 'darwin' in platform:
        from pwman.ui.mac import PwmanCliMac as PwmanCli
        OSX = True
    elif 'win' in platform:
        from pwman.ui.win import PwmanCliWin as PwmanCli
        OSX = False
    else:
        from pwman.ui.cli import PwmanCli
        OSX = False

    return PwmanCli, OSX


def main():
    args = parser_options().parse_args()
    PwmanCli, OSX = get_ui_platform(sys.platform)
    xselpath, dbtype, config = get_conf_options(args, OSX)
    dburi = config.get_value('Database', 'dburi')

    if os.path.join("Crypto", "Cipher") not in AES.__file__:  # we are using built in AES.py
        import colorama
        if config.get_value('Crypto', 'supress_warning').lower() != 'yes':
            print("{}WARNING: You are not using PyCrypto!!!\n"
                  "WARNING: You should install PyCrypto for better security and "
                  "perfomance\nWARNING: You can supress this warning by editing "
                  "pwman config file.{}".format(colorama.Fore.RED,
                                                colorama.Style.RESET_ALL))

    print(dburi)
    dbver = get_db_version(config, args)
    CryptoEngine.get()

    db = factory.createdb(dburi, dbver)

    if args.file_delim:
        importer = Importer((args, config, db))
        importer.run()
        sys.exit(0)

    cli = PwmanCli(db, xselpath, CLICallback, config)

    try:
        cli.cmdloop()
    except KeyboardInterrupt as e:
        print(e)
    finally:
        config.save()
