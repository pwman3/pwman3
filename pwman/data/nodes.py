# ============================================================================
# :This file is part of Pwman3.
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
# Copyright (C) 2012-2014 Oz Nahum <nahumoz@gmail.com>
# ============================================================================
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
# ============================================================================
from colorama import Fore
from pwman.util.crypto_engine import CryptoEngine
import pwman.ui.tools


class Node(object):

    def __init__(self, clear_text=True, **kwargs):
        if clear_text:
            enc = CryptoEngine.get()
            self._username = enc.encrypt(kwargs.get('username')).strip()
            self._password = enc.encrypt(kwargs.get('password')).strip()
            self._url = enc.encrypt(kwargs.get('url')).strip()
            self._notes = enc.encrypt(kwargs.get('notes')).strip()
            self._tags = [enc.encrypt(t).strip() for t in kwargs.get('tags',
                                                                     '')]

    def __str__(self):
        p = "{entry_title:>{width}} {entry:<{width}}\n".format(
            entry_title=pwman.ui.tools.typeset('Username:', Fore.RED),
            width=10, entry=str(self.username.decode()))
        p += "{entry_title:>{width}} {entry:<{width}}\n".format(
            entry_title=pwman.ui.tools.typeset('Password:', Fore.RED),
            width=10, entry=str(self.password.decode()))
        p += "{entry_title:>{width}} {entry:<{width}}\n".format(
            entry_title=pwman.ui.tools.typeset('URL:', Fore.RED),
            width=10, entry=str(self.url.decode()))
        p += "{entry_title:>{width}} {entry:<{width}}\n".format(
            entry_title=pwman.ui.tools.typeset('Notes:', Fore.RED),
            width=10, entry=str(self.notes.decode()))
        p += "{entry_title:>{width}} {entry:<{width}}\n".format(
            entry_title=pwman.ui.tools.typeset('Tags:', Fore.RED),
            width=10, entry=str(self.tags))
        return p

    @classmethod
    def from_encrypted_entries(cls, username, password, url, notes, tags):
        """
        We use this alternatively, to create a node instance when reading
        the encrypted entities from the database
        """
        node = Node(clear_text=False)
        node._username = username.strip()
        node._password = password.strip()
        node._url = url.strip()
        node._notes = notes.strip()
        node._tags = [t.strip() for t in tags]
        return node

    def __iter__(self):
        for item in ['_username', '_password',
                     '_url', '_notes']:
            yield getattr(self, item)
        yield self._tags

    @property
    def password(self):
        """Get the current password."""
        enc = CryptoEngine.get()
        return enc.decrypt(self._password).strip()

    @property
    def username(self):
        """Get the current username."""
        enc = CryptoEngine.get()
        return enc.decrypt(self._username).strip()

    @username.setter
    def username(self, value):
        """Set the username."""
        enc = CryptoEngine.get()
        self._username = enc.encrypt(value).strip()

    @password.setter
    def password(self, value):
        """Set the Notes."""
        enc = CryptoEngine.get()
        self._password = enc.encrypt(value).strip()

    @property
    def tags(self):
        enc = CryptoEngine.get()
        try:
            return [enc.decrypt(tag) for tag in
                    filter(None, self._tags)]
        except Exception:
            return [tag for tag in filter(None, self._tags)]

    @tags.setter
    def tags(self, value):
        self._tags = [tag for tag in value]

    @property
    def url(self):
        """Get the current url."""
        enc = CryptoEngine.get()
        return enc.decrypt(self._url).strip()

    @url.setter
    def url(self, value):
        """Set the Notes."""
        enc = CryptoEngine.get()
        self._url = enc.encrypt(value).strip()

    @property
    def notes(self):
        """Get the current notes."""
        enc = CryptoEngine.get()
        return enc.decrypt(self._notes).strip()

    @notes.setter
    def notes(self, value):
        """Set the Notes."""
        enc = CryptoEngine.get()
        self._notes = enc.encrypt(value).strip()
