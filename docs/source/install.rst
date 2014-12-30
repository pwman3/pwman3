installing and upgrading:
========================= 

You can install pwman3 simply by unpacking the archive and running:

   $ pip install .

Inside the extraced directory. At the moment pypi still does not have 
the latest version of pwman3.

Upgrading from version 0.5.x
----------------------------

If you used the 0.5.x Tversion of ``pwman3`` your database is not compatible
with the new 0.6.x version of ``pwman3``. You need to export your database
to a CSV from version 0.5.3 with::

    pwman> export 

See ``help export`` when running pwman3 in version 0.5.3. 
Once exported you should rename your old database, to keep a backup of it.
Then you can install pwman3 in version 0.6.x as described above. When finished
you can import your passwords from the CSV to a new database with::

    $ pwman3 -i path_to_your_file.csv

When the import is done, start pwman3 with::
    
    $ pwman3 

If the import was success, erase the CSV file, which contains your passwords 
in clear text.


