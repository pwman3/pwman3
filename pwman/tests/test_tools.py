from pwman.data import factory
from pwman.util import config
from pwman import which, default_config
from pwman.ui import get_ui_platform
import os
import os.path
import sys
from pwman.util.callback import Callback

PwmanCliNew, OSX = get_ui_platform(sys.platform)


class DummyCallback(Callback):

    def getinput(self, question):
        return u'12345'

    def getsecret(self, question):
        return u'12345'


class DummyCallback2(Callback):

    def getinput(self, question):
        return u'newsecret'

    def getsecret(self, question):
        return u'wrong'


class DummyCallback3(Callback):

    def getinput(self, question):
        return u'newsecret'

    def getsecret(self, question):
        ans = '12345'
        return ans


class DummyCallback4(Callback):

    def getinput(self, question):
        return u'newsecret'

    def getsecret(self, question):
        return u'newsecret'


default_config['Database'] = {'type': 'SQLite',
                              'filename':
                              os.path.join(os.path.dirname(__file__),
                                           "test.pwman.db")
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

    def __init__(self, dbver=None, filename=None):

        f = open(os.path.join(os.path.dirname(__file__), 'test.conf'), 'w')
        f.write(dc)
        f.close()
        self.configp = config.Config(os.path.join(os.path.dirname(__file__),
                                                  "test.conf"),
                                     default_config)
        self.configp.set_value('Database', 'filename',
                               os.path.join(os.path.dirname(__file__),
                                            "test.pwman.db"))
        if not OSX:
            self.xselpath = which("xsel")
            self.configp.set_value("Global", "xsel", self.xselpath)
        else:
            self.xselpath = "xsel"

        self.dbver = dbver
        self.filename = filename

    def clean(self):
        if os.path.exists(self.configp.get_value('Database', 'filename')):
            os.remove(self.configp.get_value('Database', 'filename'))

        if os.path.exists(os.path.join(os.path.dirname(__file__),
                                       'testing_config')):
            os.remove(os.path.join(os.path.dirname(__file__),
                                   'testing_config'))

        if os.path.exists(os.path.join(os.path.dirname(__file__),
                                       'test.conf')):
            os.remove(os.path.join(os.path.dirname(__file__),
                                   'test.conf'))

    def create(self):
        dbtype = 'SQLite'
        db = factory.create(dbtype, self.dbver, self.filename)
        self.cli = PwmanCliNew(db, self.xselpath, DummyCallback,
                               config_parser=self.configp)
