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
