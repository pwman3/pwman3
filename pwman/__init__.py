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
import string
import colorama
import pkg_resources
from pwman.util import config
from pwman.data.factory import check_db_version

appname = "pwman3"

try:
    version = pkg_resources.get_distribution('pwman3').version
except pkg_resources.DistributionNotFound:  # pragma: no cover
    version = "0.8.0"


class PkgMetadata(object):

    def __init__(self):
        p = pkg_resources.get_distribution('pwman3')
        f = open(os.path.join(p.location+'-info','PKG-INFO'))
        lines = f.readlines()
        self.summary = lines[3].split(':')[-1].strip()
        self.description = ''.join(map(string.strip, lines[9:14]))
        self.author_email = lines[6].split(':')[-1].strip()
        self.author = lines[5].split(':')[-1].strip()
        self.home_page = lines[4].split(':')[-1].strip()

try:
    pkg_meta = PkgMetadata()
    website = pkg_meta.home_page
    author = pkg_meta.author
    authoremail = pkg_meta.author_email
    description = pkg_meta.summary
    long_description = pkg_meta.description
except IOError as E:
    # this should only happen once when installing the package
    description = "a command line password manager with support for multiple databases."
    website = 'http://pwman3.github.io/pwman3/'


def which(cmd):  # pragma: no cover
    _, cmdname = os.path.split(cmd)

    for path in os.environ["PATH"].split(os.pathsep):
        cmd = os.path.join(path, cmdname)
        if os.path.isfile(cmd) and os.access(cmd, os.X_OK):  # pragma: no cover
            return cmd
    return ''


config_dir = os.path.expanduser("~/.pwman")


def parser_options(formatter_class=argparse.HelpFormatter):  # pragma: no cover
    parser = argparse.ArgumentParser(
            prog='pwman3',
            description=description,
            formatter_class=formatter_class)
    parser.add_argument('-c', '--config', dest='cfile',
                        default=os.path.expanduser("~/.pwman/config"),
                        help='cofiguration file to read')
    parser.add_argument('-d', '--database', dest='dbase')
    parser.add_argument('-i', '--import', nargs=2, dest='file_delim',
            help="Specify the file name and the delimeter type")
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


#def set_win_colors(config):  # pragma: no cover
#    try:
#        if sys.platform.startswith('win'):
#            colorama.init()
#   except ImportError:  # when installing colorama is still not there
#        pass

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

    #set_win_colors(configp)
    set_db(args, configp)
    set_umask(configp)
    dburi = configp.get_value("Database", "dburi")
    return xselpath, dburi, configp


def get_db_version(config, args):
    dburi = check_db_version(config.get_value("Database", "dburi"))
    return dburi
