Configuring Pwman3:
=================== 

By default Pwman3 will read the configuration file from the following path::

    ~/.pwman/config 

This is the ``PWMAN_CONFIG`` following. 

You can override this by giving the ``-c <Config File>`` at the commnad line 
when starting Pwman3. 

The configuration file has the following structure::

    [Section]
    Option = Value

The following is an example default config file::
    
    [Readline]
    history = <PWMAN_CONFIG>/history

    [Global]
    save = True
    colors = yes
    cp_timeout = 5
    umask = 0100
    cls_timeout = 10
    xsel = /usr/bin/xsel

    [Database]
    type = SQLite
    filename = <PWMAN_CONFIG>/pwman.db
    

