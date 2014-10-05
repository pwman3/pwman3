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
import os
import pkg_resources
import argparse

appname = "pwman3"
try:
    version = pkg_resources.get_distribution('pwman3').version
except pkg_resources.DistributionNotFound:  # pragma: no cover
    version = "0.5.3"

website = "http://pwman3.github.io/pwman3/"
author = "Oz Nahum Tiram"
authoremail = "nahumoz@gmail.com"
description = "Pwman - a command line password management application."
keywords = "password management sqlite crypto"


def which(cmd):
    _, cmdname = os.path.split(cmd)

    for path in os.environ["PATH"].split(os.pathsep):
        cmd = os.path.join(path, cmdname)
        if os.path.isfile(cmd) and os.access(cmd, os.X_OK):  # pragma: no cover
            return cmd

config_dir = os.path.expanduser("~/.pwman")

default_config = {'Global': {'umask': '0100', 'colors': 'yes',
                             'cls_timeout': '5',
                             'save': 'True'
                             },
                  'Database': {'type': 'SQLite',
                               'filename': os.path.join(config_dir,
                                                        "pwman.db")},
                  'Encryption': {'algorithm': 'AES'},
                  'Readline': {'history': os.path.join(config_dir,
                                                       "history")}
                  }


def parser_options():
    parser = argparse.ArgumentParser(description=('pwman3 - a command line '
                                                  'password manager.'))
    parser.add_argument('-c', '--config', dest='cfile',
                        default=os.path.expanduser("~/.pwman/config"),
                        help='cofiguration file to read')
    parser.add_argument('-d', '--database', dest='dbase')
    parser.add_argument('-e', '--encryption', dest="algo",
                        help=("Possible options are: AES(default), ARC2, ARC4,"
                              " Blowfish, CAST, DES, DES3, IDEA, RC5"))
    parser.add_argument('-k', '--convert', dest='dbconvert',
                        action='store_true', default=False,
                        #  ^:os.path.expanduser('~/.pwman/pwman.db'),
                        help=("Convert old DB format to version >= 0.4."
                              " The database that will be converted is the"
                              " one found in the config file, or the one given"
                              " as command line argument."))
    parser.add_argument('-O', '--output', dest='output',
                        # default=os.path.expanduser('~/.pwman/pwman-newdb.db'),
                        help=("The name of the newly created database after "
                              "converting."))
    return parser
