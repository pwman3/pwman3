import os
import os.path
import shutil
import sys

if sys.version_info.major > 2:  # pragma: no cover
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

from pwman.data import factory
from pwman.util import config
from pwman.util.callback import Callback


def get_ui_platform(platform):  # pragma: no cover
    if 'darwin' in platform:
        from pwman.ui.mac import PwmanCliMac as PwmanCli
        OSX = True
    elif 'win' in platform:
        from pwman.ui.win import PwmanCliWin as PwmanCli
        OSX = False
    else:
        from pwman.ui.cli import PwmanCli
        OSX = False

    return PwmanCli, OSX

PwmanCliNew, OSX = get_ui_platform(sys.platform)


class DummyCallback(Callback):

    def getinput(self, question):
        return b'12345'

    def getsecret(self, question):
        return b'12345'


class DummyCallback2(Callback):

    def getinput(self, question):
        return b'newsecret'

    def getsecret(self, question):
        return b'wrong'


class DummyCallback3(Callback):

    def getinput(self, question):
        return b'newsecret'

    def getsecret(self, question):
        ans = b'12345'
        return ans


class DummyCallback4(Callback):

    def getinput(self, question):
        return b'newsecret'

    def getsecret(self, question):
        return b'newsecret'

db =  ".".join(("pwman","test", sys.version.split(" " ,1)[0], "db"))
testdb = os.path.abspath(os.path.join(os.path.dirname(__file__), db))

config.default_config['Database'] = {'type': 'sqlite',
                                     'filename': testdb,
                                     'dburi': os.path.join(
                                         'sqlite:///', testdb)
                                     }

dc = """
[Global]
xsel = /usr/bin/xsel
colors = yes
umask = 0100
cls_timeout = 5

[Database]
type = SQLite
"""


class SetupTester(object):

    def __init__(self, dbver=None, filename=None, dburi=None):

        f = open(os.path.join(os.path.dirname(__file__), 'test.conf'), 'w')
        f.write(dc)
        f.close()
        self.configp = config.Config(os.path.join(os.path.dirname(__file__),
                                                  "test.conf"),
                                     config.default_config)

        self.configp.set_value('Database', 'dburi',
                               'sqlite://' + testdb
                               )

        if not OSX:
            self.xselpath = shutil.which("xsel") or ""
            self.configp.set_value("Global", "xsel", self.xselpath)
        else:
            self.xselpath = "xsel"

        self.dbver = dbver
        self.dburi = self.configp.get_value('Database', 'dburi')

    def clean(self):
        dbfile = self.configp.get_value('Database', 'filename')
        dburi = urlparse(self.configp.get_value('Database', 'dburi')).path
        try:
            if os.path.exists(dbfile):
                os.remove(dbfile)

            if os.path.exists(dburi):
                os.remove(dburi)
        except PermissionError:
            pass

        if os.path.exists(os.path.join(os.path.dirname(__file__),
                                       'testing_config')):
            os.remove(os.path.join(os.path.dirname(__file__),
                                   'testing_config'))

        if os.path.exists(os.path.join(os.path.dirname(__file__),
                                       'test.conf')):
            os.remove(os.path.join(os.path.dirname(__file__),
                                   'test.conf'))

    def create(self):
        db = factory.createdb(self.dburi, self.dbver)
        self.cli = PwmanCliNew(db, self.xselpath, DummyCallback,
                               config_parser=self.configp)
