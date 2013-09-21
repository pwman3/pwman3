#!/usr/bin/env python
"""
script to install pwman3
"""

#from distutils.core import setup
from setuptools import Command, setup
import pwman


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
          ]
)
