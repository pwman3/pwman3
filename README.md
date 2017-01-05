# PWMAN3 

[![Build Status](https://travis-ci.org/pwman3/pwman3.png?branch=master)](https://travis-ci.org/pwman3/pwman3)
[![Build status](https://ci.appveyor.com/api/projects/status/9yxwlj5d15bitshr?svg=true)](https://ci.appveyor.com/project/oz123/pwman3)
[![Coverage Status](https://coveralls.io/repos/pwman3/pwman3/badge.png)](https://coveralls.io/r/pwman3/pwman3?branch=develop)
[![Documentation Status](https://readthedocs.org/projects/pwman3/badge/?version=latest)](https://readthedocs.org/projects/pwman3/?badge=latest)

A nice command line password manager, which can use different database to store your passwords (currently, SQLite, MySQL, 
    and Postgresql and MongoDB are supported).
Pwman3 can also copy passwords to the clipboard without exposing them!
Besides managing and storing passwords, Pwman3 can also generate passwords using different algorithms. 

## Nice Features in pwman3:
 
 * Strong AES Encryption
 * copying of passwords to clipboard
 * launching specific uri's with default browser
 * password generators
 * not really a user oriented feature. However, it guarantees the elimination of silly 
   bugs: pwman3 is test driven! 

## Documentation

    http://pwman3.readthedocs.org/en/latest/

## A very important note about security

   If you are a concerned about security, please note:
   PWMAN3 is a very very basic software, which was designed to be used in a safe environment. 
   - If you are afraid that PWMAN3 is to weak for your needs ... and you still want to try it, here
     are a few recommendations:
     1. Don't store your Password Database in the Obvious place, and if your extremely paranoind
        store it completely away from your computer on a separate USB key. 
     2. Use a HARD to crack password to encrypt your database!
   - If you care, report bugs, and send patches. 
   - I would realy like you to use PWMAN3, so I could get feedback and more ideas, especially, if you
   know something about security! 
   
## Installing 

Pwman3 requires the following debian packages:
 
 python-colorama 
 xsel - to copy password to clipboard on Linux

It is also recommended to install python-crypto.
Pwman supports Python 3.x. 

To install from source:

    $ python setup.py install

You can also install PWMAN3 using python pip:

    $ pip install pwman3


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
 * making a password from the numeric character and the alphabet character ([A-Za-z0-9]).

   You can add a parameter for making the password to the config(~/.pwman/config).

   For Example:
     
     ```
     [Generator]
     numerics = true
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
     Pwman3 0.6.0 (c) visit: http://github.com/pwman3/pwman3
     pwman> n {'leetify':False, 'numerics':True, 'special_signs':True}
     Username: username
     Password length (default 8): 12
     New password: Q1dab@7abcd5
     ``` 
 
 * Default password length can be changed by: 

    ```
    [Generator]
    default_pw_length = 42
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

## Supporting

If you find this work useful, you can do one or more of the following:

	* Star this repository.
	* Tweeter me with a thank you.
	* Donate me a humlbe sum of 5-10€. (Donations should go to oz dot tiram at gmail dot com), I'll mention you here for supporting my work.

