Packaging for UNIX\\Linux 
========================= 

Requirements and suggested packages
-----------------------------------
The most basic install of pwman requires Python 2.7.x or Python 3.x with 
SQLite support.
Some users might be interested in working with a network database such as 
MySQL or Postgreql, in this case the package should suggest to install but not 
depend on the following components:

    * `python-psycopg2`_
    * `python-pymysql`_

.. _python-psycopg2: https://pypi.python.org/pypi/psycopg2 
.. _python-pymysql: https://pypi.python.org/pypi/PyMySQL

Building a man page
-------------------

Many users of command line programs expect to find a man page for each and 
every program installed. Some Linux flavours has even made it a policy (for 
example `Debian Policy`_). 

If you would like to format a man page for Pwman3, this program provides a 
helper method for that::

     $ python setup.py build_manpage

This will create a man page `pwman3.1` in the directory where you issued the 
command. You can control the output by editing the option `output` in the file
`setup.cfg`.


.. _Debian Policy: https://www.debian.org/doc/debian-policy/ch-docs.html
