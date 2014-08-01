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

    def getsecret(self, question):
        return u'12345'

    def getnewsecret(self, question):
        return u'12345'


class DummyCallback2(Callback):

    def getinput(self, question):
        return u'newsecret'

    def getsecret(self, question):
        return u'wrong'

    def getnewsecret(self, question):
        return u'newsecret'


class DummyCallback3(Callback):

    def getinput(self, question):
        return u'newsecret'

    def getsecret(self, question):
        return u'12345'

    def getnewsecret(self, question):
        return u'newsecret'


class DummyCallback4(Callback):

    def getinput(self, question):
        return u'newsecret'

    def getsecret(self, question):
        return u'newsecret'

    def getnewsecret(self, question):
        return u'newsecret'


default_config['Database'] = {'type': 'SQLite',
                              'filename':
                              os.path.join(os.path.dirname(__file__),
                                           "test.pwman.db")
                              }

class SetupTester(object):

    def __init__(self, dbver=None, filename=None):
        config.set_defaults(default_config)
        if not OSX:
            self.xselpath = which("xsel")
            config.set_value("Global", "xsel", self.xselpath)
        else:
            self.xselpath = "xsel"

        self.dbver = dbver
        self.filename = filename

    def clean(self):
        if os.path.exists(config.get_value('Database', 'filename')):
            os.remove(config.get_value('Database', 'filename'))

        if os.path.exists(os.path.join(os.path.dirname(__file__),
                                       'testing_config')):
            os.remove(os.path.join(os.path.dirname(__file__),
                                   'testing_config'))

    def create(self):
        dbtype = config.get_value("Database", "type")
        if self.filename:
            db = factory.create(dbtype, self.dbver, self.filename)
        else:
            db = factory.create(dbtype, self.dbver)

        self.cli = PwmanCliNew(db, self.xselpath, DummyCallback)
