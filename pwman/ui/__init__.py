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
# Copyright (C) 2012 Oz Nahum <nahumoz@gmail.com>
#============================================================================


def get_ui_platform(platform):
    if 'darwin' in platform:
        from mac import PwmanCliMacNew as PwmanCliNew
        OSX = True
    elif 'win' in platform:
        from win import PwmanCliWinNew as PwmanCliNew
        OSX = False
    else:
        from cli import PwmanCliNew
        OSX = False

    return PwmanCliNew, OSX
