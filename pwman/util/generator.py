#============================================================================
# This file is part of Pwman3.
# 
# Pwman3 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2
# as published by the Free Software Foundation; 
# 
# Pwman3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Pwman3; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#============================================================================
# Copyright (C) 2006 Ivan Kelly <ivan@ivankelly.net>
#============================================================================

"""
Functions to generate passwords.
Based heavily on passogva.py (c) 2004 Mo-Tsuki, LLC.
http://dev.mosuki.com/passogva/

Usage:
import pwman.util.generator as PwGen
minlen = 6
maxlen = 8
(word, hypenated_word) = PwGen.generate_password(minlen, maxlen)
"""
import random

class PasswordGenerationException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

def generate_password(minlen, maxlen, capitals = True, symbols = False, numerics = False):
    (password, hyphenated) = generate_password_shazel(minlen, maxlen)
    if (capitals):
        password = randomly_capitalize(password)
    if (symbols):
        password = leetify(password)
    elif (numerics):
        password = change_numerics(password)
    return (password, hyphenated)

def randomly_capitalize(password):
    newpassword = str()
    for l in password:
        if (random.random() >= 0.5):
            l = l.upper()
        newpassword = newpassword + l
    return newpassword

def leetify(password):
    newpassword = str()
    for l in password:
        if (random.random() >= 0.5):
            l = leetify_char(l)
        newpassword = newpassword + l
    return newpassword

def change_numerics(password):
    newpassword = str()
    for l in password:
        if (random.random() >= 0.5):
            l = change_numerics_char(l)
        newpassword = newpassword + l
    return newpassword
#
# Dictionary of mappings for leetness
#
leetlist = {
    'w': "\/\/", 'W': "\/\/", 'e': '3', 'E': '3', 't': '+', 'T': '7',
    'i': '1', 'I': '1', 'o': '0', 'O': '0', 'A': '4', 's': '5', 'S': '$',
    'g': '9', 'K': '|<', 'k': '|<', 'x': '><', 'X': '><', 'c': '<', 'C': '<',
    'v': '\/', 'V': '\/', 'n': '|\|', 'N': '|\|', 'm': '|\/|', 'M': '|\/|'
    }

def leetify_char(l):
    try:
        return leetlist[l]
    except KeyError:
        return l

numericlist = {
    'e': '3', 'E': '3', 'T': '7',
    'i': '1', 'I': '1', 'o': '0', 'O': '0', 'A': '4', 's': '5', 'S': '5',
    'g': '9', 'q': '9', 'l': '1'
    }

def change_numerics_char(l):
    try:
        return numericlist[l]
    except KeyError:
        return l
#
# Beyond this point layeth Steve Hazel's code
# Steven Hazel <sah@mosuki.com>
#
# I've added exceptions
#
MIN_LENGTH_PASSWORD = 6
MAX_LENGTH_PASSWORD = 14

grams = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
         'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
         'z', 'ch', 'gh', 'ph', 'rh', 'sh', 'th', 'wh', 'qu', 'ck')

vowel_grams = ('a', 'e', 'i', 'o', 'u', 'y')

occurrence_frequencies = {
    'a'  : 10,      'b'  :  8,      'c'  : 12,      'd'  : 12,
    'e'  : 12,      'f'  :  8,      'g'  :  8,      'h'  :  6,
    'i'  : 10,      'j'  :  8,      'k'  :  8,      'l'  :  6,
    'm'  :  6,      'n'  : 10,      'o'  : 10,      'p'  :  6,
    'r'  : 10,      's'  :  8,      't'  : 10,      'u'  :  6,
    'v'  :  8,      'w'  :  8,      'x'  :  1,      'y'  :  8,
    'z'  :  1,      'ch' :  1,      'gh' :  1,      'ph' :  1,
    'rh' :  1,      'sh' :  2,      'th' :  1,      'wh' :  1,
    'qu' :  1,      'ck' :  1}

numbers = []
for gram in grams:
    for i in range(occurrence_frequencies[gram]):
        numbers.append(gram)



vowel_numbers = []
for gram in vowel_grams:
    for i in range(occurrence_frequencies[gram]):
        vowel_numbers.append(gram)



#
# Bit flags
#

MAX_UNACCEPTABLE = 20

# gram rules:
NOT_BEGIN_SYLLABLE = 0x08
NO_FINAL_SPLIT = 0x04
VOWEL = 0x02
ALTERNATE_VOWEL = 0x01
NO_SPECIAL_RULE = 0x00

# digram rules:
BEGIN = 0x80
NOT_BEGIN = 0x40
BREAK = 0x20
PREFIX = 0x10
ILLEGAL_PAIR = 0x08
SUFFIX = 0x04
END = 0x02
NOT_END = 0x01
ANY_COMBINATION = 0x00

gram_rules = dict()
for gram in grams:
    gram_rules[ gram ] = NO_SPECIAL_RULE

for gram in vowel_grams:
    gram_rules[ gram ] = VOWEL


gram_rules['e'] |= NO_FINAL_SPLIT
gram_rules['y'] |= ALTERNATE_VOWEL

gram_rules['x']  = NOT_BEGIN_SYLLABLE
gram_rules['ck'] = NOT_BEGIN_SYLLABLE



digram_rules = dict()

###############################################################################
# BEGIN DIGRAM RULES
###############################################################################

digram_rules['a'] = dict()
digram_rules['a']['a'] = ILLEGAL_PAIR
digram_rules['a']['b'] = ANY_COMBINATION
digram_rules['a']['c'] = ANY_COMBINATION
digram_rules['a']['d'] = ANY_COMBINATION
digram_rules['a']['e'] = ILLEGAL_PAIR
digram_rules['a']['f'] = ANY_COMBINATION
digram_rules['a']['g'] = ANY_COMBINATION
digram_rules['a']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['a']['i'] = ANY_COMBINATION
digram_rules['a']['j'] = ANY_COMBINATION
digram_rules['a']['k'] = ANY_COMBINATION
digram_rules['a']['l'] = ANY_COMBINATION
digram_rules['a']['m'] = ANY_COMBINATION
digram_rules['a']['n'] = ANY_COMBINATION
digram_rules['a']['o'] = ILLEGAL_PAIR
digram_rules['a']['p'] = ANY_COMBINATION
digram_rules['a']['r'] = ANY_COMBINATION
digram_rules['a']['s'] = ANY_COMBINATION
digram_rules['a']['t'] = ANY_COMBINATION
digram_rules['a']['u'] = ANY_COMBINATION
digram_rules['a']['v'] = ANY_COMBINATION
digram_rules['a']['w'] = ANY_COMBINATION
digram_rules['a']['x'] = ANY_COMBINATION
digram_rules['a']['y'] = ANY_COMBINATION
digram_rules['a']['z'] = ANY_COMBINATION
digram_rules['a']['ch'] = ANY_COMBINATION
digram_rules['a']['gh'] = ILLEGAL_PAIR
digram_rules['a']['ph'] = ANY_COMBINATION
digram_rules['a']['rh'] = ILLEGAL_PAIR
digram_rules['a']['sh'] = ANY_COMBINATION
digram_rules['a']['th'] = ANY_COMBINATION
digram_rules['a']['wh'] = ILLEGAL_PAIR
digram_rules['a']['qu'] = BREAK | NOT_END
digram_rules['a']['ck'] = ANY_COMBINATION

digram_rules['b'] = dict()
digram_rules['b']['a'] = ANY_COMBINATION
digram_rules['b']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['d'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['e'] = ANY_COMBINATION
digram_rules['b']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['g'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['i'] = ANY_COMBINATION
digram_rules['b']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['k'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['l'] = BEGIN | SUFFIX | NOT_END
digram_rules['b']['m'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['n'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['o'] = ANY_COMBINATION
digram_rules['b']['p'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['r'] = BEGIN | END
digram_rules['b']['s'] = NOT_BEGIN
digram_rules['b']['t'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['u'] = ANY_COMBINATION
digram_rules['b']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['x'] = ILLEGAL_PAIR
digram_rules['b']['y'] = ANY_COMBINATION
digram_rules['b']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['ch'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['gh'] = ILLEGAL_PAIR
digram_rules['b']['ph'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['rh'] = ILLEGAL_PAIR
digram_rules['b']['sh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['th'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['wh'] = ILLEGAL_PAIR
digram_rules['b']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['b']['ck'] = ILLEGAL_PAIR

digram_rules['c'] = dict()
digram_rules['c']['a'] = ANY_COMBINATION
digram_rules['c']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['c']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['c']['d'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['c']['e'] = ANY_COMBINATION
digram_rules['c']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['c']['g'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['c']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['c']['i'] = ANY_COMBINATION
digram_rules['c']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['c']['k'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['c']['l'] = SUFFIX | NOT_END
digram_rules['c']['m'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['c']['n'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['c']['o'] = ANY_COMBINATION
digram_rules['c']['p'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['c']['r'] = NOT_END
digram_rules['c']['s'] = NOT_BEGIN | END
digram_rules['c']['t'] = NOT_BEGIN | PREFIX
digram_rules['c']['u'] = ANY_COMBINATION
digram_rules['c']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['c']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['c']['x'] = ILLEGAL_PAIR
digram_rules['c']['y'] = ANY_COMBINATION
digram_rules['c']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['c']['ch'] = ILLEGAL_PAIR
digram_rules['c']['gh'] = ILLEGAL_PAIR
digram_rules['c']['ph'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['c']['rh'] = ILLEGAL_PAIR
digram_rules['c']['sh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['c']['th'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['c']['wh'] = ILLEGAL_PAIR
digram_rules['c']['qu'] = NOT_BEGIN | SUFFIX | NOT_END
digram_rules['c']['ck'] = ILLEGAL_PAIR

digram_rules['d'] = dict()
digram_rules['d']['a'] = ANY_COMBINATION
digram_rules['d']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['d']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['d']['d'] = NOT_BEGIN
digram_rules['d']['e'] = ANY_COMBINATION
digram_rules['d']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['d']['g'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['d']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['d']['i'] = ANY_COMBINATION
digram_rules['d']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['d']['k'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['d']['l'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['d']['m'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['d']['n'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['d']['o'] = ANY_COMBINATION
digram_rules['d']['p'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['d']['r'] = BEGIN | NOT_END
digram_rules['d']['s'] = NOT_BEGIN | END
digram_rules['d']['t'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['d']['u'] = ANY_COMBINATION
digram_rules['d']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['d']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['d']['x'] = ILLEGAL_PAIR
digram_rules['d']['y'] = ANY_COMBINATION
digram_rules['d']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['d']['ch'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['d']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['d']['ph'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['d']['rh'] = ILLEGAL_PAIR
digram_rules['d']['sh'] = NOT_BEGIN | NOT_END
digram_rules['d']['th'] = NOT_BEGIN | PREFIX
digram_rules['d']['wh'] = ILLEGAL_PAIR
digram_rules['d']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['d']['ck'] = ILLEGAL_PAIR

digram_rules['e'] = dict()
digram_rules['e']['a'] = ANY_COMBINATION
digram_rules['e']['b'] = ANY_COMBINATION
digram_rules['e']['c'] = ANY_COMBINATION
digram_rules['e']['d'] = ANY_COMBINATION
digram_rules['e']['e'] = ANY_COMBINATION
digram_rules['e']['f'] = ANY_COMBINATION
digram_rules['e']['g'] = ANY_COMBINATION
digram_rules['e']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['e']['i'] = NOT_END
digram_rules['e']['j'] = ANY_COMBINATION
digram_rules['e']['k'] = ANY_COMBINATION
digram_rules['e']['l'] = ANY_COMBINATION
digram_rules['e']['m'] = ANY_COMBINATION
digram_rules['e']['n'] = ANY_COMBINATION
digram_rules['e']['o'] = BREAK
digram_rules['e']['p'] = ANY_COMBINATION
digram_rules['e']['r'] = ANY_COMBINATION
digram_rules['e']['s'] = ANY_COMBINATION
digram_rules['e']['t'] = ANY_COMBINATION
digram_rules['e']['u'] = ANY_COMBINATION
digram_rules['e']['v'] = ANY_COMBINATION
digram_rules['e']['w'] = ANY_COMBINATION
digram_rules['e']['x'] = ANY_COMBINATION
digram_rules['e']['y'] = ANY_COMBINATION
digram_rules['e']['z'] = ANY_COMBINATION
digram_rules['e']['ch'] = ANY_COMBINATION
digram_rules['e']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['e']['ph'] = ANY_COMBINATION
digram_rules['e']['rh'] = ILLEGAL_PAIR
digram_rules['e']['sh'] = ANY_COMBINATION
digram_rules['e']['th'] = ANY_COMBINATION
digram_rules['e']['wh'] = ILLEGAL_PAIR
digram_rules['e']['qu'] = BREAK | NOT_END
digram_rules['e']['ck'] = ANY_COMBINATION

digram_rules['f'] = dict()
digram_rules['f']['a'] = ANY_COMBINATION
digram_rules['f']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['f']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['f']['d'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['f']['e'] = ANY_COMBINATION
digram_rules['f']['f'] = NOT_BEGIN
digram_rules['f']['g'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['f']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['f']['i'] = ANY_COMBINATION
digram_rules['f']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['f']['k'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['f']['l'] = BEGIN | SUFFIX | NOT_END
digram_rules['f']['m'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['f']['n'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['f']['o'] = ANY_COMBINATION
digram_rules['f']['p'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['f']['r'] = BEGIN | NOT_END
digram_rules['f']['s'] = NOT_BEGIN
digram_rules['f']['t'] = NOT_BEGIN
digram_rules['f']['u'] = ANY_COMBINATION
digram_rules['f']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['f']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['f']['x'] = ILLEGAL_PAIR
digram_rules['f']['y'] = NOT_BEGIN
digram_rules['f']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['f']['ch'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['f']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['f']['ph'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['f']['rh'] = ILLEGAL_PAIR
digram_rules['f']['sh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['f']['th'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['f']['wh'] = ILLEGAL_PAIR
digram_rules['f']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['f']['ck'] = ILLEGAL_PAIR

digram_rules['g'] = dict()
digram_rules['g']['a'] = ANY_COMBINATION
digram_rules['g']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['g']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['g']['d'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['g']['e'] = ANY_COMBINATION
digram_rules['g']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['g']['g'] = NOT_BEGIN
digram_rules['g']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['g']['i'] = ANY_COMBINATION
digram_rules['g']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['g']['k'] = ILLEGAL_PAIR
digram_rules['g']['l'] = BEGIN | SUFFIX | NOT_END
digram_rules['g']['m'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['g']['n'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['g']['o'] = ANY_COMBINATION
digram_rules['g']['p'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['g']['r'] = BEGIN | NOT_END
digram_rules['g']['s'] = NOT_BEGIN | END
digram_rules['g']['t'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['g']['u'] = ANY_COMBINATION
digram_rules['g']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['g']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['g']['x'] = ILLEGAL_PAIR
digram_rules['g']['y'] = NOT_BEGIN
digram_rules['g']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['g']['ch'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['g']['gh'] = ILLEGAL_PAIR
digram_rules['g']['ph'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['g']['rh'] = ILLEGAL_PAIR
digram_rules['g']['sh'] = NOT_BEGIN
digram_rules['g']['th'] = NOT_BEGIN
digram_rules['g']['wh'] = ILLEGAL_PAIR
digram_rules['g']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['g']['ck'] = ILLEGAL_PAIR

digram_rules['h'] = dict()
digram_rules['h']['a'] = ANY_COMBINATION
digram_rules['h']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['d'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['e'] = ANY_COMBINATION
digram_rules['h']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['g'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['h'] = ILLEGAL_PAIR
digram_rules['h']['i'] = ANY_COMBINATION
digram_rules['h']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['k'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['l'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['m'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['n'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['o'] = ANY_COMBINATION
digram_rules['h']['p'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['r'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['s'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['t'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['u'] = ANY_COMBINATION
digram_rules['h']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['x'] = ILLEGAL_PAIR
digram_rules['h']['y'] = ANY_COMBINATION
digram_rules['h']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['ch'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['ph'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['rh'] = ILLEGAL_PAIR
digram_rules['h']['sh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['th'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['wh'] = ILLEGAL_PAIR
digram_rules['h']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['h']['ck'] = ILLEGAL_PAIR

digram_rules['i'] = dict()
digram_rules['i']['a'] = ANY_COMBINATION
digram_rules['i']['b'] = ANY_COMBINATION
digram_rules['i']['c'] = ANY_COMBINATION
digram_rules['i']['d'] = ANY_COMBINATION
digram_rules['i']['e'] = NOT_BEGIN
digram_rules['i']['f'] = ANY_COMBINATION
digram_rules['i']['g'] = ANY_COMBINATION
digram_rules['i']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['i']['i'] = ILLEGAL_PAIR
digram_rules['i']['j'] = ANY_COMBINATION
digram_rules['i']['k'] = ANY_COMBINATION
digram_rules['i']['l'] = ANY_COMBINATION
digram_rules['i']['m'] = ANY_COMBINATION
digram_rules['i']['n'] = ANY_COMBINATION
digram_rules['i']['o'] = BREAK
digram_rules['i']['p'] = ANY_COMBINATION
digram_rules['i']['r'] = ANY_COMBINATION
digram_rules['i']['s'] = ANY_COMBINATION
digram_rules['i']['t'] = ANY_COMBINATION
digram_rules['i']['u'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['i']['v'] = ANY_COMBINATION
digram_rules['i']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['i']['x'] = ANY_COMBINATION
digram_rules['i']['y'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['i']['z'] = ANY_COMBINATION
digram_rules['i']['ch'] = ANY_COMBINATION
digram_rules['i']['gh'] = NOT_BEGIN
digram_rules['i']['ph'] = ANY_COMBINATION
digram_rules['i']['rh'] = ILLEGAL_PAIR
digram_rules['i']['sh'] = ANY_COMBINATION
digram_rules['i']['th'] = ANY_COMBINATION
digram_rules['i']['wh'] = ILLEGAL_PAIR
digram_rules['i']['qu'] = BREAK | NOT_END
digram_rules['i']['ck'] = ANY_COMBINATION

digram_rules['j'] = dict()
digram_rules['j']['a'] = ANY_COMBINATION
digram_rules['j']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['d'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['e'] = ANY_COMBINATION
digram_rules['j']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['g'] = ILLEGAL_PAIR
digram_rules['j']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['i'] = ANY_COMBINATION
digram_rules['j']['j'] = ILLEGAL_PAIR
digram_rules['j']['k'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['l'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['m'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['n'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['o'] = ANY_COMBINATION
digram_rules['j']['p'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['r'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['s'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['t'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['u'] = ANY_COMBINATION
digram_rules['j']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['x'] = ILLEGAL_PAIR
digram_rules['j']['y'] = NOT_BEGIN
digram_rules['j']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['ch'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['ph'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['rh'] = ILLEGAL_PAIR
digram_rules['j']['sh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['th'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['wh'] = ILLEGAL_PAIR
digram_rules['j']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['j']['ck'] = ILLEGAL_PAIR

digram_rules['k'] = dict()
digram_rules['k']['a'] = ANY_COMBINATION
digram_rules['k']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['k']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['k']['d'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['k']['e'] = ANY_COMBINATION
digram_rules['k']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['k']['g'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['k']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['k']['i'] = ANY_COMBINATION
digram_rules['k']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['k']['k'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['k']['l'] = SUFFIX | NOT_END
digram_rules['k']['m'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['k']['n'] = BEGIN | SUFFIX | NOT_END
digram_rules['k']['o'] = ANY_COMBINATION
digram_rules['k']['p'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['k']['r'] = SUFFIX | NOT_END
digram_rules['k']['s'] = NOT_BEGIN | END
digram_rules['k']['t'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['k']['u'] = ANY_COMBINATION
digram_rules['k']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['k']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['k']['x'] = ILLEGAL_PAIR
digram_rules['k']['y'] = NOT_BEGIN
digram_rules['k']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['k']['ch'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['k']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['k']['ph'] = NOT_BEGIN | PREFIX
digram_rules['k']['rh'] = ILLEGAL_PAIR
digram_rules['k']['sh'] = NOT_BEGIN
digram_rules['k']['th'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['k']['wh'] = ILLEGAL_PAIR
digram_rules['k']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['k']['ck'] = ILLEGAL_PAIR

digram_rules['l'] = dict()
digram_rules['l']['a'] = ANY_COMBINATION
digram_rules['l']['b'] = NOT_BEGIN | PREFIX
digram_rules['l']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['l']['d'] = NOT_BEGIN | PREFIX
digram_rules['l']['e'] = ANY_COMBINATION
digram_rules['l']['f'] = NOT_BEGIN | PREFIX
digram_rules['l']['g'] = NOT_BEGIN | PREFIX
digram_rules['l']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['l']['i'] = ANY_COMBINATION
digram_rules['l']['j'] = NOT_BEGIN | PREFIX
digram_rules['l']['k'] = NOT_BEGIN | PREFIX
digram_rules['l']['l'] = NOT_BEGIN | PREFIX
digram_rules['l']['m'] = NOT_BEGIN | PREFIX
digram_rules['l']['n'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['l']['o'] = ANY_COMBINATION
digram_rules['l']['p'] = NOT_BEGIN | PREFIX
digram_rules['l']['r'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['l']['s'] = NOT_BEGIN
digram_rules['l']['t'] = NOT_BEGIN | PREFIX
digram_rules['l']['u'] = ANY_COMBINATION
digram_rules['l']['v'] = NOT_BEGIN | PREFIX
digram_rules['l']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['l']['x'] = ILLEGAL_PAIR
digram_rules['l']['y'] = ANY_COMBINATION
digram_rules['l']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['l']['ch'] = NOT_BEGIN | PREFIX
digram_rules['l']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['l']['ph'] = NOT_BEGIN | PREFIX
digram_rules['l']['rh'] = ILLEGAL_PAIR
digram_rules['l']['sh'] = NOT_BEGIN | PREFIX
digram_rules['l']['th'] = NOT_BEGIN | PREFIX
digram_rules['l']['wh'] = ILLEGAL_PAIR
digram_rules['l']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['l']['ck'] = ILLEGAL_PAIR

digram_rules['m'] = dict()
digram_rules['m']['a'] = ANY_COMBINATION
digram_rules['m']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['m']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['m']['d'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['m']['e'] = ANY_COMBINATION
digram_rules['m']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['m']['g'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['m']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['m']['i'] = ANY_COMBINATION
digram_rules['m']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['m']['k'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['m']['l'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['m']['m'] = NOT_BEGIN
digram_rules['m']['n'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['m']['o'] = ANY_COMBINATION
digram_rules['m']['p'] = NOT_BEGIN
digram_rules['m']['r'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['m']['s'] = NOT_BEGIN
digram_rules['m']['t'] = NOT_BEGIN
digram_rules['m']['u'] = ANY_COMBINATION
digram_rules['m']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['m']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['m']['x'] = ILLEGAL_PAIR
digram_rules['m']['y'] = ANY_COMBINATION
digram_rules['m']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['m']['ch'] = NOT_BEGIN | PREFIX
digram_rules['m']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['m']['ph'] = NOT_BEGIN
digram_rules['m']['rh'] = ILLEGAL_PAIR
digram_rules['m']['sh'] = NOT_BEGIN
digram_rules['m']['th'] = NOT_BEGIN
digram_rules['m']['wh'] = ILLEGAL_PAIR
digram_rules['m']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['m']['ck'] = ILLEGAL_PAIR

digram_rules['n'] = dict()
digram_rules['n']['a'] = ANY_COMBINATION
digram_rules['n']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['n']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['n']['d'] = NOT_BEGIN
digram_rules['n']['e'] = ANY_COMBINATION
digram_rules['n']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['n']['g'] = NOT_BEGIN | PREFIX
digram_rules['n']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['n']['i'] = ANY_COMBINATION
digram_rules['n']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['n']['k'] = NOT_BEGIN | PREFIX
digram_rules['n']['l'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['n']['m'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['n']['n'] = NOT_BEGIN
digram_rules['n']['o'] = ANY_COMBINATION
digram_rules['n']['p'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['n']['r'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['n']['s'] = NOT_BEGIN
digram_rules['n']['t'] = NOT_BEGIN
digram_rules['n']['u'] = ANY_COMBINATION
digram_rules['n']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['n']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['n']['x'] = ILLEGAL_PAIR
digram_rules['n']['y'] = NOT_BEGIN
digram_rules['n']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['n']['ch'] = NOT_BEGIN | PREFIX
digram_rules['n']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['n']['ph'] = NOT_BEGIN | PREFIX
digram_rules['n']['rh'] = ILLEGAL_PAIR
digram_rules['n']['sh'] = NOT_BEGIN
digram_rules['n']['th'] = NOT_BEGIN
digram_rules['n']['wh'] = ILLEGAL_PAIR
digram_rules['n']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['n']['ck'] = NOT_BEGIN | PREFIX

digram_rules['o'] = dict()
digram_rules['o']['a'] = ANY_COMBINATION
digram_rules['o']['b'] = ANY_COMBINATION
digram_rules['o']['c'] = ANY_COMBINATION
digram_rules['o']['d'] = ANY_COMBINATION
digram_rules['o']['e'] = ILLEGAL_PAIR
digram_rules['o']['f'] = ANY_COMBINATION
digram_rules['o']['g'] = ANY_COMBINATION
digram_rules['o']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['o']['i'] = ANY_COMBINATION
digram_rules['o']['j'] = ANY_COMBINATION
digram_rules['o']['k'] = ANY_COMBINATION
digram_rules['o']['l'] = ANY_COMBINATION
digram_rules['o']['m'] = ANY_COMBINATION
digram_rules['o']['n'] = ANY_COMBINATION
digram_rules['o']['o'] = ANY_COMBINATION
digram_rules['o']['p'] = ANY_COMBINATION
digram_rules['o']['r'] = ANY_COMBINATION
digram_rules['o']['s'] = ANY_COMBINATION
digram_rules['o']['t'] = ANY_COMBINATION
digram_rules['o']['u'] = ANY_COMBINATION
digram_rules['o']['v'] = ANY_COMBINATION
digram_rules['o']['w'] = ANY_COMBINATION
digram_rules['o']['x'] = ANY_COMBINATION
digram_rules['o']['y'] = ANY_COMBINATION
digram_rules['o']['z'] = ANY_COMBINATION
digram_rules['o']['ch'] = ANY_COMBINATION
digram_rules['o']['gh'] = NOT_BEGIN
digram_rules['o']['ph'] = ANY_COMBINATION
digram_rules['o']['rh'] = ILLEGAL_PAIR
digram_rules['o']['sh'] = ANY_COMBINATION
digram_rules['o']['th'] = ANY_COMBINATION
digram_rules['o']['wh'] = ILLEGAL_PAIR
digram_rules['o']['qu'] = BREAK | NOT_END
digram_rules['o']['ck'] = ANY_COMBINATION

digram_rules['p'] = dict()
digram_rules['p']['a'] = ANY_COMBINATION
digram_rules['p']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['p']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['p']['d'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['p']['e'] = ANY_COMBINATION
digram_rules['p']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['p']['g'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['p']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['p']['i'] = ANY_COMBINATION
digram_rules['p']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['p']['k'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['p']['l'] = SUFFIX | NOT_END
digram_rules['p']['m'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['p']['n'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['p']['o'] = ANY_COMBINATION
digram_rules['p']['p'] = NOT_BEGIN | PREFIX
digram_rules['p']['r'] = NOT_END
digram_rules['p']['s'] = NOT_BEGIN | END
digram_rules['p']['t'] = NOT_BEGIN | END
digram_rules['p']['u'] = NOT_BEGIN | END
digram_rules['p']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['p']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['p']['x'] = ILLEGAL_PAIR
digram_rules['p']['y'] = ANY_COMBINATION
digram_rules['p']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['p']['ch'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['p']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['p']['ph'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['p']['rh'] = ILLEGAL_PAIR
digram_rules['p']['sh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['p']['th'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['p']['wh'] = ILLEGAL_PAIR
digram_rules['p']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['p']['ck'] = ILLEGAL_PAIR

digram_rules['r'] = dict()
digram_rules['r']['a'] = ANY_COMBINATION
digram_rules['r']['b'] = NOT_BEGIN | PREFIX
digram_rules['r']['c'] = NOT_BEGIN | PREFIX
digram_rules['r']['d'] = NOT_BEGIN | PREFIX
digram_rules['r']['e'] = ANY_COMBINATION
digram_rules['r']['f'] = NOT_BEGIN | PREFIX
digram_rules['r']['g'] = NOT_BEGIN | PREFIX
digram_rules['r']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['r']['i'] = ANY_COMBINATION
digram_rules['r']['j'] = NOT_BEGIN | PREFIX
digram_rules['r']['k'] = NOT_BEGIN | PREFIX
digram_rules['r']['l'] = NOT_BEGIN | PREFIX
digram_rules['r']['m'] = NOT_BEGIN | PREFIX
digram_rules['r']['n'] = NOT_BEGIN | PREFIX
digram_rules['r']['o'] = ANY_COMBINATION
digram_rules['r']['p'] = NOT_BEGIN | PREFIX
digram_rules['r']['r'] = NOT_BEGIN | PREFIX
digram_rules['r']['s'] = NOT_BEGIN | PREFIX
digram_rules['r']['t'] = NOT_BEGIN | PREFIX
digram_rules['r']['u'] = ANY_COMBINATION
digram_rules['r']['v'] = NOT_BEGIN | PREFIX
digram_rules['r']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['r']['x'] = ILLEGAL_PAIR
digram_rules['r']['y'] = ANY_COMBINATION
digram_rules['r']['z'] = NOT_BEGIN | PREFIX
digram_rules['r']['ch'] = NOT_BEGIN | PREFIX
digram_rules['r']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['r']['ph'] = NOT_BEGIN | PREFIX
digram_rules['r']['rh'] = ILLEGAL_PAIR
digram_rules['r']['sh'] = NOT_BEGIN | PREFIX
digram_rules['r']['th'] = NOT_BEGIN | PREFIX
digram_rules['r']['wh'] = ILLEGAL_PAIR
digram_rules['r']['qu'] = NOT_BEGIN | PREFIX | NOT_END
digram_rules['r']['ck'] = NOT_BEGIN | PREFIX

digram_rules['s'] = dict()
digram_rules['s']['a'] = ANY_COMBINATION
digram_rules['s']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['s']['c'] = NOT_END
digram_rules['s']['d'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['s']['e'] = ANY_COMBINATION
digram_rules['s']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['s']['g'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['s']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['s']['i'] = ANY_COMBINATION
digram_rules['s']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['s']['k'] = ANY_COMBINATION
digram_rules['s']['l'] = BEGIN | SUFFIX | NOT_END
digram_rules['s']['m'] = SUFFIX | NOT_END
digram_rules['s']['n'] = PREFIX | SUFFIX | NOT_END
digram_rules['s']['o'] = ANY_COMBINATION
digram_rules['s']['p'] = ANY_COMBINATION
digram_rules['s']['r'] = NOT_BEGIN | NOT_END
digram_rules['s']['s'] = NOT_BEGIN | PREFIX
digram_rules['s']['t'] = ANY_COMBINATION
digram_rules['s']['u'] = ANY_COMBINATION
digram_rules['s']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['s']['w'] = BEGIN | SUFFIX | NOT_END
digram_rules['s']['x'] = ILLEGAL_PAIR
digram_rules['s']['y'] = ANY_COMBINATION
digram_rules['s']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['s']['ch'] = BEGIN | SUFFIX | NOT_END
digram_rules['s']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['s']['ph'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['s']['rh'] = ILLEGAL_PAIR
digram_rules['s']['sh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['s']['th'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['s']['wh'] = ILLEGAL_PAIR
digram_rules['s']['qu'] = SUFFIX | NOT_END
digram_rules['s']['ck'] = NOT_BEGIN

digram_rules['t'] = dict()
digram_rules['t']['a'] = ANY_COMBINATION
digram_rules['t']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['t']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['t']['d'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['t']['e'] = ANY_COMBINATION
digram_rules['t']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['t']['g'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['t']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['t']['i'] = ANY_COMBINATION
digram_rules['t']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['t']['k'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['t']['l'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['t']['m'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['t']['n'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['t']['o'] = ANY_COMBINATION
digram_rules['t']['p'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['t']['r'] = NOT_END
digram_rules['t']['s'] = NOT_BEGIN | END
digram_rules['t']['t'] = NOT_BEGIN | PREFIX
digram_rules['t']['u'] = ANY_COMBINATION
digram_rules['t']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['t']['w'] = BEGIN | SUFFIX | NOT_END
digram_rules['t']['x'] = ILLEGAL_PAIR
digram_rules['t']['y'] = ANY_COMBINATION
digram_rules['t']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['t']['ch'] = NOT_BEGIN
digram_rules['t']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['t']['ph'] = NOT_BEGIN | END
digram_rules['t']['rh'] = ILLEGAL_PAIR
digram_rules['t']['sh'] = NOT_BEGIN | END
digram_rules['t']['th'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['t']['wh'] = ILLEGAL_PAIR
digram_rules['t']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['t']['ck'] = ILLEGAL_PAIR

digram_rules['u'] = dict()
digram_rules['u']['a'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['u']['b'] = ANY_COMBINATION
digram_rules['u']['c'] = ANY_COMBINATION
digram_rules['u']['d'] = ANY_COMBINATION
digram_rules['u']['e'] = NOT_BEGIN
digram_rules['u']['f'] = ANY_COMBINATION
digram_rules['u']['g'] = ANY_COMBINATION
digram_rules['u']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['u']['i'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['u']['j'] = ANY_COMBINATION
digram_rules['u']['k'] = ANY_COMBINATION
digram_rules['u']['l'] = ANY_COMBINATION
digram_rules['u']['m'] = ANY_COMBINATION
digram_rules['u']['n'] = ANY_COMBINATION
digram_rules['u']['o'] = NOT_BEGIN | BREAK
digram_rules['u']['p'] = ANY_COMBINATION
digram_rules['u']['r'] = ANY_COMBINATION
digram_rules['u']['s'] = ANY_COMBINATION
digram_rules['u']['t'] = ANY_COMBINATION
digram_rules['u']['u'] = ILLEGAL_PAIR
digram_rules['u']['v'] = ANY_COMBINATION
digram_rules['u']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['u']['x'] = ANY_COMBINATION
digram_rules['u']['y'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['u']['z'] = ANY_COMBINATION
digram_rules['u']['ch'] = ANY_COMBINATION
digram_rules['u']['gh'] = NOT_BEGIN | PREFIX
digram_rules['u']['ph'] = ANY_COMBINATION
digram_rules['u']['rh'] = ILLEGAL_PAIR
digram_rules['u']['sh'] = ANY_COMBINATION
digram_rules['u']['th'] = ANY_COMBINATION
digram_rules['u']['wh'] = ILLEGAL_PAIR
digram_rules['u']['qu'] = BREAK | NOT_END
digram_rules['u']['ck'] = ANY_COMBINATION

digram_rules['v'] = dict()
digram_rules['v']['a'] = ANY_COMBINATION
digram_rules['v']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['d'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['e'] = ANY_COMBINATION
digram_rules['v']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['g'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['i'] = ANY_COMBINATION
digram_rules['v']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['k'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['l'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['m'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['n'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['o'] = ANY_COMBINATION
digram_rules['v']['p'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['r'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['s'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['t'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['u'] = ANY_COMBINATION
digram_rules['v']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['x'] = ILLEGAL_PAIR
digram_rules['v']['y'] = NOT_BEGIN
digram_rules['v']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['ch'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['ph'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['rh'] = ILLEGAL_PAIR
digram_rules['v']['sh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['th'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['wh'] = ILLEGAL_PAIR
digram_rules['v']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['v']['ck'] = ILLEGAL_PAIR

digram_rules['w'] = dict()
digram_rules['w']['a'] = ANY_COMBINATION
digram_rules['w']['b'] = NOT_BEGIN | PREFIX
digram_rules['w']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['w']['d'] = NOT_BEGIN | PREFIX | END
digram_rules['w']['e'] = ANY_COMBINATION
digram_rules['w']['f'] = NOT_BEGIN | PREFIX
digram_rules['w']['g'] = NOT_BEGIN | PREFIX | END
digram_rules['w']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['w']['i'] = ANY_COMBINATION
digram_rules['w']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['w']['k'] = NOT_BEGIN | PREFIX
digram_rules['w']['l'] = NOT_BEGIN | PREFIX | SUFFIX
digram_rules['w']['m'] = NOT_BEGIN | PREFIX
digram_rules['w']['n'] = NOT_BEGIN | PREFIX
digram_rules['w']['o'] = ANY_COMBINATION
digram_rules['w']['p'] = NOT_BEGIN | PREFIX
digram_rules['w']['r'] = BEGIN | SUFFIX | NOT_END
digram_rules['w']['s'] = NOT_BEGIN | PREFIX
digram_rules['w']['t'] = NOT_BEGIN | PREFIX
digram_rules['w']['u'] = ANY_COMBINATION
digram_rules['w']['v'] = NOT_BEGIN | PREFIX
digram_rules['w']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['w']['x'] = NOT_BEGIN | PREFIX
digram_rules['w']['y'] = ANY_COMBINATION
digram_rules['w']['z'] = NOT_BEGIN | PREFIX
digram_rules['w']['ch'] = NOT_BEGIN
digram_rules['w']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['w']['ph'] = NOT_BEGIN
digram_rules['w']['rh'] = ILLEGAL_PAIR
digram_rules['w']['sh'] = NOT_BEGIN
digram_rules['w']['th'] = NOT_BEGIN
digram_rules['w']['wh'] = ILLEGAL_PAIR
digram_rules['w']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['w']['ck'] = NOT_BEGIN

digram_rules['x'] = dict()
digram_rules['x']['a'] = NOT_BEGIN
digram_rules['x']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['d'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['e'] = NOT_BEGIN
digram_rules['x']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['g'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['i'] = NOT_BEGIN
digram_rules['x']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['k'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['l'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['m'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['n'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['o'] = NOT_BEGIN
digram_rules['x']['p'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['r'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['s'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['t'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['u'] = NOT_BEGIN
digram_rules['x']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['x'] = ILLEGAL_PAIR
digram_rules['x']['y'] = NOT_BEGIN
digram_rules['x']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['ch'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['ph'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['rh'] = ILLEGAL_PAIR
digram_rules['x']['sh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['th'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['wh'] = ILLEGAL_PAIR
digram_rules['x']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['x']['ck'] = ILLEGAL_PAIR

digram_rules['y'] = dict()
digram_rules['y']['a'] = ANY_COMBINATION
digram_rules['y']['b'] = NOT_BEGIN
digram_rules['y']['c'] = NOT_BEGIN | NOT_END
digram_rules['y']['d'] = NOT_BEGIN
digram_rules['y']['e'] = ANY_COMBINATION
digram_rules['y']['f'] = NOT_BEGIN | NOT_END
digram_rules['y']['g'] = NOT_BEGIN
digram_rules['y']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['y']['i'] = BEGIN | NOT_END
digram_rules['y']['j'] = NOT_BEGIN | NOT_END
digram_rules['y']['k'] = NOT_BEGIN
digram_rules['y']['l'] = NOT_BEGIN | NOT_END
digram_rules['y']['m'] = NOT_BEGIN
digram_rules['y']['n'] = NOT_BEGIN
digram_rules['y']['o'] = ANY_COMBINATION
digram_rules['y']['p'] = NOT_BEGIN
digram_rules['y']['r'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['y']['s'] = NOT_BEGIN
digram_rules['y']['t'] = NOT_BEGIN
digram_rules['y']['u'] = ANY_COMBINATION
digram_rules['y']['v'] = NOT_BEGIN | NOT_END
digram_rules['y']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['y']['x'] = NOT_BEGIN
digram_rules['y']['y'] = ILLEGAL_PAIR
digram_rules['y']['z'] = NOT_BEGIN
digram_rules['y']['ch'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['y']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['y']['ph'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['y']['rh'] = ILLEGAL_PAIR
digram_rules['y']['sh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['y']['th'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['y']['wh'] = ILLEGAL_PAIR
digram_rules['y']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['y']['ck'] = ILLEGAL_PAIR

digram_rules['z'] = dict()
digram_rules['z']['a'] = ANY_COMBINATION
digram_rules['z']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['d'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['e'] = ANY_COMBINATION
digram_rules['z']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['g'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['i'] = ANY_COMBINATION
digram_rules['z']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['k'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['l'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['m'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['n'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['o'] = ANY_COMBINATION
digram_rules['z']['p'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['r'] = NOT_BEGIN | NOT_END
digram_rules['z']['s'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['t'] = NOT_BEGIN
digram_rules['z']['u'] = ANY_COMBINATION
digram_rules['z']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['w'] = SUFFIX | NOT_END
digram_rules['z']['x'] = ILLEGAL_PAIR
digram_rules['z']['y'] = ANY_COMBINATION
digram_rules['z']['z'] = NOT_BEGIN
digram_rules['z']['ch'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['ph'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['rh'] = ILLEGAL_PAIR
digram_rules['z']['sh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['th'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['wh'] = ILLEGAL_PAIR
digram_rules['z']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['z']['ck'] = ILLEGAL_PAIR

digram_rules['ch'] = dict()
digram_rules['ch']['a'] = ANY_COMBINATION
digram_rules['ch']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['d'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['e'] = ANY_COMBINATION
digram_rules['ch']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['g'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['i'] = ANY_COMBINATION
digram_rules['ch']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['k'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['l'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['m'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['n'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['o'] = ANY_COMBINATION
digram_rules['ch']['p'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['r'] = NOT_END
digram_rules['ch']['s'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['t'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['u'] = ANY_COMBINATION
digram_rules['ch']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['w'] = NOT_BEGIN | NOT_END
digram_rules['ch']['x'] = ILLEGAL_PAIR
digram_rules['ch']['y'] = ANY_COMBINATION
digram_rules['ch']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['ch'] = ILLEGAL_PAIR
digram_rules['ch']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['ph'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['rh'] = ILLEGAL_PAIR
digram_rules['ch']['sh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['th'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['wh'] = ILLEGAL_PAIR
digram_rules['ch']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ch']['ck'] = ILLEGAL_PAIR

digram_rules['gh'] = dict()
digram_rules['gh']['a'] = ANY_COMBINATION
digram_rules['gh']['b'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['c'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['d'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['e'] = ANY_COMBINATION
digram_rules['gh']['f'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['g'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['h'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['i'] = BEGIN | NOT_END
digram_rules['gh']['j'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['k'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['l'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['m'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['n'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['o'] = BEGIN | NOT_END
digram_rules['gh']['p'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['gh']['r'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['s'] = NOT_BEGIN | PREFIX
digram_rules['gh']['t'] = NOT_BEGIN | PREFIX
digram_rules['gh']['u'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['v'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['w'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['x'] = ILLEGAL_PAIR
digram_rules['gh']['y'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['z'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['ch'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['gh'] = ILLEGAL_PAIR
digram_rules['gh']['ph'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['rh'] = ILLEGAL_PAIR
digram_rules['gh']['sh'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['th'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['wh'] = ILLEGAL_PAIR
digram_rules['gh']['qu'] = NOT_BEGIN | BREAK | PREFIX | NOT_END
digram_rules['gh']['ck'] = ILLEGAL_PAIR

digram_rules['ph'] = dict()
digram_rules['ph']['a'] = ANY_COMBINATION
digram_rules['ph']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ph']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ph']['d'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ph']['e'] = ANY_COMBINATION
digram_rules['ph']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ph']['g'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ph']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ph']['i'] = ANY_COMBINATION
digram_rules['ph']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ph']['k'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ph']['l'] = BEGIN | SUFFIX | NOT_END
digram_rules['ph']['m'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ph']['n'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ph']['o'] = ANY_COMBINATION
digram_rules['ph']['p'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ph']['r'] = NOT_END
digram_rules['ph']['s'] = NOT_BEGIN
digram_rules['ph']['t'] = NOT_BEGIN
digram_rules['ph']['u'] = ANY_COMBINATION
digram_rules['ph']['v'] = NOT_BEGIN | NOT_END
digram_rules['ph']['w'] = NOT_BEGIN | NOT_END
digram_rules['ph']['x'] = ILLEGAL_PAIR
digram_rules['ph']['y'] = NOT_BEGIN
digram_rules['ph']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ph']['ch'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ph']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ph']['ph'] = ILLEGAL_PAIR
digram_rules['ph']['rh'] = ILLEGAL_PAIR
digram_rules['ph']['sh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ph']['th'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ph']['wh'] = ILLEGAL_PAIR
digram_rules['ph']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ph']['ck'] = ILLEGAL_PAIR

digram_rules['rh'] = dict()
digram_rules['rh']['a'] = BEGIN | NOT_END
digram_rules['rh']['b'] = ILLEGAL_PAIR
digram_rules['rh']['c'] = ILLEGAL_PAIR
digram_rules['rh']['d'] = ILLEGAL_PAIR
digram_rules['rh']['e'] = BEGIN | NOT_END
digram_rules['rh']['f'] = ILLEGAL_PAIR
digram_rules['rh']['g'] = ILLEGAL_PAIR
digram_rules['rh']['h'] = ILLEGAL_PAIR
digram_rules['rh']['i'] = BEGIN | NOT_END
digram_rules['rh']['j'] = ILLEGAL_PAIR
digram_rules['rh']['k'] = ILLEGAL_PAIR
digram_rules['rh']['l'] = ILLEGAL_PAIR
digram_rules['rh']['m'] = ILLEGAL_PAIR
digram_rules['rh']['n'] = ILLEGAL_PAIR
digram_rules['rh']['o'] = BEGIN | NOT_END
digram_rules['rh']['p'] = ILLEGAL_PAIR
digram_rules['rh']['r'] = ILLEGAL_PAIR
digram_rules['rh']['s'] = ILLEGAL_PAIR
digram_rules['rh']['t'] = ILLEGAL_PAIR
digram_rules['rh']['u'] = BEGIN | NOT_END
digram_rules['rh']['v'] = ILLEGAL_PAIR
digram_rules['rh']['w'] = ILLEGAL_PAIR
digram_rules['rh']['x'] = ILLEGAL_PAIR
digram_rules['rh']['y'] = BEGIN | NOT_END
digram_rules['rh']['z'] = ILLEGAL_PAIR
digram_rules['rh']['ch'] = ILLEGAL_PAIR
digram_rules['rh']['gh'] = ILLEGAL_PAIR
digram_rules['rh']['ph'] = ILLEGAL_PAIR
digram_rules['rh']['rh'] = ILLEGAL_PAIR
digram_rules['rh']['sh'] = ILLEGAL_PAIR
digram_rules['rh']['th'] = ILLEGAL_PAIR
digram_rules['rh']['wh'] = ILLEGAL_PAIR
digram_rules['rh']['qu'] = ILLEGAL_PAIR
digram_rules['rh']['ck'] = ILLEGAL_PAIR

digram_rules['sh'] = dict()
digram_rules['sh']['a'] = ANY_COMBINATION
digram_rules['sh']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['sh']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['sh']['d'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['sh']['e'] = ANY_COMBINATION
digram_rules['sh']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['sh']['g'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['sh']['h'] = ILLEGAL_PAIR
digram_rules['sh']['i'] = ANY_COMBINATION
digram_rules['sh']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['sh']['k'] = NOT_BEGIN
digram_rules['sh']['l'] = BEGIN | SUFFIX | NOT_END
digram_rules['sh']['m'] = BEGIN | SUFFIX | NOT_END
digram_rules['sh']['n'] = BEGIN | SUFFIX | NOT_END
digram_rules['sh']['o'] = ANY_COMBINATION
digram_rules['sh']['p'] = NOT_BEGIN
digram_rules['sh']['r'] = BEGIN | SUFFIX | NOT_END
digram_rules['sh']['s'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['sh']['t'] = SUFFIX
digram_rules['sh']['u'] = ANY_COMBINATION
digram_rules['sh']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['sh']['w'] = SUFFIX | NOT_END
digram_rules['sh']['x'] = ILLEGAL_PAIR
digram_rules['sh']['y'] = ANY_COMBINATION
digram_rules['sh']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['sh']['ch'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['sh']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['sh']['ph'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['sh']['rh'] = ILLEGAL_PAIR
digram_rules['sh']['sh'] = ILLEGAL_PAIR
digram_rules['sh']['th'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['sh']['wh'] = ILLEGAL_PAIR
digram_rules['sh']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['sh']['ck'] = ILLEGAL_PAIR

digram_rules['th'] = dict()
digram_rules['th']['a'] = ANY_COMBINATION
digram_rules['th']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['d'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['e'] = ANY_COMBINATION
digram_rules['th']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['g'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['i'] = ANY_COMBINATION
digram_rules['th']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['k'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['l'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['m'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['n'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['o'] = ANY_COMBINATION
digram_rules['th']['p'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['r'] = NOT_END
digram_rules['th']['s'] = NOT_BEGIN | END
digram_rules['th']['t'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['u'] = ANY_COMBINATION
digram_rules['th']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['w'] = SUFFIX | NOT_END
digram_rules['th']['x'] = ILLEGAL_PAIR
digram_rules['th']['y'] = ANY_COMBINATION
digram_rules['th']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['ch'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['ph'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['rh'] = ILLEGAL_PAIR
digram_rules['th']['sh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['th'] = ILLEGAL_PAIR
digram_rules['th']['wh'] = ILLEGAL_PAIR
digram_rules['th']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['th']['ck'] = ILLEGAL_PAIR

digram_rules['wh'] = dict()
digram_rules['wh']['a'] = BEGIN | NOT_END
digram_rules['wh']['b'] = ILLEGAL_PAIR
digram_rules['wh']['c'] = ILLEGAL_PAIR
digram_rules['wh']['d'] = ILLEGAL_PAIR
digram_rules['wh']['e'] = BEGIN | NOT_END
digram_rules['wh']['f'] = ILLEGAL_PAIR
digram_rules['wh']['g'] = ILLEGAL_PAIR
digram_rules['wh']['h'] = ILLEGAL_PAIR
digram_rules['wh']['i'] = BEGIN | NOT_END
digram_rules['wh']['j'] = ILLEGAL_PAIR
digram_rules['wh']['k'] = ILLEGAL_PAIR
digram_rules['wh']['l'] = ILLEGAL_PAIR
digram_rules['wh']['m'] = ILLEGAL_PAIR
digram_rules['wh']['n'] = ILLEGAL_PAIR
digram_rules['wh']['o'] = BEGIN | NOT_END
digram_rules['wh']['p'] = ILLEGAL_PAIR
digram_rules['wh']['r'] = ILLEGAL_PAIR
digram_rules['wh']['s'] = ILLEGAL_PAIR
digram_rules['wh']['t'] = ILLEGAL_PAIR
digram_rules['wh']['u'] = ILLEGAL_PAIR
digram_rules['wh']['v'] = ILLEGAL_PAIR
digram_rules['wh']['w'] = ILLEGAL_PAIR
digram_rules['wh']['x'] = ILLEGAL_PAIR
digram_rules['wh']['y'] = BEGIN | NOT_END
digram_rules['wh']['z'] = ILLEGAL_PAIR
digram_rules['wh']['ch'] = ILLEGAL_PAIR
digram_rules['wh']['gh'] = ILLEGAL_PAIR
digram_rules['wh']['ph'] = ILLEGAL_PAIR
digram_rules['wh']['rh'] = ILLEGAL_PAIR
digram_rules['wh']['sh'] = ILLEGAL_PAIR
digram_rules['wh']['th'] = ILLEGAL_PAIR
digram_rules['wh']['wh'] = ILLEGAL_PAIR
digram_rules['wh']['qu'] = ILLEGAL_PAIR
digram_rules['wh']['ck'] = ILLEGAL_PAIR

digram_rules['qu'] = dict()
digram_rules['qu']['a'] = ANY_COMBINATION
digram_rules['qu']['b'] = ILLEGAL_PAIR
digram_rules['qu']['c'] = ILLEGAL_PAIR
digram_rules['qu']['d'] = ILLEGAL_PAIR
digram_rules['qu']['e'] = ANY_COMBINATION
digram_rules['qu']['f'] = ILLEGAL_PAIR
digram_rules['qu']['g'] = ILLEGAL_PAIR
digram_rules['qu']['h'] = ILLEGAL_PAIR
digram_rules['qu']['i'] = ANY_COMBINATION
digram_rules['qu']['j'] = ILLEGAL_PAIR
digram_rules['qu']['k'] = ILLEGAL_PAIR
digram_rules['qu']['l'] = ILLEGAL_PAIR
digram_rules['qu']['m'] = ILLEGAL_PAIR
digram_rules['qu']['n'] = ILLEGAL_PAIR
digram_rules['qu']['o'] = ANY_COMBINATION
digram_rules['qu']['p'] = ILLEGAL_PAIR
digram_rules['qu']['r'] = ILLEGAL_PAIR
digram_rules['qu']['s'] = ILLEGAL_PAIR
digram_rules['qu']['t'] = ILLEGAL_PAIR
digram_rules['qu']['u'] = ILLEGAL_PAIR
digram_rules['qu']['v'] = ILLEGAL_PAIR
digram_rules['qu']['w'] = ILLEGAL_PAIR
digram_rules['qu']['x'] = ILLEGAL_PAIR
digram_rules['qu']['y'] = ILLEGAL_PAIR
digram_rules['qu']['z'] = ILLEGAL_PAIR
digram_rules['qu']['ch'] = ILLEGAL_PAIR
digram_rules['qu']['gh'] = ILLEGAL_PAIR
digram_rules['qu']['ph'] = ILLEGAL_PAIR
digram_rules['qu']['rh'] = ILLEGAL_PAIR
digram_rules['qu']['sh'] = ILLEGAL_PAIR
digram_rules['qu']['th'] = ILLEGAL_PAIR
digram_rules['qu']['wh'] = ILLEGAL_PAIR
digram_rules['qu']['qu'] = ILLEGAL_PAIR
digram_rules['qu']['ck'] = ILLEGAL_PAIR

digram_rules['ck'] = dict()
digram_rules['ck']['a'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['b'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['c'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['d'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['e'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['f'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['g'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['h'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['i'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['j'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['k'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['l'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['m'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['n'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['o'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['p'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['r'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['s'] = NOT_BEGIN
digram_rules['ck']['t'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['u'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['v'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['w'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['x'] = ILLEGAL_PAIR
digram_rules['ck']['y'] = NOT_BEGIN
digram_rules['ck']['z'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['ch'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['gh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['ph'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['rh'] = ILLEGAL_PAIR
digram_rules['ck']['sh'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['th'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['wh'] = ILLEGAL_PAIR
digram_rules['ck']['qu'] = NOT_BEGIN | BREAK | NOT_END
digram_rules['ck']['ck'] = ILLEGAL_PAIR

###############################################################################
# END DIGRAM RULES
###############################################################################


def marked(flag, first_unit, second_unit):
    return digram_rules[first_unit][second_unit] & flag



# Generates a random word, as well as its hyphenated form.  The
# length of the returned word will be between minlen and maxlen.

def generate_password_shazel(minlen = MIN_LENGTH_PASSWORD,
                      maxlen = MAX_LENGTH_PASSWORD):

    if (minlen > maxlen):
        raise PasswordGenerationException("minlen minlen is greater than maxlen maxlen.")

    #
    # Check for zero length words.  This is technically not an error,
    # so we take the short cut and return empty words.
    #
    if (maxlen == 0):
        raise PasswordGenerationException("maxlen must be greater than 0.")


    word = ''
    for i in range(MAX_UNACCEPTABLE):
        results = _random_word(random.randint(minlen, maxlen))
        word = results[0]
        hyphenated_word = results[1]
        if (word != ''):
            break


    if (word == "" and (minlen > 0)):
        raise PasswordGenerationException("failed to generate an acceptable random password.")



    return (word, hyphenated_word)



# Selects a random element from an array.

def random_element(ar):

    try:
        keys = ar.keys()
    except:
        keys = range(len(ar))
    return ar[ keys[random.randint(0, len(keys) - 1)] ]




# This is the routine that returns a random word.  It collects random
# syllables until a predetermined word length is found.  If a retry
# threshold is reached, another word is tried.

def _random_word(pwlen):

    word = ''
    word_syllables = []

    max_retries = (4 * pwlen) + len(grams)

    tries = 0 # count of retries.


    # word_units used to be an array of indices into the 'rules' C-array.
    # now it's an array of actual units (grams).
    word_units = []


    saved_pair = []
    #
    # Find syllables until the entire word is constructed.
    #
    while(len(word) < pwlen):
        #
        # Get the syllable and find its length.
        #

        new_syllable, syllable_units, saved_pair = get_syllable(pwlen - len(word), saved_pair)

        #
        # Append the syllable units to the word units.
        #
        word_units = word_units + syllable_units

        #
        # If the word has been improperly formed, throw out
        # the syllable.  The checks performed here are those
        # that must be formed on a word basis.  The other
        # tests are performed entirely within the syllable.
        # Otherwise, append the syllable to the word.
        #
        if not (
            _improper_word(word_units)
             or
            (
                 word == ''
                 and
                 _have_initial_y(syllable_units)
            )
             or
             (
                 len(word + new_syllable) == pwlen
                 and
                 _have_final_split(syllable_units)
            )
           ):
            word = word + new_syllable
            word_syllables.append(new_syllable)


        #
        # Keep track of the times we have tried to get syllables.
        # If we have exceeded the threshold, start from scratch.
        #
        tries = tries + 1
        if (tries > max_retries):
            tries = 0
            word = ''
            word_syllables = []
            word_units = []



    return (word, '-'.join(word_syllables))




# Selects a gram (aka "unit").  This is the standard random unit
# generating routine for get_syllable().
#
# This routine attempts to return grams (units) with a distribution
# approaching that of the distribution of the units in English.
#
# The distribution of the units may be altered in this procedure
# without affecting the digram table or any other programs using the
# random_word function, as long as the set of grams (units) is kept
# consistent throughout this library.

def _random_unit(type):

    if (type & VOWEL):
        # Sometimes, we are asked to explicitly get a vowel (i.e., if
        # a digram pair expects one following it).  This is a
        # shortcut to do that and avoid looping with rejected
        # consonants.
        return random_element(vowel_numbers)
    else:
        # Get any letter according to the English distribution.
        return random_element(numbers)






# Check that the word does not contain illegal combinations
# that may span syllables.  Specifically, these are:
#
#  1. An illegal pair of units between syllables.
#  2. Three consecutive vowel units.
#  3. Three consecutive consonant units.
#
# The checks are made against units (1 or 2 letters), not against
# the individual letters, so three consecutive units can have
# the length of 6 at most.

def _improper_word(units):

    failure = 0

    for unit_count in range(len(units)):
        #
        # Check for ILLEGAL_PAIR.
        # This should have been caught for units within a syllable,
        # but in some cases it would have gone unnoticed for units between syllables
        # (e.g., when saved units in get_syllable() were not used).
        #
        if (unit_count > 0
            and digram_rules[units[unit_count-1]][units[unit_count]]
            & ILLEGAL_PAIR):
            return 1 # Failure!


        if (unit_count >= 2):


            #
            # Check for consecutive vowels or consonants.  Because the
            # initial y of a syllable is treated as a consonant rather
            # than as a vowel, we exclude y from the first vowel in the
            # vowel test.  The only problem comes when y ends a syllable
            # and two other vowels start the next, like fly-oint.  Since
            # such words are still pronounceable, we accept this.
            #

            #
            # Vowel check.
            #
            if ((
                (gram_rules[units[unit_count - 2]] & VOWEL)
                and
                not (gram_rules[units[unit_count - 2]] & ALTERNATE_VOWEL)
                and
                (gram_rules[units[unit_count - 1]] & VOWEL)
                and
                (gram_rules[units[unit_count    ]] & VOWEL)
                )
            or
            #
            # Consonant check.
            #
                (
                not (gram_rules[units[unit_count - 2]] & VOWEL)
                and
                not (gram_rules[units[unit_count - 1]] & VOWEL)
                and
                not (gram_rules[units[unit_count    ]] & VOWEL)
                )):
                return 1 # Failure!



    return 0 # success



# Treating y as a vowel is sometimes a problem.  Some words get
# formed that look irregular.  One special group is when y starts a
# word and is the only vowel in the first syllable.  The word ycl is
# one example.  We discard words like these.

def _have_initial_y(units):

    vowel_count = 0
    normal_vowel_count = 0

    for unit_count in range(len(units)):
        #
        # Count vowels.
        #
        if (gram_rules[units[unit_count]] & VOWEL):
            vowel_count = vowel_count + 1

            #
            # Count the vowels that are not:
            #  1. 'y'
            #  2. at the start of the word.
            #
            if (not (gram_rules[units[unit_count]] & ALTERNATE_VOWEL) or (unit_count > 0)):
                normal_vowel_count = normal_vowel_count + 1




    return (vowel_count <= 1) and (normal_vowel_count == 0)



# Besides the problem with the letter y, there is one with a silent e
# at the end of words, like face or nice.  We allow this silent e,
# but we do not allow it as the only vowel at the end of the word or
# syllables like ble will be generated.

def _have_final_split(units):

    vowel_count = 0

    #
    # Count all the vowels in the word.
    #
    for unit_count in range(len(units)):
        if (gram_rules[units[unit_count]] & VOWEL):
            vowel_count = vowel_count + 1



    #
    # Return TRUE iff the only vowel was e, found at the end if the word.
    #
    return ((vowel_count == 1)
             and (gram_rules[units[len(units) - 1]] & NO_FINAL_SPLIT))




def digram_is_invalid(first_unit, second_unit, current_unit_num,
                      length_left, units_in_syllable, vowel_count):

    #
    # Reject ILLEGAL_PAIRS of units.
    #
    if (marked(ILLEGAL_PAIR,
                first_unit,
                second_unit)):
        return 1


    #
    # Reject units that will be split between
    # syllables when the syllable has no vowels
    # in it.
    #
    if (marked(BREAK,
                first_unit,
                second_unit) and
        (vowel_count == 0)):
        return 1


    #
    # Reject a unit that will end a syllable when
    # no previous unit was a vowel and neither is
    # this one.
    #
    if (marked(END,
                first_unit,
                second_unit) and
        (vowel_count == 0) and
        not (gram_rules[second_unit] & VOWEL)):
        return 1


    if (current_unit_num == 1):
        #
        # Reject the unit if we are at the starting
        # digram of a syllable and it does not fit.
        #
        if (marked(NOT_BEGIN,
                    first_unit,
                    second_unit)):
            return 1

    else:
        # We are not at the start of a syllable.

        #
        # Do not allow syllables where the first letter is y
        # and the next pair can begin a syllable.  This may
        # lead to splits where y is left alone in a syllable.
        # Also, the combination does not sound to good even
        # if not split.
        #
        if ((current_unit_num == 2) and
            marked(BEGIN,
                    first_unit,
                    second_unit) and
            (gram_rules[units_in_syllable[0]] &
              ALTERNATE_VOWEL)):
            return 1


        #
        # If this is the last unit of a word, we
        # should reject any digram that cannot end a
        # syllable.
        #
        if (marked(NOT_END,
                    first_unit,
                    second_unit) and
            (length_left == 0)):
            return 1


        #
        # Reject the unit if the digram it forms wants
        # to break the syllable, but the resulting
        # digram that would end the syllable is not
        # allowed to end a syllable.
        #
        if (marked(BREAK,
                    first_unit,
                    second_unit) and
            (digram_rules[units_in_syllable[current_unit_num-2]]
              [first_unit] & NOT_END)):
            return 1



        #
        # Reject the unit if the digram it forms
        # expects a vowel preceding it and there
        # is none.
        #
        if (marked(PREFIX,
                    first_unit,
                    second_unit) and
            not (gram_rules[ units_in_syllable[current_unit_num-2] ] &
               VOWEL)):
            return 1



    return 0



# Generate next unit to password, making sure that it follows these rules:
#
# 1. Each syllable must contain exactly 1 or 2 consecutive vowels,
# where y is considered a vowel.
#
# 2. Syllable end is determined as follows:
#
#    a. Vowel is generated and previous unit is a consonant and
#       syllable already has a vowel.  In this case, new syllable is
#       started and already contains a vowel.
#    b. A pair determined to be a "break" pair is encountered.
#       In this case new syllable is started with second unit of this pair.
#    c. End of password is encountered.
#    d. "begin" pair is encountered legally.  New syllable is started
#    with this pair.
#    e. "end" pair is legally encountered.  New syllable has nothing yet.
#
# 3. Try generating another unit if:
#
#    a. third consecutive vowel and not y.
#    b. "break" pair generated but no vowel yet in current or
#       previous 2 units are "not_end".
#    c. "begin" pair generated but no vowel in syllable preceding begin pair,
#       or both previous 2 pairs are designated "not_end".
#    d. "end" pair generated but no vowel in current syllable or in
#       "end" pair.
#    e. "not_begin" pair generated but new syllable must begin
#       (because previous syllable ended as defined in 2 above).
#    f. vowel is generated and 2a is satisfied, but no syllable break
#       is possible in previous 3 pairs.
#    g. Second and third units of syllable must begin, and first unit
#       is "alternate_vowel".

def get_syllable(pwlen, saved_pair):

    #
    # This is needed if the saved_pair is tried and the syllable then
    # discarded because of the retry limit. Since the saved_pair is OK and
    # fits in nicely with the preceding syllable, we will always use it.
    #
    hold_saved_pair = saved_pair

    max_retries = (4 * pwlen) + len(grams)

    max_loops = 100
    num_loops = 0

    #
    # Loop until valid syllable is found.
    #
    while True:  # do: ftso python while: not PEP 315.
        #
        # Try for a new syllable.  Initialize all pertinent
        # syllable variables.
        #

        syllable = ""               # string, returned
        units_in_syllable = dict()  # array of units, returned

        # grams:
        unit = ''
        current_unit = 0
        last_unit = ''

        # numbers:
        vowel_count = 0
        tries = 0
        length_left = pwlen

        # flags:
        rule_broken = 0
        want_vowel = 0
        want_another_unit = 1

        saved_pair = hold_saved_pair

        #
        # This loop finds all the units for the syllable.
        #
        while True:  # do: ftso python while: not PEP 315.
            want_vowel = 0

            #
            # This loop continues until a valid unit is found for the
            # current position within the syllable.
            #
            while True:  # do: ftso python while: not PEP 315.
                rule_broken = 0
                #
                # If there are saved units from the previous
                # syllable, use them up first.
                #

                #
                # If there were two saved units, the first is
                # guaranteed (by checks performed in the previous
                # syllable) to be valid.  We ignore the checks and
                # place it in this syllable manually.
                #
                if (len(saved_pair) == 2):
                    syllable = saved_pair.pop()
                    units_in_syllable[0] = syllable
                    if (gram_rules[syllable] & VOWEL):
                        vowel_count = vowel_count + 1

                    current_unit = current_unit + 1
                    length_left -= len(syllable)


                if (len(saved_pair) > 0):
                    #
                    # The unit becomes the last unit checked in the
                    # previous syllable.
                    #
                    unit = saved_pair.pop()

                    #
                    # The saved units have been used.  Do not try to
                    # reuse them in this syllable (unless this
                    # particular syllable is rejected at which point
                    # we start to rebuild it with these same saved
                    # units).
                    #
                else:
                    #
                    # If we don't have to consider the saved units,
                    # we generate a random one.
                    #
                    if (want_vowel):
                        unit = _random_unit(VOWEL)
                    else:
                        unit = _random_unit(NO_SPECIAL_RULE)



                length_left -= len(unit)

                rule_broken = 0
                #
                # Prevent having a word longer than expected.
                #
                if (length_left < 0):
                    rule_broken = 1


                #
                # First unit of syllable.  This is special because
                # the digram tests require 2 units and we don't have
                # that yet.  Nevertheless, we can perform some
                # checks.
                #
                if (current_unit == 0):
                    #
                    # If this shouldn't begin a syllable, don't use it.
                    #
                    if (gram_rules[unit] & NOT_BEGIN_SYLLABLE):
                        rule_broken = 1
                    elif (length_left == 0):
                        #
                        # If this is the last unit of a word, we have
                        # a one unit syllable.  Since each syllable
                        # must have a vowel, we make sure the unit is
                        # a vowel.  Otherwise, we discard it.
                        #
                        if (gram_rules[unit] & VOWEL):
                            want_another_unit = 0
                        else:
                            rule_broken = 1


                else:

                    #
                    # We are not at the start of a syllable.
                    # Save the previous unit for later tests.
                    #
                    last_unit = units_in_syllable[current_unit-1]

                    #
                    # There are some digram tests that are
                    # universally true.  We test them out.
                    #

                    if (digram_is_invalid(last_unit,
                                               unit,
                                               current_unit,
                                               length_left,
                                               units_in_syllable,
                                               vowel_count)):
                        rule_broken = 1


                    #
                    # The following checks occur when the current
                    # unit is a vowel and we are not looking at a
                    # word ending with an e.
                    #
                    if (not rule_broken and
                        (gram_rules[unit] & VOWEL) and
                        ((length_left > 0)
                          or not (gram_rules[last_unit] & NO_FINAL_SPLIT))):
                        #
                        # Don't allow 3 consecutive vowels in a
                        # syllable.  Although some words formed
                        # like this are OK, like "beau", most are
                        # not.
                        #
                        if ((vowel_count > 1) and
                            (gram_rules[last_unit] & VOWEL)):
                            rule_broken = 1

                        #
                        # Check for the case of
                        # vowels-consonants-vowel, which is only
                        # legal if the last vowel is an e and we
                        # are the end of the word (which is not
                        # happening here due to a previous
                        # check).
                        #
                        elif ((vowel_count != 0) and not (gram_rules[last_unit] & VOWEL)):
                            #
                            # Try to save the vowel for the next
                            # syllable, but if the syllable left here
                            # is not proper (i.e., the resulting last
                            # digram cannot legally end it), just
                            # discard it and try for another.
                            #
                            if (digram_rules[ units_in_syllable[ current_unit - 2] ][last_unit] & NOT_END):
                                rule_broken = 1
                            else:
                                saved_pair = [unit]
                                want_another_unit = 0





                    #
                    # The unit picked and the digram formed are legal.
                    # We now determine if we can end the syllable.  It may,
                    # in some cases, mean the last unit(s) may be deferred to
                    # the next syllable.  We also check here to see if the
                    # digram formed expects a vowel to follow.
                    #
                    if (not rule_broken and want_another_unit):
                        if ((vowel_count != 0) and
                           (gram_rules[unit] & NO_FINAL_SPLIT) and
                           (length_left == 0) and
                           not (gram_rules[last_unit] & VOWEL)):

                            #
                            # This word ends in a silent e.
                            #

                            want_another_unit = 0
                        elif (marked(END,
                                     last_unit,
                                     unit)
                              or (length_left == 0)):

                            #
                            # This syllable ends either because the
                            # digram is a END pair or we would
                            # otherwise exceed the length of the
                            # word.
                            #

                            want_another_unit = 0
                        elif (vowel_count != 0 and length_left > 0):
                            #
                            # Since we have a vowel in the syllable
                            # already, if the digram calls for the end of the
                            # syllable, we can legally split it off. We also
                            # make sure that we are not at the end of the
                            # dangerous because that syllable may not have
                            # vowels, or it may not be a legal syllable end,
                            # and the retrying mechanism will loop infinitely
                            # with the same digram.
                            #

                            #
                            # If we must begin a syllable, we do so if
                            # the only vowel in THIS syllable is not part
                            # of the digram we are pushing to the next
                            # syllable.
                            #
                            if (marked(BEGIN,
                                        last_unit,
                                        unit) and
                                (current_unit > 1) and
                                not ((vowel_count == 1) and
                                   (gram_rules[last_unit] & VOWEL))):
                                saved_pair = [unit, last_unit]
                                want_another_unit = 0
                            elif (
                                marked(BREAK,
                                       last_unit,
                                       unit)):
                                saved_pair = [unit]
                                want_another_unit = 0

                        elif (
                            marked(SUFFIX,
                                   last_unit,
                                   unit)):
                            want_vowel = 1




                tries = tries + 1

                #
                # If this unit was illegal, redetermine the amount of
                # letters left to go in the word.
                #
                if (rule_broken):
                    length_left += len(unit)

                if not (rule_broken and tries <= max_retries):
                    break


            #
            # The unit fit OK.
            #
            if (tries <= max_retries):
                #
                # If the unit were a vowel, count it in.  However, if
                # the unit were a y and appear at the start of the
                # syllable, treat it like a constant (so that words
                # like "year" can appear and not conflict with the 3
                # consecutive vowel rule).
                #
                if (
                    (gram_rules[unit] & VOWEL)
                and
                    ((current_unit > 0) or not (gram_rules[unit] & ALTERNATE_VOWEL))
               ):
                    vowel_count = vowel_count + 1


                #
                # If a unit or units were to be saved, we must adjust
                # the syllable formed.  Otherwise, we append the
                # current unit to the syllable.
                #
                if (len(saved_pair) == 2):
                    syllable = syllable[0:
                                        len(syllable) -
                                        len(last_unit)]
                    length_left += len(last_unit)
                    current_unit -= 2

                elif (len(saved_pair) == 1):
                    current_unit = current_unit - 1

                else:
                    units_in_syllable[ current_unit ] = unit
                    syllable = syllable + unit

            else:
                #
                # Whoops!  Too many tries.  We set rule_broken so we
                # can loop in the outer loop and try another
                # syllable.
                #

                rule_broken = 1


            current_unit = current_unit + 1
            if not (tries <= max_retries and want_another_unit):
                break

        num_loops = num_loops + 1

        if not ((rule_broken or _illegal_placement(units_in_syllable))):
            break

    return (syllable, units_in_syllable.values(), saved_pair)




# goes through an individual syllable and checks for illegal
# combinations of letters that go beyond looking at digrams.
#
# We look at things like 3 consecutive vowels or consonants, or
# syllables with consonants between vowels (unless one of them is the
# final silent e).

def _illegal_placement(units):

    vowel_count = 0
    failure = 0

    for unit_count in range(len(units)):
        if (failure):
            break


        if (unit_count >= 1):
            #
            # Don't allow vowels to be split with consonants in a
            # single syllable.  If we find such a combination (except
            # for the silent e) we have to discard the syllable.
            #
            if (
                (
                    not (gram_rules[units[unit_count-1]] & VOWEL)
                 and
                     (gram_rules[units[unit_count  ]] & VOWEL)
                 and
                    not ((gram_rules[units[unit_count  ]] & NO_FINAL_SPLIT) and (unit_count == len(units)))
                 and
                     vowel_count
                )
             or

                 #
                 # Perform these checks when we have at least 3 units.
                 #
                 (
                     (unit_count >= 2)
                 and
                     (
                         #
                         # Disallow 3 consecutive consonants.
                         #
                         (
                             not (gram_rules[units[unit_count-2]] & VOWEL)
                         and
                             not (gram_rules[units[unit_count-1]] & VOWEL)
                         and
                             not (gram_rules[units[unit_count]] & VOWEL)
                        )
                     or

                         #
                         # Disallow 3 consecutive vowels, where the
                         # first is not a y.
                         #
                         (
                             (gram_rules[units[unit_count-2]] & VOWEL)
                         and
                             not ((gram_rules[units[0]] & ALTERNATE_VOWEL)
                                  and (unit_count == 2))
                         and
                             (gram_rules[units[unit_count-1]] & VOWEL)
                         and
                             (gram_rules[units[unit_count]] & VOWEL)
                        )
                    )
                )
            ):
                    failure = 1



        #
        # Count the vowels in the syllable.  As mentioned somewhere
        # above, exclude the initial y of a syllable.  Instead, treat
        # it as a consonant.
        #
        if (
            (gram_rules[units[unit_count]] & VOWEL)
        and
            not (
                (gram_rules[units[0]] & ALTERNATE_VOWEL)
            and
                (unit_count == 0)
            and
                (len(units) > 1)
           )
       ):
            vowel_count = vowel_count + 1



    return failure
