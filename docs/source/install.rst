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

    $ pwman3 -i path_to_your_file.csv

When the import is done, start pwman3 with::
    
    $ pwman3 

If the import was success, erase the CSV file, which contains your passwords 
in clear text.

A Note about Python versions
----------------------------

Pwman3 was tested on Python versions 2.7-3.x. However, du to subtle differences
in PyCrypto, unicode and other stuff it is not recommended to use the same database
with different Python versions. 
Hence, if you are using Python version 2.7.x to run Pwman3 and later on you would 
like to change your default Python interpreter to Python 3 serious, it is recommended
that you export your database and re-import it to a new database created using Python 
3.X . 

Database versions 
----------------- 

The current version of Pwman3 is tested with Postgresql-9.3, MySQL-5.5,
MongoDB 2.6.X and SQLite3. 

The required python drivers are:
 
 * pymysql  version 0.6.6 
 * psycopg2 version 2.6
 * pymongo version 2.8
