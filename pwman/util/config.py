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

if sys.version_info.major > 2:
    from configparser import ConfigParser, ParsingError, NoOptionError
else:
    from ConfigParser import ConfigParser, ParsingError, NoOptionError
import copy

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

_file = None
_conf = dict()
_defaults = dict()


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
        except ParsingError as e:
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
        except NoOptionError:
            return ''

    def set_value(self, section, name, value):
        self.parser.set(section, name, value)


def set_conf(conf_dict):
    global _conf
    _conf = conf_dict


def set_defaults(defaults):
    global _defaults
    _defaults = defaults


def add_defaults(defaults):
    global _defaults
    for n in defaults.keys():
        if n not in _defaults:
            _defaults[n] = dict()
        for k in defaults[n].keys():
            _defaults[n][k] = defaults[n][k]


def get_value(section, name):
    global _conf, _defaults
    try:
        return _conf[section][name]
    except KeyError:
        pass

    try:
        value = _defaults[section][name]
        set_value(section, name, value)
        return value
    except KeyError:
        pass

    return ''


def set_value(section, name, value):
    global _conf
    if section not in _conf:
        _conf[section] = dict()
    _conf[section][name] = value


def get_conf():
    """
    Get a copy of the config.
    Modifications have no effect.
    This function only serves for allowing applications
    to output the config to the user"""
    global _conf
    return copy.deepcopy(_conf)


def load(filename):
    """Load configuration from 'filename'."""
    global _conf, _file

    _file = filename

    parser = ConfigParser()

    fp = None
    try:
        try:
            fp = open(filename, "r")
            try:
                parser.read_file(fp)
            except AttributeError:
                parser.readfp(fp)
        except ParsingError as e:
            raise ConfigException(e)
        except IOError as e:
            raise ConfigNoConfigException(e)
    finally:
        if (fp):
            fp.close()

    for section in parser.sections():
        for option in parser.options(section):
            set_value(section, option, parser.get(section, option))


def set_config(config_dict):
    global _conf
    _conf = config_dict


def save(filename=None):
    """Save the configuration to 'filename'."""
    global _conf, _file
    if not filename:
        filename = _file

    parser = ConfigParser()
    for key in _conf.keys():
        if not parser.has_section(key):
            parser.add_section(key)
        sectiondict = _conf[key]
        if isinstance(sectiondict, dict):
            for optionkey in sectiondict.keys():
                parser.set(key, optionkey, str(sectiondict[optionkey]))
    try:
        fp = open(filename, "w+")
        parser.write(fp)
        fp.close()
    except IOError as e:
        raise ConfigException(str(e))


def get_pass_conf():
    numerics = get_value("Generator", "numerics").lower() == 'true'
    # TODO: allow custom leetifying through the config
    leetify = get_value("Generator", "leetify").lower() == 'true'
    special_chars = get_value("Generator", "special_chars").lower() == 'true'
    return numerics, leetify, special_chars
