Configuring Pwman3
================== 

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
    filename = sqlite:///<PWMAN_CONFIG>/pwman.db`
    

Following is a table describing the parameters and their meanings:


    ===========   ===========
    **Section**   *Readline* 
    -----------   -----------
                  *Global*
    history       path to the file containing history of commands typed
    -----------   -----------
    **Section**   *Global* 
    -----------   -----------
    save          True or False - whether the Configuring file should be saved
    -----------   -----------
    colors        yes or no - If set to *no*, no colors used in output. This is useful for breil terminals. 
    -----------   -----------
    cp_timeout    Number of seconds before the clipboard is erased.
    -----------   -----------
    cls_timeout   Number of seconds before the screen is clean after a print.
    -----------   -----------
    umask         The umask in which database and configuration files are written.
    -----------   -----------
    xsel          path to the xsel binary (Linux\BSD only) 
    -----------   -----------
    **Section**   *Database* 
    -----------   -----------
    dburi         Database URI conforming to `RFC3986`_. SQLite, Postgreql, 
                  MySQL and MongoDB are currently supported. 
       
                  SQLite example: `sqlite:///path/to/your/db`

                  Postgreql example: `postgresql://<user>:<pass>@<host[:port]>/<database>`

                  MySQL example:     `mysql://<user>:<pass>@<host[:port]>/<database>`
                  
                  MongoDB example:   `mongodb://<user>:<pass>@<host[:port]>/<database>`
    ===========   ===========


.. _RFC3986: http://www.ietf.org/rfc/rfc3986.txt

