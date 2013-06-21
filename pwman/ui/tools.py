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

from pwman.util.callback import Callback
import pwman.util.config as config
import subprocess as sp
import getpass
import sys
import struct
import os
# import traceback

if sys.platform != 'win32':
    import termios
    import fcntl
    import tty
    try:
        import pyreadline as readline
        _readline_available = True
    except ImportError:
        _readline_available = False
       # raise ImportError("You need 'pyreadline' on Windows")
else:
    try:
        import readline
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


def typeset(text, color, bold=False, underline=False):
    """print colored strings"""
    if not config.get_value("Global", "colors") == 'yes':
        return text
    if (bold):
        bold = "%d ;" % (ANSI.Bold)
    else:
        bold = ""
    if (underline):
        underline = "%d;" % (ANSI.Underscore)
    else:
        underline = ""
    return "\033[%s%s%sm%s\033[%sm" % (bold, underline, color,
                                       text, ANSI.Reset)


def select(question, possible):
    """
    select input from user
    """
    for i in range(0, len(possible)):
        print ("%d - %-"+str(_defaultwidth)+"s") % (i+1, possible[i])
    while 1:
        uinput = getonechar(question)
        if uinput.isdigit() and int(uinput) in range(1, len(possible)+1):
            return possible[int(uinput)-1]


def text_to_clipboards(text):
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
        print e, "\nExecuting xsel failed, is it installed ?\n \
please check your configuration file ... "


def text_to_mcclipboard(text):
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
        print e, "\nExecuting pbcoy failed..."


def open_url(link, macosx=False):
    """
    launch xdg-open or open in MacOSX with url
    """
    uopen = "xdg-open"
    if macosx:
        uopen = "open"
    try:
        sp.Popen([uopen, link], stdin=sp.PIPE)
    except OSError, e:
        print "Executing open_url failed with:\n", e


def getpassword(question, width=_defaultwidth, echo=False):
    if echo:
        print question.ljust(width),
        return sys.stdin.readline().rstrip()
    else:
        while 1:
            a1 = getpass.getpass(question.ljust(width))
            if len(a1) == 0:
                return a1
            a2 = getpass.getpass("[Repeat] %s" % (question.ljust(width)))
            if a1 == a2:
                return a1
            else:
                print "Passwords don't match. Try again."


def gettermsize():
    s = struct.pack("HHHH", 0, 0, 0, 0)
    f = sys.stdout.fileno()
    x = fcntl.ioctl(f, termios.TIOCGWINSZ, s)
    rows, cols, width, height = struct.unpack("HHHH", x)
    return rows, cols


def getinput(question, default="", completer=None, width=_defaultwidth):
    if not _readline_available:
        return raw_input(question.ljust(width))
    else:
        def defaulter():
            """define default behavior startup"""
            if _readline_available:
                readline.insert_text(default)
            readline.set_startup_hook(defaulter)
            oldcompleter = readline.get_completer()
            readline.set_completer(completer)

        x = raw_input(question.ljust(width))
        readline.set_completer(completer)
        readline.set_startup_hook()
        return x

def getyesno(question, defaultyes=False, width=_defaultwidth):
    if (defaultyes):
        default = "[Y/n]"
    else:
        default = "[y/N]"
    ch = getonechar("%s %s" % (question, default), width)
    if (ch == '\n'):
        if (defaultyes):
            return True
        else:
            return False
    elif (ch == 'y' or ch == 'Y'):
        return True
    elif (ch == 'n' or ch == 'N'):
        return False
    else:
        return getyesno(question, defaultyes, width)


class CliMenu(object):
    def __init__(self):
        self.items = []

    def add(self, item):
        if (isinstance(item, CliMenuItem)):
            self.items.append(item)
        else:
            print item.__class__

    def run(self):
        while True:
            i = 0
            for x in self.items:
                i = i + 1
                current = x.getter()
                currentstr = ''
                if type(current) == list:
                    for c in current:
                        currentstr += ("%s " % (c))
                else:
                    currentstr = current

                print ("%d - %-"+str(_defaultwidth)+\
                      "s %s") % (i, x.name+":",
                                 currentstr)
            print "%c - Finish editing" % ('X')
            option = getonechar("Enter your choice:")
            try:
                print "selection, ", option
                # substract 1 because array subscripts start at 0
                selection = int(option) - 1
                # new value is created by calling the editor with the
                # previous value as a parameter
                # TODO: enable overriding password policy as if new node
                # is created.
                if selection == 1:  # for password
                    value = self.items[selection].editor(0)
                else:
                    edit = self.items[selection].getter()
                    value = self.items[selection].editor(edit)
                self.items[selection].setter(value)
            except (ValueError, IndexError):
                if (option.upper() == 'X'):
                    break
                print "Invalid selection"


def getonechar(question, width=_defaultwidth):
    question = "%s " % (question)
    print question.ljust(width),
    sys.stdout.flush()

    fd = sys.stdin.fileno()
    tty_mode = tty.tcgetattr(fd)
    tty.setcbreak(fd)
    try:
        ch = os.read(fd, 1)
    finally:
        tty.tcsetattr(fd, tty.TCSAFLUSH, tty_mode)
    print ch
    return ch


class CliMenuItem(object):
    def __init__(self, name, editor, getter, setter):
        self.name = name
        self.editor = editor
        self.getter = getter
        self.setter = setter


class CLICallback(Callback):
    def getinput(self, question):
        return raw_input(question)

    def getsecret(self, question):
        return getpass.getpass(question + ":")
