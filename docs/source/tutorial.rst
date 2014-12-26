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


