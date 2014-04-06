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
# Copyright (C) 2013 Oz Nahum <nahumoz@gmail.com>
#============================================================================
"""
Define the CLI interface for pwman3 and the helper functions
"""
from __future__ import print_function
from pwman.util.callback import Callback
import pwman.util.config as config
import subprocess as sp
import getpass
import sys
import struct
import os
import colorama
from pwman.data.tags import TagNew as Tag
import pwman.util.generator as generator

if sys.platform != 'win32':
    import termios
    import fcntl
    import tty
    import readline
    _readline_available = True
else:  # pragma: no cover
    try:
        import pyreadline as readline
        _readline_available = True
    except ImportError, e:
        _readline_available = False

_defaultwidth = 10


class ANSI(object):
    """
    ANSI Colors
    """
    Reset = 0
    Bold = 1
    Underscore = 2

    Black = 30
    Red = 31
    Green = 32
    Yellow = 33
    Blue = 34
    Magenta = 35
    Cyan = 36
    White = 37


def typeset(text, color, bold=False, underline=False):  # pragma: no cover
    """
    print colored strings using colorama
    """
    if not config.get_value("Global", "colors") == 'yes':
        return text
    if bold:
        text = colorama.Style.BRIGHT + text
    if underline and not 'win32' in sys.platform:
        text = ANSI.Underscore + text
    return color + text + colorama.Style.RESET_ALL


def select(question, possible):  # pragma: no cover
    """
    select input from user
    """
    for i in range(0, len(possible)):
        print ("%d - %-" + str(_defaultwidth) + "s") % (i + 1, possible[i])
    while 1:
        uinput = getonechar(question)
        if uinput.isdigit() and int(uinput) in range(1, len(possible) + 1):
            return possible[int(uinput) - 1]


def text_to_clipboards(text):  # pragma: no cover
    """
    copy text to clipboard
    credit:
    https://pythonadventures.wordpress.com/tag/xclip/
    """
    # "primary":
    try:
        xsel_proc = sp.Popen(['xsel', '-pi'], stdin=sp.PIPE)
        xsel_proc.communicate(text)
        # "clipboard":
        xsel_proc = sp.Popen(['xsel', '-bi'], stdin=sp.PIPE)
        xsel_proc.communicate(text)
    except OSError, e:
        print (e, "\nExecuting xsel failed, is it installed ?\n \
               please check your configuration file ... ")


def text_to_mcclipboard(text):  # pragma: no cover
    """
    copy text to mac os x clip board
    credit:
    https://pythonadventures.wordpress.com/tag/xclip/
    """
    # "primary":
    try:
        pbcopy_proc = sp.Popen(['pbcopy'], stdin=sp.PIPE)
        pbcopy_proc.communicate(text)
    except OSError, e:
        print (e, "\nExecuting pbcoy failed...")


def open_url(link, macosx=False):  # pragma: no cover
    """
    launch xdg-open or open in MacOSX with url
    """
    uopen = "xdg-open"
    if macosx:
        uopen = "open"
    try:
        sp.Popen([uopen, link], stdin=sp.PIPE)
    except OSError, e:
        print ("Executing open_url failed with:\n", e)


def getpassword(question, argsgiven=None,
                width=_defaultwidth, echo=False,
                reader=getpass.getpass, numerics=False, leetify=False,
                symbols=False, special_signs=False,
                length=None):  # pragma: no cover
    # TODO: getpassword should recieve a config insatnce
    #       and generate the policy according to it,
    #       so that getpassword in cli would be simplified
    if argsgiven == 1 or length:
        while not length:
            try:
                length = getinput("Password length (default 7): ", default='7')
                length = int(length)
            except ValueError:
                print("please enter a proper integer")

        password, dumpme = generator.generate_password(length, length,
                                                       True, leetify,
                                                       numerics,
                                                       special_signs)
        print ("New password: %s" % (password))
        return password
    # no args given
    while True:
        a1 = reader(question.ljust(width))
        if not a1:
            return getpassword('', argsgiven=1)
        a2 = reader("[Repeat] %s" % (question.ljust(width)))
        if a1 == a2:
            if leetify:
                return generator.leetify(a1)
            else:
                return a1
        else:
            print ("Passwords don't match. Try again.")


def gettermsize():  # pragma: no cover
    s = struct.pack("HHHH", 0, 0, 0, 0)
    f = sys.stdout.fileno()
    x = fcntl.ioctl(f, termios.TIOCGWINSZ, s)
    rows, cols, width, height = struct.unpack("HHHH", x)
    return rows, cols


def getinput(question, default="", reader=raw_input,
             completer=None, width=_defaultwidth):  # pragma: no cover
    """
    http://stackoverflow.com/questions/2617057/\
            supply-inputs-to-python-unittests
    """
    if reader == raw_input:
        if not _readline_available:
            val = raw_input(question.ljust(width))
            if val:
                return val
            else:
                return default
        else:
            def defaulter():
                """define default behavior startup"""
                if _readline_available:
                    readline.insert_text(default)
                readline.set_startup_hook(defaulter)
                readline.get_completer()
                readline.set_completer(completer)

            x = raw_input(question.ljust(width))
            readline.set_completer(completer)
            readline.set_startup_hook()
            if not x:
                return default
            return x
    else:
        return reader()


class CMDLoop(object):  # pragma: no cover
    """
    The menu that drives editing of a node
    """
    def __init__(self):
        self.items = []

    def add(self, item):
        if (isinstance(item, CliMenuItem)):
            self.items.append(item)
        else:
            print (item.__class__)

    def run(self, new_node=None):
        while True:
            i = 0
            for x in self.items:
                i = i + 1
                try:
                    current = x.getter
                except AttributeError:
                    current = x

                # when printing tags, we have list ...
                currentstr = ''
                if type(current) == list:
                    for c in current:
                        try:
                            currentstr += ' ' + c
                        except TypeError:
                            currentstr += ' ' + c.name
                # for the case we are not dealing with
                # a list of tags
                else:
                    currentstr = current

                print ("%s - %s: %s" % (i, x.name, currentstr))
            print("X - Finish editing")
            option = getonechar("Enter your choice:")
            try:
                print ("Selection, ", option)
                # substract 1 because array subscripts start at 0
                selection = int(option) - 1
                # new value is created by calling the editor with the
                # previous value as a parameter
                # TODO: enable overriding password policy as if new node
                # is created.
                if selection == 0:
                    new_node.username = getinput("Username:")
                    self.items[0].getter = new_node.username
                    self.items[0].setter = new_node.username
                elif selection == 1:  # for password
                    new_node.password = getpassword('New Password:')
                    self.items[1].getter = new_node.password
                    self.items[1].setter = new_node.password
                elif selection == 2:
                    new_node.url = getinput("Url:")
                    self.items[2].getter = new_node.url
                    self.items[2].setter = new_node.url
                elif selection == 3:  # for notes
                    # new_node.notes = getinput("Notes:")
                    new_node.notes = getinput("Notes:")
                    self.items[3].getter = new_node.notes
                    self.items[3].setter = new_node.notes
                elif selection == 4:
                    taglist = getinput("Tags:")
                    tagstrings = taglist.split()
                    tags = [Tag(tn) for tn in tagstrings]
                    new_node.tags = tags
                    self.items[4].setter = new_node.tags
                    self.items[4].getter = new_node.tags
            except (ValueError, IndexError):
                if (option.upper() == 'X'):
                    break
                print("Invalid selection")


def getonechar(question, width=_defaultwidth):  # pragma: no cover
    question = "%s " % (question)
    print (question.ljust(width),)
    try:
        sys.stdout.flush()
        fd = sys.stdin.fileno()
        # tty module exists only if we are on Posix
        try:
            tty_mode = tty.tcgetattr(fd)
            tty.setcbreak(fd)
        except NameError:
            pass
        try:
            ch = os.read(fd, 1)
        finally:
            try:
                tty.tcsetattr(fd, tty.TCSAFLUSH, tty_mode)
            except NameError:
                pass
    except AttributeError:
        ch = sys.stdin.readline()[0]

    print(ch)
    return ch


class CliMenuItem(object):  # pragma: no cover
    def __init__(self, name, editor, getter, setter):
        self.name = name
        self.editor = editor
        self.getter = getter
        self.setter = setter


class CLICallback(Callback):  # pragma: no cover

    def getinput(self, question):
        return raw_input(question)

    def getsecret(self, question):
        return getpass.getpass(question + ":")

    def getnewsecret(self, question):
        return getpass.getpass(question + ":")
