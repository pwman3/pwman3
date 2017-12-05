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
import argparse
import urllib.request
import os
import pkg_resources
import re
import string
import shutil
import sys
from pwman.util import config
from pwman.data.factory import check_db_version

try:
    import cryptography  # noqa
    has_cryptography = True
except ImportError:
    has_cryptography = False


appname = "pwman3"

try:
    version = pkg_resources.get_distribution('pwman3').version
except pkg_resources.DistributionNotFound:  # pragma: no cover
    version = "0.9.5"


class PkgMetadata(object):

    def __init__(self):
        p = pkg_resources.get_distribution('pwman3')
        f = open(os.path.join(p.location+'-info', 'PKG-INFO'))
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
    description = "a command line password manager with support for multiple databases."  # noqa
    website = 'http://pwman3.github.io/pwman3/'


config_dir = os.path.expanduser("~/.pwman")


def parser_options(formatter_class=argparse.HelpFormatter):  # pragma: no cover
    parser = argparse.ArgumentParser(prog='pwman3',
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
        xselpath = shutil.which("xsel") or ""
        configp.set_value("Global", "xsel", xselpath)
    elif OSX:
        pbcopypath = shutil.which("pbcopy") or ""
        configp.set_value("Global", "xsel", pbcopypath)


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

    set_db(args, configp)
    set_umask(configp)
    dburi = configp.get_value("Database", "dburi")
    return xselpath, dburi, configp


def get_db_version(config, args):
    dburi = check_db_version(config.get_value("Database", "dburi"))
    return dburi


def calculate_client_info():  # pragma: no cover
    import hashlib
    import socket
    from getpass import getuser
    hashinfo = hashlib.sha256((socket.gethostname() + getuser()).encode())
    hashinfo = hashinfo.hexdigest()
    return hashinfo


def is_latest_version(version, client_info):  # pragma: no cover
    """check current version againt latest version"""
    try:
        url = ("https://pwman.tiram.it/is_latest/?"
               "current_version={}&os={}&hash={}".format(
                version, sys.platform, client_info))
        res = urllib.request.urlopen(url, timeout=0.5)
        data = res.read()  # This will return entire content.

        if res.status != 200:
            return None, True
        if data.decode().split(".") > version.split("."):
            return None, False
        else:
            return None, True
    except Exception as E:
        return E, True
