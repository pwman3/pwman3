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
import argparse
from util import config
import sys
import re
import data.factory

appname = "pwman3"
try:
    version = pkg_resources.get_distribution('pwman3').version
except pkg_resources.DistributionNotFound:  # pragma: no cover
    version = "0.5"

website = "http://github.com/pwman3/pwman3"
author = "Oz Nahum"
authoremail = "nahumoz@gmail.com"
description = "a command line password management application."
keywords = "password management sqlite crypto"
long_description = ("Pwman3 aims to provide a simple but powerful command line "
                    "interface for password management.\nIt allows one to store your "
                    "password in a SQLite database locked by a\nmaster password which "
                    "can be encrypted with different algorithms (e.g AES, Blowfish, "
                    "DES3, IDEA, etc.).")

_db_warn = ("pwman3 detected that you are using the old database format"
            " which is insecure."
            " pwman3 will try to automatically convert the database now."
            "\n"
            "If you choose not to convert the database, pwman3, will quit."
            "\nYou can check the help (pwman3 -h) or look at the manpage how to convert "
            " the database manually."
            )


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


def parser_options(formatter_class=argparse.HelpFormatter):
    parser = argparse.ArgumentParser(prog=appname,
                                     description=description,
                                     formatter_class=formatter_class)
    parser.add_argument('-c', '--config', dest='cfile',
                        default=os.path.expanduser("~/.pwman/config"),
                        help='cofiguration file to read')
    parser.add_argument('-d', '--database', dest='dbase')
    parser.add_argument('-e', '--encryption', dest="algo",
                        help=("Possible options are: AES(default), ARC2, ARC4,"
                              " Blowfish, CAST, DES, DES3, IDEA, RC5"))
    parser.add_argument('-k', '--convert', dest='dbconvert',
                        action='store_true', default=False,
                        # os.path.expanduser('~/.pwman/pwman.db'),
                        help=("Convert old DB format to version >= 0.4."
                              " The database that will be converted is the"
                              " one found in the config file, or the one given"
                              " as command line argument."))
    parser.add_argument('-O', '--output', dest='output',
                        #default=os.path.expanduser('~/.pwman/pwman-newdb.db'),
                        help=("The name of the newly created database after "
                              "converting."))
    return parser


def get_conf(args):
    config_dir = os.path.expanduser("~/.pwman")

    if not os.path.isdir(config_dir):
        os.mkdir(config_dir)

    if not os.path.exists(args.cfile):
        config.set_defaults(default_config)
    else:
        config.load(args.cfile)

    return config


def set_xsel(config, OSX):
    if not OSX:
        xselpath = which("xsel")
        config.set_value("Global", "xsel", xselpath)
    elif OSX:
        pbcopypath = which("pbcopy")
        config.set_value("Global", "xsel", pbcopypath)


def set_win_colors(config):
    if 'win' in sys.platform:
        try:
            import colorama
            colorama.init()
        except ImportError:
            config.set_value("Global", "colors", 'no')


def set_umask(config):
    # set umask before creating/opening any files
    try:
        umask = config.get_value("Global", "umask")
        if re.search(r'^\d{4}$', umask):
            os.umask(int(umask))
        else:
            raise ValueError
    except ValueError:
        print("Could not determine umask from config!")
        sys.exit(2)


def set_db(args):
    if args.dbase:
        config.set_value("Database", "filename", args.dbase)
        config.set_value("Global", "save", "False")


def set_algorithm(args, config):
    if args.algo:
        config.set_value("Encryption", "algorithm", args.algo)
        config.set_value("Global", "save", "False")


def get_conf_options(args, OSX):

    config = get_conf(args)
    xselpath = config.get_value("Global", "xsel")
    if not xselpath:
        set_xsel(config, OSX)

    set_win_colors(config)
    set_db(args)
    set_umask(config)
    set_algorithm(args, config)
    dbtype = config.get_value("Database", "type")
    if not dbtype:
        print("Could not read the Database type from the config!")
        sys.exit(1)

    return xselpath, dbtype


def get_db_version(config, dbtype, args):
    if os.path.exists(config.get_value("Database", "filename")):
        dbver = data.factory.check_db_version(dbtype)
        if dbver < 0.4 and not args.dbconvert:
            print(_db_warn)
    else:
        dbver = 0.4
    return dbver
