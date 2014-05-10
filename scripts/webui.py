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
# Copyright (C) 2012-2014 Oz Nahum <nahumoz@gmail.com>
#============================================================================
from __future__ import print_function
from bottle import route, run, debug, template, request, get
import os
import sys
import re
import shutil
from pwman import default_config, which
from pwman import parser_options
from pwman.ui import get_ui_platform
from pwman.ui.tools import CLICallback
from pwman.util.crypto import CryptoEngine
import pwman.util.config as config
import pwman.data.factory


tmplt = """
%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<p>The open items are as follows:</p>
<table border="1">
%for row in rows:
  <tr>
  %for col in row:
    <td>{{col}}</td>
  %end
  </tr>
%end
</table>
"""

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

@route('/', method=['GET', 'POST'])
def listnodes():
    OSX = False
    args = parser_options().parse_args()
    xselpath, dbtype = get_conf_options(args, OSX)
    dbver = 0.4
    db = pwman.data.factory.create(dbtype, dbver)
    db.open()
    crypto  = CryptoEngine.get()
    crypto.auth('YOURPASSWORD')


    nodeids = db.listnodes()
    nodes = db.getnodes(nodeids)

    nodesd = [''] * len(nodes)
    for idx, node in enumerate(nodes):
        tags = node.tags
        tags = filter(None, tags)
        nodesd[idx]=('@'.join((node.username, node.url)), ','.join(tags))

    output = template('make_table', rows=nodesd)
    return output

debug(True)
run(reloader=True)
