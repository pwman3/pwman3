#!/usr/bin/env python
"""
script to install pwman3
"""

from setuptools import setup
import pwman
import sys
from setuptools.command.install import install
import os
from subprocess import Popen,  PIPE

def describe():
    des = Popen('git describe', shell=True, stdout=PIPE)
    ver = des.stdout.readlines()
    if ver:
        return ver[0].strip()
    else:
        return pwman.version



class PyCryptoInstallCommand(install):
    """
    A Custom command to download and install pycrypto26
    binary from voidspace. Not optimal, but it should work ...
    """
    description = ("A Custom command to download and install pycrypto26"
                   "binary from voidspace.")

    def run(self):
        base_path = "http://www.voidspace.org.uk/downloads/pycrypto26"
        if 'win32' in sys.platform:
            if not 'AMD64' in sys.version:
                pycrypto = 'pycrypto-2.6.win32-py2.7.exe'
            else:  # 'for AMD64'
                pycrypto = 'pycrypto-2.6.win-amd64-py2.7.exe'
            os.system('easy_install '+base_path+'/'+pycrypto)
            install.run(self)
        else:
            print(('Please use pip or your Distro\'s package manager '
                   'to install pycrypto ...'))



setup(name=pwman.appname,
      version=describe(),
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
      package_data={"data": ["documentation"]},
      include_package_data=True,
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
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7'
      ],
      test_suite='pwman.tests.suite',
      cmdclass={
                'install_pycrypto': PyCryptoInstallCommand},

      )
