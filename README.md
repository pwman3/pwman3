# PWMAN3 

A nice command line password manager, which is smart enough to use different SQL Databases (MySQL, SQLite, PostgreSQL).  
Pwman3 can also copy passwords to the clipboard (on Mac and Linux) without exposing them, so you save
some typing. 
Besides managing and storing passwords, Pwman3 can also generate passwords using different algorithms. 
## Nice Features in pwman3:

 * copying of passwords to clipboard
 * lauching specific uri's with default browser
 * password generators

## A very important note about security

   If you are a concerned about security, please note:
   PWMAN3 is a very very basic software, which was designed to be used in a safe environment. 
   - it does not - at the moment - include enchanched security features, due to lack of resourecs. 
   - I would realy like you to use PWMAN3, so I could get feedback and more ideas, especially, if you
   know something about security (which is probably more than I know at the moment. 
   - Be patient, I am working on PWMAN on my free time, and for fun, so don't expect PWMAN3 to 
     do to more than storing your passwords. 
   - If you are afraid that PWMAN3 is to weak for your needs ... and you still want to try it, here
     are a few recommendations:
     1. Use the AES encryption, it is supposed to be better the Blowfish. 
     2. Don't store your Password Database in the Obvious place, and if your extremely paranoind
        store it completely away from your computer on a separate USB key. 
     3. Use a HARD to crack password to encrypt your database!
   - If you care, report bugs, and send patches. 
   
## Installing 

Pwman3 requires the following debian packages:
 
when using python 2.4:    
    
    python-pysqlite2
    python-celementtree
    python-crypto

when using python >= 2.5 
    
    python-crypto (>=2.6) from upstream (currently broken with 
    pycrypto from Debian).

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

## User Insterface

   1. When xsel is install on a Linux system, you can copy passwords directly to clipboard with the copy command.
   2. The command 'open' will open the default browser if URL is specified.
   3. An automatic 'clear screen' function is called after printing an entry in the database. 
      The screen will be cleared after 5 seconds by default. However, this can be changed by changing the 
      correct value in `~.pwman/config`:
      
      ```
      [Global]
      ...
      cls_timeout = 10
      ```
      To disable the automatic 'clear screen' functionality set `cls_timeout` to a negative integer. 

      ```
      [Global]
      ...
      cls_timeout = -1
      ```


## ikegam's function 

 * making a password from the numeric character and the alphabet character ([A-Za-z0-9]).

   You can add a parameter for making the password to the config(~/.pwman/config).

   For Example:
     
     ```
     [Generator]
     numerics = true
     ```

 * Passwords can be l33tified similarly using the following.
     
     ```
     [Generator]
     leetify = true
     ```
 * Passwords can contain one of the following special signs:
    
    ```
    specialsigns = ["@", "#", "?", "!", '\\', "|", "$",
                     "%", "^", "&", "*", "(", ")", ":", ";",
                     "{", "}", "+","-"]
    ```
The config file  must have the following option:
    
    ```
    [Generator]
    special_signs = true
    ```

 * Individual password policy can be chosen with:
 
     ```
     Pwman3 0.2.1 (c) visit: http://github.com/pwman3/pwman3
     pwman> n {'leetify':False, 'numerics':True, 'special_signs':True}
     Username: username
     Password length (default 7): 7
     New password: Q1dab@7
     ``` 
   
 * Copying password to X11 or Mac clip board:
  - On Mac OSX systems copying utilizes `pbcopy`  
  - On X11 Systems  Specify the path to `xsel` if you already have `~/.pwman/config` 
      
     ```
     [Global]
     xsel = yes
      xselpath = /usr/bin/xsel
     ```
 
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
