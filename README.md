# PWMAN3 

A nice command line password manager, which is smart enough to use different SQL Databases (MySQL, SQLite, BerkelyDB).  
Pwman3 can also copy passwords to the clipboard (on Mac and Linux) without exposing them, so you save
some typing. 
Besides managing and storing passwords, Pwman3 can also generate passwords using different algorithms. 
## Nice Features in pwman3:

 * copying of passwords to clipboard
 * lauching specific uri's with default browser
 * password generators

## Installing 

Pwman3 requires the following debian packages:
	
when using python 2.4:    
    
    python-pysqlite2
	python-celementtree
    python-crypto



when using python >= 2.5 
    
    python-crypto

for nicer functionality:
    xsel - to copy password to clipboard on Linux



Pwman now uses argparse, which is only
available in Python 2.7. Therefore, if you intend to use
pwman3 with an older version of Python, please do so before
installing:

    $ cp scripts/pwman3 scripts/pwman3_bkup
    $ cp scripts/pwman3_old scripts/pwman3

Note that the old startup script of pwman3 might have limited
functionality compared to the newer version. 

To install:

    $ python setup.py install

## ikegam's function 

 * making a password from the numeric character and the alphabet character ([A-Za-z0-9]).

   You can add a parametor for making the password to the config(~/.pwman/config).

   For Example)
     [Generator]
     numerics = true
     
 * Passwords can be l33tified similarly using the following.
     [Generator]
     leetify = true
 
 * Copying password to X11 or Mac clipbord:
  - On Mac OSX systems copying utilizes `pbcopy`  
  - On X11 Systems  Specify the path to `xsel` if you already have `~/.pwman/config` 
      [Global]
      xsel = yes
      xselpath = /usr/bin/xsel

 
     When launching `pwman` for the first time, it will try and look for 
     `xsel` and write the configuration properly. 

## Password leetifying

If you choose to leetify your passwords when generating passwords, 
e.g. `leetify = true` in `~/.pwman/config`, password lengths may exceed the length chosen. 
This is because certain letters will be replaced with 2 or more characters. 
That is, if an initial random password was generated as : `Murkahm1` it will eventually be
set to: `|\/|ur|<ham1`. To see to full leet list checkout line 79 in `pwman/util/generator.py`
or issue in your terminal: 

     python -c'from pwman.util import generator; print generator.leetlist'
