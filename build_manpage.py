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

"""


import datetime
from distutils.core import Command
from distutils.errors import DistutilsOptionError
import argparse


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

        self._parser.formatter_class = ManPageFormatter
        self.announce('Writing man page %s' % self.output)
        self._today = datetime.date.today()

    def _markup(self, txt):
        return txt.replace('-', '\\-')

    def _write_header(self):
        
        appname = self.distribution.get_name()
        ret = []
        
        ret.append(self._parser.formatter_class._mk_title(self._parser._get_formatter(), 
                                                          appname))
        description = self.distribution.get_description()
        
        if description:
            name = self._markup('%s - %s' % (self._markup(appname),
                                             description.splitlines()[0]))
        else:
            name = self._markup(appname)
        ret.append('.SH NAME\n%s\n' % name)
        

        self._parser._prog = appname
        ret.append(self._parser.formatter_class._mk_synopsis(self._parser._get_formatter(), 
                                                        self._parser))
                                                                                                         
        ret.append(self._parser.formatter_class._mk_description(self._parser._get_formatter(), 
                                                                self.distribution))
        
        return ''.join(ret)

    def _write_options(self):
        ret = ['.SH OPTIONS\n']
        ret.extend(self._parser.formatter_class.format_options(self._parser))

        return ''.join(ret)

    def _write_footer(self):
        ret = []
        appname = self.distribution.get_name()
        author = '%s <%s>' % (self.distribution.get_author(),
                              self.distribution.get_author_email())
        ret.append(('.SH AUTHORS\n.B %s\nwas written by %s.\n'
                    % (self._markup(appname), self._markup(author))))
        homepage = self.distribution.get_url()
        ret.append(('.SH DISTRIBUTION\nThe latest version of %s may '
                    'be downloaded from\n'
                    '%s\n\n'
                    % (self._markup(appname), self._markup(homepage),)))
        return ''.join(ret)

    def run(self):
        manpage = []
        manpage.append(self._write_header())
        manpage.append(self._write_options())
        manpage.append(self._write_footer())
        stream = open(self.output, 'w')
        stream.write(''.join(manpage))
        stream.close()


class ManPageFormatter(argparse.HelpFormatter):
    
    def __init__(self,
                 prog,
                 indent_increment=2,
                 max_help_position=24,
                 width=None,
                 section=1):
        
        super(ManPageFormatter, self).__init__(prog)
        
        self._prog = prog
        self._section = 1
        self._today = datetime.date.today().strftime('%Y\\-%m\\-%d')
    
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
        # TODO: Override _fromat_usage, work in progress
        usage = self._format_usage(parser._prog, parser._actions, 
                                   parser._mutually_exclusive_groups, '')
        
        usage = usage.replace('%s ' % parser._prog, '')
        usage = '.SH SYNOPSIS\n \\fB%s\\fR %s\n' % (self._markup(parser._prog),
                                                       usage)
        return usage
        
    def _mk_title(self, prog):
        
        return '.TH {0} {1} {2}\n'.format(prog, self._section, 
                                          self._today)
    
    def _mk_description(self, distribution):
        
        long_desc = distribution.get_long_description()
        
        if long_desc:
            long_desc = long_desc.replace('\n', '\n.br\n')
            return '.SH DESCRIPTION\n%s\n' % self._markup(long_desc)
        else:
            return ''
    
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
        return formatter.format_help()

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
    
    def _format_usage(self, prog, actions, groups, prefix):
        
        # if usage is specified, use that
        # if usage is not None:
        #    usage = usage % dict(prog=self._prog)

        # if no optionals or positionals are available, usage is just prog
        #elif usage is None and not actions:
        #    usage = '%(prog)s' % dict(prog=self._prog)

        # if optionals and positionals are available, calculate usage
        #elif usage is None:
        if True:
            prog = '%(prog)s' % dict(prog=prog)

            # split optionals from positionals
            optionals = []
            positionals = []
            for action in actions:
                if action.option_strings:
                    optionals.append(action)
                else:
                    positionals.append(action)

            # build full usage string
            format = self._format_actions_usage
            action_usage = format(optionals + positionals, groups)
            usage = ' '.join([s for s in [prog, action_usage] if s])

            # wrap the usage parts if it's too long
            text_width = self._width - self._current_indent
            if len(prefix) + len(usage) > text_width:

                # break usage into wrappable parts
                part_regexp = r'\(.*?\)+|\[.*?\]+|\S+'
                opt_usage = format(optionals, groups)
                pos_usage = format(positionals, groups)
                opt_parts = _re.findall(part_regexp, opt_usage)
                pos_parts = _re.findall(part_regexp, pos_usage)
                assert ' '.join(opt_parts) == opt_usage
                assert ' '.join(pos_parts) == pos_usage

                # helper for wrapping lines
                def get_lines(parts, indent, prefix=None):
                    lines = []
                    line = []
                    if prefix is not None:
                        line_len = len(prefix) - 1
                    else:
                        line_len = len(indent) - 1
                    for part in parts:
                        if line_len + 1 + len(part) > text_width:
                            lines.append(indent + ' '.join(line))
                            line = []
                            line_len = len(indent) - 1
                        line.append(part)
                        line_len += len(part) + 1
                    if line:
                        lines.append(indent + ' '.join(line))
                    if prefix is not None:
                        lines[0] = lines[0][len(indent):]
                    return lines

                # if prog is short, follow it with optionals or positionals
                if len(prefix) + len(prog) <= 0.75 * text_width:
                    indent = ' ' * (len(prefix) + len(prog) + 1)
                    if opt_parts:
                        lines = get_lines([prog] + opt_parts, indent, prefix)
                        lines.extend(get_lines(pos_parts, indent))
                    elif pos_parts:
                        lines = get_lines([prog] + pos_parts, indent, prefix)
                    else:
                        lines = [prog]

                # if prog is long, put it on its own line
                else:
                    indent = ' ' * len(prefix)
                    parts = opt_parts + pos_parts
                    lines = get_lines(parts, indent)
                    if len(lines) > 1:
                        lines = []
                        lines.extend(get_lines(opt_parts, indent))
                        lines.extend(get_lines(pos_parts, indent))
                    lines = [prog] + lines

                # join lines into usage
                usage = '\n'.join(lines)

        # prefix with 'usage:'
        return '%s%s\n\n' % (prefix, usage)

#  build.sub_commands.append(('build_manpage', None))
