Pwman3 - tutorial 
*****************

Pwman3 is a text centric password manager, and as such suitable for people wishing
to use it over SSH or brail terminals. 

Pwman3 is launched by typing ``pwman3`` in your shell. Multiple start options are 
available. You can see them by typing::
   
    $ pwman3 -h 

For more information see also ``man pwman3``. 

When started for the first time, ``pwman3`` will create a configuration file 
and your database (By default an SQLite database called ``pwman.db``) in your 
home directory under ``.pwman``.
Before creating the database you will be asked to enter the master password which 
will be used to create an encryption key which will be used to encrypt the entries 
in your database::

    $ pwman3 
    Please type in the master password:

Take note of this password! If you forget it, you won't be able to read your password
database. 

Now ``pwman3`` will wait for your input.  The user interface is 
a simple loop waiting for user commands. You can see all the commands by typing::

    pwman> help

    Documented commands (type help <topic>):
    ========================================
    cls   delete  exit    forget  list  open    print
    copy  edit    export  help    new   passwd  tags 

    Aliases:
    ========
    EOF  cp  h  ls  n  o  p  rm

Most commands have a single or two letter alias which is easy to remember. 

As for a start you would probably like to store some passwords in your database, all 
you need to do is type the command ``new`` (or the alias ``n``), and then insert the information
as promted::

    pwman> new
    Username: oz123
    Password: 
    Url: example.org
    Notes: Your notes      
    Tags: bank private

Note the password is typed in without echoing it. Also note that two tags were 
separated by a space. Now, you can list your database entries with::
    
    pwman> ls

    ID  USER        URL                 TAGS    
    1   oz123       example.org         bank, private

After a while you have had many new nodes inserted in your database::


    ID  USER        URL                     TAGS    
    1   oz123       example.org             bank, private
    2   oz123       intranet.workplace.biz  work
    3   oz123       shopping.com            shopping 

Now searching for a searching entry can become quite tiresome. Hence, you can 
minimize the number of entries display by applying a filter to the ``list`` 
command::

    pwman> ls work

    ID  USER        URL                 TAGS    
    2   oz123       intranet.workplace.biz  workplace

If you don't remember all the tags you created you can list the tags using the 
command ``tags``::
    
    pwman> tags
    Tags:
    bank,
    private,
    shopping

To see the content of a saved entry, you need to use the ``print`` command::

    pwman> print 2
    Username: oz123      
    Password: Org4n7#  
    URL: intranet.workplace.biz    
    Notes:           
    Tags: ['work']
    Type Enter to flush screen or wait 5 sec. 

Notice, that the ``print`` command expects an entry number as an argument. 
After printing the content of the entry, pwman3 will wait for ``Enter`` to be 
pressed or 5 seconds until it flushes the screen. This way, unautorized eyes 
can not browse your screen and see your password. You can always scroll up to 
see the printed entry or print it again. 

If you don't want to type passwords and urls constantly ``Pwman3`` comes with 
two shortcut commands. The first shortcut is ``open``, when calling it with 
an entry number it will open the URL in your default browser::
    
    pwman> open 2

This will open the URL *intranet.workplace.biz*. After opening the browser you can use the ``copy`` command to copy your password
to your clipboard. The password will be *erased* from the clipboard after 10 
seconds::

    pwman> copy 2
    erasing in 10 sec...

After working with passwords for quite a while you can ``delete`` (or ``rm``)
entries or edit them::

    pwman> rm 2
    Are you sure you want to delete node 2 [y/N]?N

    pwman> e 2
    Editing node 2.
    1 - Username: oz123
    2 - Password: Org4n7#
    3 - Url: intranet.workplace.biz
    4 - Notes: 
    5 - Tags: workplace
    X - Finish editing
    Enter your choice:

You now know all the basics of using ``pwman3``. If you need more help, try 
the command ``help`` to see more commands which are not documented here. 
Alternatively, you can open a ticket in https://github.com/pwman3/pwman3/issues.

