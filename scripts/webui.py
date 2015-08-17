#!/usr/bin/env python
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
# Copyright (C) 2012-2014 Oz Nahum <nahumoz@gmail.com>
# ============================================================================
from __future__ import print_function
from bottle import route, run, debug, template, request, redirect, static_file
from pwman.util.crypto_engine import CryptoEngine
import pwman.data.factory
from pwman.data.nodes import Node
from pwman import parser_options, get_conf_options
from pkg_resources import resource_filename
import sys
from signal import SIGTERM
import os
import json

templates_path = [resource_filename('pwman', 'ui/templates')]
statics = [resource_filename('pwman', 'ui/templates/static')][0]


AUTHENTICATED = False
TAGS = None
DB = None

# BUG: Error: SQLite: Incorrect number of bindings supplied.
# The current statement uses 2, and there are 1 supplied.
# When issuing multiple times filter

# WEB GUI shows multiple tags as one tag!


@route('/exit', method=['GET'])
def exit():
    os.kill(os.getpid(), SIGTERM)


def require_auth(fn):
    def check_auth(**kwargs):
        if AUTHENTICATED:
            return fn(**kwargs)
        else:
            redirect("/auth")
    return check_auth


@route('/node/:no')
@require_auth
def view_node(no):
    global DB
    node = DB.getnodes([no])
    node = DB.getnodes([no])[0]
    node = Node.from_encrypted_entries(node[1],
                                       node[2],
                                       node[3],
                                       node[4],
                                       node[5:])
    return template("ajax.tpl", request=request, node=node,
                    template_lookup=templates_path)


@route('/_add_numbers')
def add_numbers():
    """Add two numbers server side, ridiculous but well..."""
    a = request.params.get('a', 0, type=int)
    b = request.params.get('b', 0, type=int)
    return json.dumps({'result': a+b})




@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root=statics)


def submit_node(id, request):
    # create new\update node based on request.params.items()
    redirect('/')


@route('/new/', method=['GET', 'POST'])
@route('/edit/:no', method=['GET', 'POST'])
@require_auth
def edit_node(no=None):
    global DB

    if 'POST' in request.method:
        submit_node(no, request)

    if no:
        node = DB.getnodes([no])[0]
        node = Node.from_encrypted_entries(node[1],
                                           node[2],
                                           node[3],
                                           node[4],
                                           node[5:])

    output = template('edit.tpl', node=node,  
                      template_lookup=templates_path)
    return output


@route('/forget', method=['GET', 'POST'])
def forget():
    global AUTHENTICATED
    AUTHENTICATED = False
    enc = CryptoEngine.get()
    enc.forget()

    redirect('/auth')


@route('/auth', method=['GET', 'POST'])
def is_authenticated():
    global AUTHENTICATED
    crypto = CryptoEngine.get()

    if request.method == 'POST':
        key = request.POST.get('pwd', '')
        while True:
            try:
                crypto.authenticate(key)
                break
            except Exception:
                redirect('/auth')

        AUTHENTICATED = True
        redirect('/')
    else:
        return template("login.tpl", template_lookup=templates_path, request=request)


@route('/auth', method=['GET', 'POST'])
def is_authenticated():
    crypto = CryptoEngine.get()
    crypto.authenticate('foobar')
    global AUTHENTICATED
    AUTHENTICATED = True
    redirect('/')


@route('/', method=['GET', 'POST'])
@require_auth
def listnodes(apply=['require_login']):

    global AUTHENTICATED, TAGS, DB

    _filter = None

    if 'POST' in request.method:
        _filter = request.POST.get('tag')
        if _filter:
            DB._filtertags = []
        if _filter == 'None':
            DB._filtertags = []

    nodeids = DB.listnodes()
    raw_nodes = DB.getnodes(nodeids)
    _nodes_inst = []
    for node in raw_nodes:
        _nodes_inst.append(Node.from_encrypted_entries(
            node[1],
            node[2],
            node[3],
            node[4],
            node[5:]))
        _nodes_inst[-1]._id = node[0]
    nodesd = _nodes_inst
    ce = CryptoEngine.get()
    tags = [ce.decrypt(t).decode() for t in DB.listtags()]
    html_nodes = template("main.tpl", nodes=nodesd, tags=tags, request=request,
                          template_lookup=[resource_filename('pwman',
                                                             'ui/templates')])
    return html_nodes


@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=statics)


class Pwman3WebDaemon(object):

    def __enter__(self):
        return self

    def run(self):
        global AUTHENTICATED, TAGS, DB
        OSX = False
        sys.argv = []
        args = parser_options().parse_args()
        xselpath, dburi, configp = get_conf_options(args, OSX)
        DB = pwman.data.factory.createdb(dburi, None)
        DB.open()
        print(dir(DB))
        CryptoEngine.get()
        debug(True)
        run(port=9030)

    def __exit__(self, type, value, traceback):
        return isinstance(value, TypeError)

if __name__ == '__main__':

    with Pwman3WebDaemon() as webui:
        webui.run()
