Installing and upgrading:
========================= 

You can get the latest stable version of pwman3 from pypi::

   $ pip install pwman3 

Or you can install pwman3 cloning the repository and running::
    
   $ git clone https://github.com/pwman3/pwman3.git
   $ cd pwman3 && pip install .

Inside the extraced directory. At the moment pypi still does not have 
the latest version of pwman3.


Upgrading from version 0.5.x
----------------------------

If you used the 0.5.x version of ``pwman3`` your database is not compatible
with the new 0.6.x and later versions of ``pwman3``. You need to export your database
to a CSV from version 0.5.3 with::

    pwman> export 

See ``help export`` when running pwman3 in version 0.5.3. 
Once exported you should rename your old database, to keep a backup of it.
Then you can install pwman3 in version 0.6.x or later as described above. When finished
you can import your passwords from the CSV to a new database with::

    $ pwman3 -i path_to_your_file.csv \;

The `\;` tells the importer that the file is semi-colon separated.
When the import is done, start pwman3 with::
    
    $ pwman3 

If the import was success, erase the CSV file, which contains your passwords 
in clear text.

Upgrading from version 0.6 or later:
------------------------------------

Once again the latest release (version 0.9) breaks compatibility with earlier
versions. As a user you might consider this an annoyance, which is understandable.
However, older Pwman3 version used a very old cryptography library which is
no longer actively maintained. With the migration of the code base to use
the cryptography_ library, there was a necessary change of the underlying
encryption algorithm. AES encryption with ECB mode was the old algorithm used, 
which is by now considered outdated, and it was replaced with Fernet encryption
which is considered best practice.

To upgrade, follow the path described above to export your database to a CSV,
and the import it.

A Note about Python versions
----------------------------

Earlier versions of Pwman3 supported both Python2 and Python3 versions. This
created a bit of an effort for maintaining version compatablity, and served
as a migration path for future versions. Python 3 has been around now for quite
a while, and soon enough, Python2 support will end. Python 3 is mature enough, 
and offers many improvements for developers. Python 3.4 is included in all major
modern Linux distributions.
If you use a certain enterprise Linux versions which does not ship Python 3.3
or later, the process for installing a newer Python versions is pretty straight
forward and very well documented. You should opt for using newer Python versions
for all your software if possible.

If you want to learn more about why Python 3, see the following `Python3 statement`_

Database versions 
----------------- 

The current version of Pwman3 is tested with Postgresql-9.3, MySQL-5.5,
MongoDB 2.6.X and SQLite3. 

The required python drivers are:
 
 * pymysql  version 0.6.6 
 * psycopg2 version 2.6
 * pymongo version 2.8

.. _cryptography: https://cryptography.io
.. _Python3 statement: https://python3statement.github.io/
