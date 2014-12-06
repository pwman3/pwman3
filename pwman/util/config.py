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
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
#============================================================================
import sys
import os

if sys.version_info.major > 2:  # pragma: no cover
    from configparser import (ConfigParser, ParsingError, NoOptionError,
                              NoSectionError)
else:                           # pragma: no cover
    from ConfigParser import (ConfigParser, ParsingError, NoOptionError,
                              NoSectionError)

config_dir = os.path.expanduser("~/.pwman")

default_config = {'Global': {'umask': '0100', 'colors': 'yes',
                             'cls_timeout': '5',
                             'save': 'True'
                             },
                  'Database': {'type': 'SQLite',
                               'filename': os.path.join(config_dir,
                                                        "pwman.db")},
                  'Encryption': {'algorithm': 'AES'},
                  'Readline': {'history': os.path.join(config_dir,
                                                       "history")}
                  }


class ConfigException(Exception):
    """Basic exception for config."""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__,
                               self.message)  # pragma: no cover


class ConfigNoConfigException(ConfigException):
    pass


class Config(object):

    def __init__(self, filename=None, defaults=None, **kwargs):

        self.filename = filename
        self.parser = self._load(defaults)

    def _load(self, defaults):
        try:
            parser = ConfigParser(defaults)
            with open(self.filename) as f:
                try:
                    parser.read_file(f)
                except AttributeError:
                    parser.readfp(f)
        except ParsingError as e:  # pragma: no cover
            raise ConfigException(e)

        self._add_defaults(defaults, parser)

        return parser

    def _add_defaults(self, defaults, parser):
        for section, options in defaults.items():
            if not parser.has_section(section):
                parser.add_section(section)

            for key, value in options.items():
                if not parser.has_option(section, key):
                    parser.set(section, key, value)

    def get_value(self, section, name):
        try:
            return self.parser.get(section, name)
        except (NoOptionError, NoSectionError):  # pragma: no cover
            return ''

    def set_value(self, section, name, value):
        self.parser.set(section, name, value)

    def save(self, filename):
        with open(filename, "w+") as fp:
            self.parser.write(fp)


def get_pass_conf(config):
    numerics = config.get_value("Generator", "numerics").lower() == 'true'
    # TODO: allow custom leetifying through the config
    leetify = config.get_value("Generator", "leetify").lower() == 'true'
    special_chars = config.get_value("Generator",
                                     "special_chars").lower() == 'true'
    return numerics, leetify, special_chars
