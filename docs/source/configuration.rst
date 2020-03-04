Configuring Pwman3
==================

By default Pwman3 will read the configuration file from the following path on Unix like systems::

    ~/.config/pwman/config

On windows the configuration is found in ``%APPDATA/pwman/%``

You can override this by giving the ``-c <Config File>`` at the commnad line
when starting Pwman3.

The configuration file has the following structure::

    [Section]
    Option = Value

The following is an example default config file::

    [Readline]
    history = <PWMAN_DATA_DIR>/history

    [Global]
    save = True
    colors = yes
    cp_timeout = 5
    umask = 0100
    cls_timeout = 10
    xsel = /usr/bin/xsel
    lock_timeout = 60

    [Database]
    filename = sqlite:///<PWMAN_DATA_DIR>/pwman.db`

    [Updater]
    supress_version_check = no
    client_info = ee5cd64310568736b971e3fb7c7064a4459b99a2b78672515fd0f06c82f65d5

On Windows ``PWMAN_DATA_DIR`` is ``%APPDATA/pwman/%`` on Unix like systems it is

``~/.local/share/pwman/``.


A detailed table of all configuration parameters is found in :py:class:`pwman.util.config.Config`.


