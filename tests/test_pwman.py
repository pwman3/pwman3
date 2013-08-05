#!/usr/bin/env python
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
import os
import os.path

import sys
sys.path.insert(0, os.getcwd())
_saveconfig = True

import sys
from pwman.util.crypto import CryptoEngine

if 'darwin' in sys.platform:
    from pwman.ui.mac import PwmanCliMac as PwmanCli
    from pwman.ui.mac import PwmanCliMacNew as PwmanCliNew
    OSX = True
elif 'win' in sys.platform:
    from pwman.ui.cli import PwmanCli
    from pwman.ui.win import PwmanCliWinNew as PwmanCliNew
    OSX = False
else:
    from pwman.ui.cli import PwmanCli
    from pwman.ui.cli import PwmanCliNew
    OSX = False


import pwman.util.config as config
import pwman.data.factory
from pwman.data.convertdb import PwmanConvertDB


def which(cmd):
    _, cmdname = os.path.split(cmd)

    for path in os.environ["PATH"].split(os.pathsep):
        cmd = os.path.join(path, cmdname)
        if os.path.isfile(cmd) and os.access(cmd, os.X_OK):
            return cmd

    return None

try:
    # set cls_timout to negative number (e.g. -1) to disable
    default_config = {'Global': {'umask': '0100', 'colors': 'yes',
                                 'cls_timeout': '5'
                                 },
                      'Database': {'type': 'SQLite',
                                   'filename': os.path.join("tests",
                                                            "test.pwman.db")},
                      'Encryption': {'algorithm': 'AES'},
                      'Readline': {'history': os.path.join("tests",
                                                           "history")}
                      }
    config.set_defaults(default_config)
    if 'win' in sys.platform:
        try:
            import colorama
            colorama.init()
        except ImportError:
            config.set_value("Global", "colors", 'no')
    if not OSX:
        xselpath = which("xsel")
        config.set_value("Global", "xsel", xselpath)
    elif OSX:
        pbcopypath = which("pbcopy")
        config.set_value("Global", "xsel", pbcopypath)
    # set umask before creating/opening any files
    umask = int(config.get_value("Global", "umask"))
    os.umask(umask)

    enc = CryptoEngine.get()

    dbtype = config.get_value("Database", "type")
    # if it is done here, we could do the following:
    # if db.ver == 0.4 :
    #     db = pwman.data.factory.create(dbtyp, new_version)
    # else:
    #     we use the old code untouched ... insecure, but
    #     keeps backwards compatibility ...
    # if the database file exists check it's version
    # else: force version 0.4
    if os.path.exists(config.get_value("Database", "filename")):
        dbver = pwman.data.factory.check_db_version(dbtype)
        dbver = float(dbver.strip("\'"))
    else:
        dbver = 0.4
    # the method create could create an old instance that
    # accepts cPickle object or new style instance that
    # accepts only strings.
    # The user should be STRONGLY Prompted to CONVERT the
    # database to the new format using a command line tool.
    # version 0.5 pwman will depreciate that old and insecure
    # code ...

    db = pwman.data.factory.create(dbtype, dbver)
    if dbver >= 0.4:
        cli = PwmanCliNew(db, xselpath)
    elif dbver < 0.4:
        cli = PwmanCli(db, xselpath)
except SystemExit, e:
    sys.exit(e)


import unittest
from db_tests import CLITests
from db_tests import DBTests
if __name__ == '__main__':
    unittest.main()
