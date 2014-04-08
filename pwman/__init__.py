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
import pkg_resources

appname = "Pwman3"
try:
    version = pkg_resources.get_distribution('pwman3').version
except pkg_resources.DistributionNotFound:  # pragma: no cover
    version = "0.5"

website = "http://github.com/pwman3/pwman3"
author = "Oz Nahum"
authoremail = "nahumoz@gmail.com"
description = "Pwman -a command line password management application."
keywords = "password management sqlite crypto"


def which(cmd):
    _, cmdname = os.path.split(cmd)

    for path in os.environ["PATH"].split(os.pathsep):
        cmd = os.path.join(path, cmdname)
        if os.path.isfile(cmd) and os.access(cmd, os.X_OK):  # pragma: no cover
            return cmd

config_dir = os.path.expanduser("~/.pwman")

default_config = {'Global': {'umask': '0100', 'colors': 'yes',
                             'cls_timeout': '5'
                             },
                  'Database': {'type': 'SQLite',
                               'filename': os.path.join(config_dir,
                                                        "pwman.db")},
                  'Encryption': {'algorithm': 'AES'},
                  'Readline': {'history': os.path.join(config_dir,
                                                       "history")}
                  }
