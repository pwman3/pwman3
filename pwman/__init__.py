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
import os
import pkg_resources
import argparse
from pwman.util import config
import sys
import re
from pwman.data import factory
from pwman.data.database import __DB_FORMAT__
import colorama

appname = "pwman3"


try:
    version = pkg_resources.get_distribution('pwman3').version
except pkg_resources.DistributionNotFound:  # pragma: no cover
    version = u"0.5"

website = "http://pwman3.github.io/pwman3/"
author = "Oz Nahum"
authoremail = "nahumoz@gmail.com"
description = "a command line password management application."
keywords = "password management sqlite crypto"
long_description = (u"Pwman3 aims to provide a simple but powerful command "
                    "line interface for password management.\nIt allows one "
                    "to store your password in a SQLite database locked by "
                    "a\nmaster password which can be encrypted with different "
                    "algorithms (e.g AES, Blowfish, DES3, IDEA, etc.).")

_db_warn = (u"pwman3 detected that you are using the old database format"
            " which is insecure."
            " pwman3 will try to automatically convert the database now."
            "\n"
            "If you choose not to convert the database, pwman3, will quit."
            "\nYou can check the help (pwman3 -h) or look at the manpage how "
            "to convert the database manually."
            )


def which(cmd):
    _, cmdname = os.path.split(cmd)

    for path in os.environ["PATH"].split(os.pathsep):
        cmd = os.path.join(path, cmdname)
        if os.path.isfile(cmd) and os.access(cmd, os.X_OK):  # pragma: no cover
            return cmd
    return ''

config_dir = os.path.expanduser("~/.pwman")

default_config = {'Global': {'umask': '0100', 'colors': 'yes',
                             'cls_timeout': '5',
                             'save': 'True'
                             },
                  'Database': {'type': 'SQLite',
                               'filename': os.path.join(config_dir,
                                                        "pwman.db")},
                  'Readline': {'history': os.path.join(config_dir,
                                                       "history")}
                  }


def parser_options(formatter_class=argparse.HelpFormatter):
    parser = argparse.ArgumentParser(prog=appname,
                                     description=description,
                                     formatter_class=formatter_class)
    parser.add_argument('-c', '--config', dest='cfile',
                        default=os.path.expanduser("~/.pwman/config"),
                        help='cofiguration file to read')
    parser.add_argument('-d', '--database', dest='dbase')
    return parser


def get_conf(args):
    config_dir = os.path.expanduser("~/.pwman")

    if not os.path.isdir(config_dir):  # pragma: no cover
        os.mkdir(config_dir)

    configp = config.Config(args.cfile, default_config)
    return configp


def set_xsel(config, OSX):
    if not OSX:
        xselpath = which("xsel")
        config.set_value("Global", "xsel", xselpath)
    elif OSX:
        pbcopypath = which("pbcopy")
        config.set_value("Global", "xsel", pbcopypath)


def set_win_colors(config):  # pragma: no cover
    if 'win' in sys.platform:
        colorama.init()


def set_umask(config):
    umask = config.get_value("Global", "umask")
    if re.search(r'^\d{4}$', umask):
        os.umask(int(umask))
    else:
        raise config.ConfigException("Could not determine umask from config!")


def set_db(args, configp):
    if args.dbase:
        configp.set_value("Database", "filename", args.dbase)
        configp.set_value("Global", "save", "False")


def get_conf_options(args, OSX):
    configp = get_conf(args)
    xselpath = configp.get_value("Global", "xsel")
    if not xselpath:
        set_xsel(configp, OSX)

    set_win_colors(configp)
    set_db(args, configp)
    set_umask(configp)
    dbtype = configp.get_value("Database", "type")
    if not dbtype:
        raise Exception("Could not read the Database type from the config!")

    return xselpath, dbtype, configp


def get_db_version(config, dbtype, args):
    if os.path.exists(config.get_value("Database", "filename")):
        dbver = factory.check_db_version(dbtype, config.get_value("Database",
                                                                  "filename"))
    else:
        dbver = __DB_FORMAT__
    return dbver
