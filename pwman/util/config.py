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
# Copyright (C) 2012 Oz Nahum <nahumoz@gmail.com>
# ============================================================================
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
# ============================================================================
import sys
import os

if sys.version_info.major > 2:  # pragma: no cover
    from configparser import (ConfigParser, ParsingError, NoOptionError,
                              NoSectionError, MissingSectionHeaderError)
else:                           # pragma: no cover
    from ConfigParser import (ConfigParser, ParsingError, NoOptionError,
                              NoSectionError, MissingSectionHeaderError)

config_dir = os.path.expanduser("~/.pwman")

default_config = {'Global': {'umask': '0100', 'colors': 'yes',
                             'cls_timeout': '10', 'cp_timeout': '5',
                             'save': 'True'
                             },
                  'Database': {
                      'dburi': 'sqlite://' + os.path.join(config_dir,
                                                          'pwman.db')},
                  'Readline': {'history': os.path.join(config_dir,
                                                       'history')},
                  'Crypto': {'supress_warning': 'no'},
                  }

if 'win' in sys.platform:
    default_config['Database']['dburi'] = default_config['Database']['dburi'].replace("\\", "/")

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
        defaults = defaults or default_config
        parser = ConfigParser()
        try:
            with open(self.filename) as f:
                try:
                    try:
                        parser.read_file(f)
                    except AttributeError:
                        parser.readfp(f)
                except (ParsingError, MissingSectionHeaderError) as e:
                    raise ConfigException(e)
        except IOError:
            self._self_write_new_conf(self.filename, defaults, parser)

        self._add_defaults(defaults, parser)
        return parser

    def _self_write_new_conf(self, filename, defaults, parser):
        self.parser = parser
        self._add_defaults(defaults, parser)
        self.save()

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

    def save(self):
        if not "False" in self.get_value("Global", "Save"):
            with open(self.filename, "w") as fp:
                self.parser.write(fp)


def get_pass_conf(config):
    ascii_lowercase = config.get_value("Generator",
                                       "ascii_lowercase").lower() == 'true'
    ascii_uppercase = config.get_value("Generator",
                                       "ascii_uppercase").lower() == 'true'
    ascii_digits = config.get_value("Generator",
                                    "ascii_digits").lower() == 'true'
    ascii_punctuation = config.get_value("Generator",
                                         "ascii_punctuation").lower() == 'true'
    return ascii_lowercase, ascii_uppercase, ascii_digits, ascii_punctuation
