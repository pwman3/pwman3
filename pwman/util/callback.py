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
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
#============================================================================

"""Callback interface
To be used when UI needs to be back to get info from user.
"""

class Callback:
    """Callback interface. Callback classes must implement this."""
    def getinput(self, question):
        """Return text"""
        pass
    
    def getsecret(self, question):
        """Return key"""
        pass

    def error(self, error):
        """Present error to user"""
        pass

    def warning(self, warning):
        """Present warning to user"""
        pass

    def notice(self, warning):
        """Present notice to user"""
        pass


class CallbackCancelException(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return "CallbackCancelException: %s" % (self.message)

