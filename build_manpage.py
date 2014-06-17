# -*- coding: utf-8 -*-

# This file is distributed under the same License of Python
# Copyright (c) 2014 Oz Nahum Tiram  <nahumoz@gmail.com>

"""
build_manpage.py

Add a `build_manpage` command  to your setup.py.
To use this Command class import the class to your setup.py,
and add a command to call this class::

    from build_manpage import BuildManPage

    ...
    ...

    setup(
    ...
    ...
    cmdclass={
        'build_manpage': BuildManPage,
    )

You can then use the following setup command to produce a man page::

    $ python setup.py build_manpage --output=prog.1 --parser=yourmodule:argparser

Alternatively, set the variable AUTO_BUILD to True, and just invoke::

    $ python setup.py build

If automatically want to build the man page every time you invoke your build,
add to your ```setup.cfg``` the following::

    [build_manpage]
    output = <appname>.1
    parser = <path_to_your_parser>
"""


import datetime
from distutils.core import Command
from distutils.errors import DistutilsOptionError
from distutils.command.build import build
import argparse
import re as _re

AUTO_BUILD = False

class BuildManPage(Command):

    description = 'Generate man page from an ArgumentParser instance.'

    user_options = [
        ('output=', 'O', 'output file'),
        ('parser=', None, 'module path to an ArgumentParser instance'
         '(e.g. mymod:func, where func is a method or function which return'
         'an arparse.ArgumentParser instance.'),
    ]

    def initialize_options(self):
        self.output = None
        self.parser = None

    def finalize_options(self):
        if self.output is None:
            raise DistutilsOptionError('\'output\' option is required')
        if self.parser is None:
            raise DistutilsOptionError('\'parser\' option is required')
        mod_name, func_name = self.parser.split(':')
        fromlist = mod_name.split('.')
        try:
            mod = __import__(mod_name, fromlist=fromlist)
            self._parser = getattr(mod, func_name)(formatter_class=ManPageFormatter)

        except ImportError as err:
            raise err

        self.announce('Writing man page %s' % self.output)
        self._today = datetime.date.today()

    def _markup(self, txt):
        return txt.replace('-', '\\-')

    def _write_header(self):

        appname = self.distribution.get_name()
        ret = []

        formater = self._parser._get_formatter()
        ret.append(self._parser.formatter_class._mk_title(formater, appname))
        description = self.distribution.get_description()

        ret.append(self._parser.formatter_class._make_name(formater,
                                                           self._parser))
        self._parser._prog = appname
        ret.append(self._parser.formatter_class._mk_synopsis(formater,
                                                             self._parser))
        formater.long_desc = self.distribution.get_description()
        ret.append(self._parser.formatter_class._mk_description(formater))

        return ''.join(ret)

    def _write_options(self):
        return self._parser.formatter_class.format_options(self._parser)

    def _write_footer(self):
        """
        Writing the footer allows one to add a lot of extra information.
        Sections and and their content can be specified in the dictionary
        sections which is passed to the formater method
        """
        appname = self.distribution.get_name()
        homepage = self.distribution.get_url()
        sections = {'authors': ("pwman3 was originally written by Ivan Kelly "
                                "<ivan@ivankelly.net>.\n pwman3 is now maintained "
                                "by Oz Nahum <nahumoz@gmail.com>."),
                    'distribution': ("The latest version of {} may be "
                                     "downloaded from {}".format(appname,
                                                                 homepage))
                    }

        return self._parser.formatter_class._mk_footer(self._parser._get_formatter(),
                                                       sections)

    def run(self):

        manpage = []
        manpage.append(self._write_header())
        manpage.append(self._write_options())
        manpage.append(self._write_footer())
        stream = open(self.output, 'w')
        stream.write(''.join(manpage))
        stream.close()


class ManPageFormatter(argparse.HelpFormatter):
    """
    Formatter class to create man pages.
    Ideally, this class should rely only on the parser, and not distutils.
    The following shows a scenario for usage::

        from pwman import parser_options
        from build_manpage import ManPageFormatter

        p = parser_options(ManPageFormatter)
        p.format_help()

    The last line would print all the options and help infomation wrapped with
    man page macros where needed.
    """

    def __init__(self,
                 prog,
                 indent_increment=2,
                 max_help_position=24,
                 width=None,
                 section=1,
                 desc=None,
                 long_desc=None,
                 authors=None,
                 distribution=None):

        super(ManPageFormatter, self).__init__(prog)

        self._prog = prog
        self._section = 1
        self._today = datetime.date.today().strftime('%Y\\-%m\\-%d')

    def _get_formatter(self, **kwargs):
        return self.formatter_class(prog=self.prog, **kwargs)

    def _markup(self, txt):
        return txt.replace('-', '\\-')

    def _underline(self, string):
        return "\\fI\\s-1" + string + "\\s0\\fR"

    def _bold(self, string):
        if not string.strip().startswith('\\fB'):
            string = '\\fB' + string
        if not string.strip().endswith('\\fR'):
            string = string + '\\fR'
        return string

    def _mk_synopsis(self, parser):
        self.add_usage(parser.usage, parser._actions,
                       parser._mutually_exclusive_groups, prefix='')
        usage = self._format_usage(None, parser._actions,
                                   parser._mutually_exclusive_groups, '')

        usage = usage.replace('%s ' % parser._prog, '')
        usage = '.SH SYNOPSIS\n \\fB%s\\fR %s\n' % (self._markup(parser._prog),
                                                       usage)
        return usage

    def _mk_title(self, prog):
        return '.TH {0} {1} {2}\n'.format(prog, self._section,
                                          self._today)

    def _make_name(self, parser):
        """
        this method is in consitent with others ... it relies on
        distribution
        """
        return '.SH NAME\n%s \\- %s\n' % (parser.prog,
                                          parser.description)

    def _mk_description(self):
        if self.long_desc:
            long_desc = self.long_desc.replace('\n', '\n.br\n')
            return '.SH DESCRIPTION\n%s\n' % self._markup(long_desc)
        else:
            return ''

    def _mk_footer(self, sections):
        footer = []
        for section, value in sections.iteritems():
            part = ".SH {}\n {}".format(section.upper(), value)
            footer.append(part)

        return '\n'.join(footer)

    @staticmethod
    def format_options(parser):

        formatter = parser._get_formatter()

        # positionals, optionals and user-defined groups
        for action_group in parser._action_groups:
            formatter.start_section(None)
            formatter.add_text(None)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        # epilog
        formatter.add_text(parser.epilog)

        # determine help from format above
        return '.SH OPTIONS\n' + formatter.format_help()

    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar

        else:
            parts = []

            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend([self._bold(action_str) for action_str in action.option_strings])

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            else:
                default = self._underline(action.dest.upper())
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    parts.append('%s %s' % (self._bold(option_string), args_string))

            return ', '.join(parts)


class ManPageCreator(object):
    """
    This class takes a little different approach. Instead of relying on
    information from ArgumentParser, it relies on information retrieved
    from distutils.
    This class makes it easy for package maintainer to create man pages in cases,
    that there is no ArgumentParser.
    """
    pass

    def _mk_name(self, distribution):
        """
        """
        return '.SH NAME\n%s \\- %s\n' % (distribution.get_name(),
                                          distribution.get_description())

if AUTO_BUILD:
    build.sub_commands.append(('build_manpage', None))
