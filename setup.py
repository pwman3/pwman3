#!/usr/bin/env python
"""
script to install pwman3
"""
import argparse
import datetime
import os
import sys

from setuptools import setup
from setuptools import find_packages
from distutils.core import Command
from distutils.errors import DistutilsOptionError

# The BuildManPage code is distributed
# under the same License of Python
# Copyright (c) 2014 Oz Nahum Tiram  <nahumoz@gmail.com>

"""
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

    $ python setup.py build_manpage --output=prog.1
        --parser=yourmodule:argparser

Alternatively, set the variable AUTO_BUILD to True, and just invoke::

    $ python setup.py build

If automatically want to build the man page every time you invoke your build,
add to your ```setup.cfg``` the following::

    [build_manpage]
    output = <appname>.1
    parser = <path_to_your_parser>
"""


# build.sub_commands.append(('build_manpage', None))

class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        import subprocess

        raise SystemExit(
            subprocess.call([sys.executable,
                             '-m',
                             'tests.test_pwman']))


class IntegrationTestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        import subprocess

        raise SystemExit(
            subprocess.call([sys.executable,
                             '-m',
                             'tests.test_integration']))


sys.path.insert(0, os.getcwd())


install_requires = ['colorama>=0.2.4', 'cryptography']

if sys.platform.startswith('win'):
    install_requires.append('pyreadline3')


long_description = u"""\
Pwman3 aims to provide a simple but powerful commandline interface for
password management.
It allows one to store passwords in database locked by master password which
is AES encrypted.
Pwman3 supports MySQL, Postgresql and SQLite and even MongoDB"""

packages = find_packages(exclude=['tests'])

import pwman

setup(name='pwman3',
      version=pwman.version,
      description=("a command line password manager with support for multiple"
                   " databases."),
      long_description=long_description,
      author='Oz Nahum Tiram',
      author_email='nahumoz@gmail.com',
      url='http://pwman3.github.io/pwman3/',
      license="GNU GPL",
      packages=packages,
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      keywords="password-manager crypto cli",
      classifiers=['Environment :: Console',
                   'Intended Audience :: End Users/Desktop',
                   'Intended Audience :: Developers',
                   'Intended Audience :: System Administrators',
                   ('License :: OSI Approved :: GNU General Public License'
                    ' v3 or later (GPLv3+)'),
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.9',
                   'Programming Language :: Python :: 3.10',
                   'Programming Language :: Python :: 3.11',
                   ],
      cmdclass={
          'build_manpage': BuildManPage,
          'test': TestCommand,
          'integration': IntegrationTestCommand
      },
      entry_points={
          'console_scripts': ['pwman3 = pwman.ui.cli:main']
          }
      )
