#!/usr/bin/env python

from distutils.core import setup
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
      )
