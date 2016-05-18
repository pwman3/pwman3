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
# Copyright (C) 2013 Oz Nahum <nahumoz@gmail.com>
# ============================================================================
"""
Define the CLI interface for pwman3 and the helper functions
"""
from __future__ import print_function
import subprocess as sp
import getpass
import sys
import struct
import shlex
import platform
import colorama
import os
import ast
from pwman.util.callback import Callback
from pwman.util.crypto_engine import generate_password


if sys.version_info.major > 2:  # pragma: no cover
    raw_input = input

if not sys.platform.startswith('win'):
    import termios
    import fcntl
    import readline
    _readline_available = True
else:  # pragma: no cover
    try:
        import readline
        _readline_available = True
    except ImportError as e:
        try:
            import pyreadline as readrline
            _readline_available = True
        except ImportError as e:
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


def typeset(text, color, bold=False, underline=False,
            has_colorama=True):  # pragma: no cover
    """
    print colored strings using colorama
    """
    if not has_colorama:
        return text
    if bold:
        text = colorama.Style.BRIGHT + text
    if underline and 'win32' not in sys.platform:
        text = ANSI.Underscore + text
    return color + text + colorama.Style.RESET_ALL


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
    except OSError as e:
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
    except OSError as e:
        print (e, "\nExecuting pbcoy failed...")


def open_url(link, macosx=False, ):  # pragma: no cover
    """
    launch xdg-open or open in MacOSX with url
    """
    uopen = "xdg-open "
    if macosx:
        uopen = "open "
    try:
        sp.call(uopen + link, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    except OSError as e:
        print("Executing open_url failed with:\n", e)


def get_terminal_size():  # pragma: no cover
    """ getTerminalSize()
     - get width and height of console
     - works on linux,os x,windows,cygwin(windows)
     originally retrieved from:
     http://stackoverflow.com/questions/566746/how-to-get-\
         console-window-width-in-python
    """
    current_os = platform.system()
    tuple_xy = None
    if current_os == 'Windows':
        tuple_xy = _get_terminal_size_windows()
        if tuple_xy is None:
            tuple_xy = _get_terminal_size_tput()
            # needed for window's python in cygwin's xterm!
    if current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
        tuple_xy = _get_terminal_size_linux()
    if tuple_xy is None:
        tuple_xy = (80, 25)      # default value
    return tuple_xy


def _get_terminal_size_windows():  # pragma: no cover
    try:
        from ctypes import windll, create_string_buffer
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom,
             maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
            return sizex, sizey
    except:
        pass


def _get_terminal_size_tput():  # pragma: no cover
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-\
    #    find-the-width-height-of-a-terminal-window
    try:
        cols = int(sp.check_call(shlex.split('tput cols')))
        rows = int(sp.check_call(shlex.split('tput lines')))
        return (cols, rows)
    except:
        pass


def _get_terminal_size_linux():  # pragma: no cover
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            cr = struct.unpack('hh',
                               fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
            return cr
        except:
            pass
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            return None
    return int(cr[1]), int(cr[0])


def gettermsize():  # pragma: no cover
    if sys.stdout.isatty():
        s = struct.pack("HHHH", 0, 0, 0, 0)
        f = sys.stdout.fileno()
        x = fcntl.ioctl(f, termios.TIOCGWINSZ, s)
        rows, cols, width, height = struct.unpack("HHHH", x)
        return rows, cols
    else:
        return 40, 80


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
                readline.insert_text(default)

            if _readline_available:
                readline.set_startup_hook(defaulter)
                readline.get_completer()
                readline.set_completer(completer)

            x = raw_input(question.ljust(width))

            if _readline_available:
                readline.set_startup_hook()
            return x if x else default

    else:
        return reader()


def get_or_create_pass():  # pragma: no cover

    p = getpass.getpass(prompt='Password (leave empty to create one):')

    if p:
        return p

    while not p:
        print("Password length (default: 8):", end="")
        sys.stdout.flush()
        ans = sys.stdin.readline().strip()
        try:
            ans = ast.literal_eval(ans)
            if isinstance(ans, int):
                kwargs = {'pass_len': ans}
                break
            elif isinstance(ans, dict):
                kwargs = ans
                break
            else:
                print("Did not understand your input...")
                continue
        except ValueError:
            print("Something evil happend.")
            print("Did not understand your input...")
            continue
        except SyntaxError:
            kwargs = {}
            break

    p = generate_password(**kwargs)
    return p


def _get_secret():
    if sys.stdin.isatty():  # pragma: no cover
        p = get_or_create_pass()
    else:
        p = sys.stdin.readline().rstrip()

    return p


def set_selection(new_node, items, selection, reader):  # pragma: no cover
    if selection == 0:
        new_node.username = getinput("Username:", new_node.username)
        items[0].getter = new_node.username
    elif selection == 1:  # for password
        new_node.password = _get_secret()
        items[1].getter = new_node.password
    elif selection == 2:
        new_node.url = getinput("Url:", new_node.url)
        items[2].getter = new_node.url
    elif selection == 3:  # for notes
        new_node.notes = getinput("Notes :", new_node.notes)
        items[3].getter = new_node.notes
    elif selection == 4:
        taglist = getinput("Tags:", " ".join(new_node.tags))
        tags = taglist.split()
        new_node.tags = tags
        items[4].getter = ','.join(new_node.tags)


class CMDLoop(object):

    """
    The menu that drives editing of a node
    """

    def __init__(self, config):
        self.items = []
        self.config = config

    def add(self, item):
        if isinstance(item, CliMenuItem):
            self.items.append(item)

    def run(self, new_node=None, reader=raw_input):
        while True:
            for i, x in enumerate(self.items):
                print ("%s - %s: %s" % (i + 1, x.name, x.getter))

            print("X - Finish editing")
            # read just the first character entered
            option = reader("Enter your choice:")[0]
            try:
                print ("Selection, ", option)
                # substract 1 because array subscripts start at 0
                selection = int(option) - 1
                set_selection(new_node, self.items, selection, reader)
            except (ValueError, IndexError):  # pragma: no cover
                if (option.upper() == 'X'):
                    break
                print("Invalid selection")


class CliMenuItem(object):

    def __init__(self, name, getter):
        self.name = name
        self.getter = getter


class CLICallback(Callback):  # pragma: no cover

    def getinput(self, question):
        return raw_input(question)

    def getsecret(self, question):
        return getpass.getpass(question + ":")

    def getnewsecret(self, question):
        return getpass.getpass(question + ":")
