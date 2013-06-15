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

import pwman.util.config as config
import subprocess as sp


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
