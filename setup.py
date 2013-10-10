#!/usr/bin/env python
"""
script to install pwman3
"""

from setuptools import setup
import pwman
import sys
from setuptools.command.install import install
import os
import urllib
import shutil


class PyCryptoInstallCommand(install):
    """
    A Custom command to download and install pycrypto26
    binary from voidspace. Not optimal, but it should work ...
    """
    description = ("A Custom command to download and install pycrypto26"
                   "binary from voidspace.")

    def run(self):
        if 'win32' in sys.platform:
            if not os.path.exists('./.setup'):
                os.mkdir('./.setup')
            urllib.urlretrieve(("http://www.voidspace.org.uk/downloads/"
                               "pycrypto26/pycrypto-2.6.win32-py2.7.exe"),
                               os.path.join('.', 'setup',
                                            ('pycrypto-2.6.win32-py2.7.exe')))
            os.system('easy_install '
                      + os.path.join('.', '.setup',
                                     'pycrypto-2.6.win32-py2.7.exe'))
            install.run(self)
            shutil.rmtree('.', '.setup')
        else:
            print(('Please use pip or your Distro\'s package manager '
                   'to install pycrypto ...'))


setup(name=pwman.appname,
      version=pwman.version,
      description=pwman.description,
      author=pwman.author,
      author_email=pwman.authoremail,
      url=pwman.website,
      license="GNU GPL",
      packages=['pwman',
                'pwman.data',
                'pwman.data.drivers',
                'pwman.exchange',
                'pwman.ui',
                'pwman.util'],
      scripts=['scripts/pwman3'],
      zip_safe=False,
      install_requires=['pycrypto>=2.6',
                        'colorama>=0.2.4'],
      classifiers=[
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7'
      ],
      test_suite='pwman.tests',
      cmdclass={'install_pycrypto': PyCryptoInstallCommand},

      )
