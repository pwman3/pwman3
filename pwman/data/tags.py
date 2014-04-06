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
#============================================================================
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
#============================================================================

from pwman.util.crypto import CryptoEngine


class TagNew(object):

    def __init__(self, name):
        enc = CryptoEngine.get()
        self._name = enc.encrypt(name)

    def __eq__(self, other):  # pragma: no cover
        if other._name == self._name:
            return True
        else:
            return False

    def __str__(self):
        enc = CryptoEngine.get()
        return enc.decrypt(self._name)

    @property
    def name(self):
        enc = CryptoEngine.get()
        return enc.decrypt(self._name)

    @name.setter
    def name(self, value):
        enc = CryptoEngine.get()  # pragma: no cover
        self._name = enc.encrypt(value)  # pragma: no cover


class Tag(object):  # pragma: no cover
    """
    tags are specific strings used to classify nodes
    the methods in this class override some built-ins
    for strings.
    """
    #def __init__(self, name):
    #    self.set_name(name)

    def __eq__(self, other):
        if other._name == self._name:
            return True
        else:
            return False

    def get_name(self):
        enc = CryptoEngine.get()
        return enc.decrypt(self._name)

    def set_name(self, name):
        enc = CryptoEngine.get()
        self._name = enc.encrypt(name)

    def __str__(self):
        enc = CryptoEngine.get()
        return enc.decrypt(self._name)
