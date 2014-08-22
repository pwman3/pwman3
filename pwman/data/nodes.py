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

from pwman.util.crypto_engine import CryptoEngine


class NewNode(object):

    def __str__(self):  # pragma: no cover
        enc = CryptoEngine.get()
        try:
            tags = ', '.join([enc.decrypt(tag).strip() for tag in filter(None,
                             self._tags)])
        except Exception:
            tags = ', '.join([tag.strip() for tag in filter(None, self._tags)])

        user = enc.decrypt(self._username).strip()
        url = enc.decrypt(self._url).strip()
        return '{0}@{1}\t{2}'.format(user, url,
                                     tags)

    def dump_edit_to_db(self):
        dump = u""
        try:
            dump += u"username:"+self._username.decode()+u"##"
        except AttributeError:
            dump += u"username:"+self._username+u"##"
        try:
            dump += u"password:"+self._password.decode()+u"##"
        except AttributeError:
            dump += u"password:"+self._password+u"##"
        try:
            dump += u"url:"+self._url.decode()+u"##"
        except AttributeError:
            dump += u"url:"+self._url+u"##"
        try:
            dump += u"notes:"+self._notes.decode()+u"##"
        except AttributeError:
            dump += u"notes:"+self._notes+u"##"
        dump += u"tags:"
        tagsloc = u""
        for tag in self._tags:
            if isinstance(tag, str):
                tagsloc += u"tag:"+tag.strip()+u"**endtag**"
            if isinstance(tag, bytes):
                try:
                    tagsloc += u"tag:"+tag.decode()+u"**endtag**"
                except:
                    tagsloc += u"tag:"+tag+u"**endtag**"

            else:
                tagsloc += u'tag:'+tag._name+u'**endtag**'

        dump += tagsloc
        dump = [dump]
        return dump

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
            return [enc.decrypt(tag) for tag in filter(None, self._tags)]
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
