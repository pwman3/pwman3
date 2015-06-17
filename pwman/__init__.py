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
# Copyright (C) 2012 Oz Nahum Tiram <nahumoz@gmail.com>
# ============================================================================
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
# ============================================================================
import os
import argparse
import sys
import re
import colorama
import pkg_resources
from pwman.util import config
from pwman.data.factory import check_db_version

appname = "pwman3"

try:
    version = pkg_resources.get_distribution('pwman3').version
except pkg_resources.DistributionNotFound:  # pragma: no cover
    version = "0.7.1"

website = "http://pwman3.github.io/pwman3/"
author = "Oz Nahum Tiram"
authoremail = "nahumoz@gmail.com"
description = "a command line password manager with support for multiple databases."
keywords = "password management sqlite crypto"
long_description = u"""
Pwman3 aims to provide a simple but powerful commandline interface for
password management.
It allows one to store passwords in database locked by master password which
is AES encrypted.
Pwman3 supports MySQL, Postgresql and SQLite"""


def which(cmd):  # pragma: no cover
    _, cmdname = os.path.split(cmd)

    for path in os.environ["PATH"].split(os.pathsep):
        cmd = os.path.join(path, cmdname)
        if os.path.isfile(cmd) and os.access(cmd, os.X_OK):  # pragma: no cover
            return cmd
    return ''

config_dir = os.path.expanduser("~/.pwman")


def parser_options(formatter_class=argparse.HelpFormatter):  # pragma: no cover
    parser = argparse.ArgumentParser(prog=appname,
                                     description=description,
                                     formatter_class=formatter_class)
    parser.add_argument('-c', '--config', dest='cfile',
                        default=os.path.expanduser("~/.pwman/config"),
                        help='cofiguration file to read')
    parser.add_argument('-d', '--database', dest='dbase')
    parser.add_argument('-i', '--import', dest='import_file',
                        type=argparse.FileType())
    return parser


def get_conf(args):
    config_dir = os.path.expanduser("~/.pwman")

    if not os.path.isdir(config_dir):  # pragma: no cover
        os.mkdir(config_dir)

    configp = config.Config(args.cfile, config.default_config)
    return configp


def set_xsel(configp, OSX):
    if not OSX:
        xselpath = which("xsel")
        configp.set_value("Global", "xsel", xselpath)
    elif OSX:
        pbcopypath = which("pbcopy")
        configp.set_value("Global", "xsel", pbcopypath)


def set_win_colors(config):  # pragma: no cover
    if 'win' in sys.platform:
        colorama.init()


def set_umask(configp):
    umask = configp.get_value("Global", "umask")
    if re.search(r'^\d{4}$', umask):
        os.umask(int(umask))


def set_db(args, configp):
    if args.dbase:
        configp.set_value("Database", "dburi", args.dbase)
        configp.set_value("Global", "save", "False")


def get_conf_options(args, OSX):
    configp = get_conf(args)
    xselpath = configp.get_value("Global", "xsel")
    if not xselpath:  # pragma: no cover
        set_xsel(configp, OSX)

    set_win_colors(configp)
    set_db(args, configp)
    set_umask(configp)
    dburi = configp.get_value("Database", "dburi")
    return xselpath, dburi, configp


def get_db_version(config, args):
    dburi = check_db_version(config.get_value("Database", "dburi"))
    return dburi
