# PWMAN3 

[![Build Status](https://travis-ci.org/pwman3/pwman3.png?branch=master)](https://travis-ci.org/pwman3/pwman3)
[![Coverage Status](https://coveralls.io/repos/pwman3/pwman3/badge.png)](https://coveralls.io/r/pwman3/pwman3?branch=master)

A nice command line password manager, which is smart enough to use different SQL Databases (MySQL, SQLite, PostgreSQL).  
Pwman3 can also copy passwords to the clipboard (on Mac and Linux) without exposing them, so you save
some typing. 
Besides managing and storing passwords, Pwman3 can also generate passwords using different algorithms. 

## Nice Features in pwman3:

 * copying of passwords to clipboard
 * launching specific uri's with default browser
 * password generators
 * not really a user oriented feature. However, it guarantees the elimination of silly 
   bugs: pwman3 is test driven! 

## A very important note about security

   If you are a concerned about security, please note:
   PWMAN3 is a very very basic software, which was designed to be used in a safe environment. 
   - If you are afraid that PWMAN3 is to weak for your needs ... and you still want to try it, here
     are a few recommendations:
     1. Use the AES encryption, it is supposed to be better than Blowfish. 
     2. Don't store your Password Database in the Obvious place, and if your extremely paranoind
        store it completely away from your computer on a separate USB key. 
     3. Use a HARD to crack password to encrypt your database!
   - If you care, report bugs, and send patches. 
   - I would realy like you to use PWMAN3, so I could get feedback and more ideas, especially, if you
   know something about security (which is probably more than I know at the moment. 
   - Be patient, I am working on PWMAN on my free time, and for fun, so don't expect PWMAN3 to 
     do to more than storing your passwords. 
   
## Installing 

Pwman3 requires the following debian packages:
 
 python-colorama
 python-crypto 
 xsel - to copy password to clipboard on Linux
    
Pwman only supports Python 2.7. 

To install from source:

    $ python setup.py install

You can also install PWMAN3 using python pip:

    $ pip install pwman3

### Windows Users:

Before installing pwman3 you need to install PyCrypto. To you can install PyCrypto with:

    python setup install_pycrypto

When done, issue:
    
    python setup install

If you are more picky than than than you can compile PyCrypto using the instruction bellow.

After you downloaded the source code of 
pycrypto and extracted it do the following inisde the source code direcotry:

    C:\Temp\pycrypto> python setup.py build -c mingw32 
    C:\Temp\pycrypto> python setup.py bdist_wininst

Now you should be able to run pwman3 on Windows.

On Windows 7 64bit: 

PyCrypto builds with mingw gcc version 4.6.2. Note that you also need msys installed from mingw. 
The above setup commands won't work in the Windows command prompt. But they do work in 
the msys command prompt. 
You also need to edit the following file:

	C:\Python27\Lib\distutils\cygwinccompiler.py

Before doing anything on this file make sure you create a backup! After that remove all references
for ``-mno-cygwin`. 

and after all that, if you a security minded person, who is capable of using a command line password:
Do your self a favor and skip Windows. Try Linux\BSD\*Nix OS. 

## User Interface
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
