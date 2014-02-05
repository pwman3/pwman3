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

from ConfigParser import ConfigParser, ParsingError
import copy


class ConfigException(Exception):
    """Basic exception for config."""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "%s: %s" % (self.__class__.__name__, self.message)  # pragma: no cover


class ConfigNoConfigException(ConfigException):
    pass

_file = None
_conf = dict()
_defaults = dict()


def set_defaults(defaults):
    global _defaults
    _defaults = defaults


def add_defaults(defaults):
    global _defaults
    for n in defaults.keys():
        if not n in _defaults:
            _defaults[n] = dict()
        for k in defaults[n].keys():
            _defaults[n][k] = defaults[n][k]


def get_value(section, name):
    global _conf, _defaults
    try:
        return _conf[section][name]
    except KeyError, e:
        pass

    try:
        value = _defaults[section][name]
        set_value(section, name, value)
        return value
    except KeyError, e:
        pass

    return ''


def set_value(section, name, value):
    global _conf
    if not section in _conf:
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
            parser.readfp(fp)
        except ParsingError, e:
            raise ConfigException(e)
        except IOError, e:
            raise ConfigNoConfigException(e)
    finally:
        if (fp):
            fp.close()

    for section in parser.sections():
        for option in parser.options(section):
            set_value(section, option, parser.get(section, option))


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
                parser.set(key, optionkey, sectiondict[optionkey])
    try:
        fp = file(filename, "w+")
        parser.write(fp)
        fp.close()
    except IOError, e:
        raise ConfigException(str(e))
