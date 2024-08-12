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
import os
import re
import string
import shutil
import ssl
import sys
import urllib.request

from importlib.metadata import PackageNotFoundError, version, distribution

from pwman.util import config
from pwman.data.factory import check_db_version

try:
    import cryptography  # noqa
    has_cryptography = True
except ImportError:
    has_cryptography = False


appname = "pwman3"
website = 'http://pwman3.github.io/pwman3/'

try:
    version = version('pwman3')
except PackageNotFoundError:
    version = '0.12.2'


class PkgMetadata(object):

    def __init__(self):
        d = distribution("pwman3")
        self.summary = d.metadata.get("summary")
        self.author_email = d.metadata.get("author-email")
        self.home_page = d.metadata.get("project-url")
        self.home_page = d.metadata.get("project-url").split(", ")[-1]




def parser_options(formatter_class=argparse.HelpFormatter):  # pragma: no cover
    pkg_meta = PkgMetadata()
    description = pkg_meta.summary

    parser = argparse.ArgumentParser(prog='pwman3',
                                     description=description,
                                     formatter_class=formatter_class)
    parser.add_argument('-c', '--config', dest='cfile',
                        default=os.path.join(
                                             config.find_config_dir(
                                                 'pwman')[0], 'config'),
                        help='cofiguration file to read')
    parser.add_argument('-d', '--database', dest='dbase')
    parser.add_argument('-i', '--import', nargs=2, dest='file_delim',
                        help="Specify the file name and the delimeter type")
    subparsers = parser.add_subparsers(help='commands', dest="cmd")

    printer = subparsers.add_parser('p', help='print password entry')
    printer.add_argument("node", type=int)

    copy = subparsers.add_parser('cp', help='copy password entry to clipboard')
    copy.add_argument("node", type=str)

    version = subparsers.add_parser('version', help='version')
    version.add_argument("--latest", action='store_true')
    return parser


def get_conf(args):
    for dir in config.find_config_dir('pwman'):
        if not os.path.isdir(dir):  # pragma: no cover
            os.makedirs(dir, exist_ok=True)

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
        hostname = os.getenv("PWMAN_HOSTNAME", "pwman.tiram.it")
        url = (f"https://{hostname}/is_latest/?"
               f"current_version={version}&os={sys.platform}&hash={client_info}")
        ctx = None
        if os.getenv("TEST") == '1':
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        res = urllib.request.urlopen(url, timeout=0.5, context=ctx)
        data = res.read()  # This will return entire content.

        if res.status != 200:
            return None, True
        if parse_version(data.decode()) > parse_version(version):
            return None, False
        else:
            return None, True
    except Exception as E:
        return E, True
