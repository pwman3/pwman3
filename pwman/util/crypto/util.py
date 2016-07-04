"""
Copyright (c) 2014  Philippe Teuwen <phil@teuwen.org>


Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
IN THE SOFTWARE.

This code is taken from https://github.com/doegox/python-cryptoplus/
"""

def number2string(i):
    """Convert a number to a string

    Input: long or integer
    Output: string (big-endian)
    """
    s=hex(i)[2:].rstrip('L')
    if len(s) % 2:
        s = '0' + s
    return s.decode('hex')

def number2string_N(i, N):
    """Convert a number to a string of fixed size

    i: long or integer
    N: length of string
    Output: string (big-endian)
    """
    s = '%0*x' % (N*2, i)
    return s.decode('hex')

def string2number(i):
    """ Convert a string to a number

    Input: string (big-endian)
    Output: long or integer
    """
    return int(i.encode('hex'),16)

def xorstring(a,b):
    """XOR two strings of same length

    For more complex cases, see CryptoPlus.Cipher.XOR"""
    assert len(a) == len(b)
    return number2string_N(string2number(a)^string2number(b), len(a))

class Counter(str):
    #found here: http://www.lag.net/pipermail/paramiko/2008-February.txt
    """Necessary for CTR chaining mode

    Initializing a counter object (ctr = Counter('xxx'), gives a value to the counter object.
    Everytime the object is called ( ctr() ) it returns the current value and increments it by 1.
    Input/output is a raw string.

    Counter value is big endian"""
    def __init__(self, initial_ctr):
        if not isinstance(initial_ctr, str):
            raise TypeError("nonce must be str")
        self.c = int(initial_ctr.encode('hex'), 16)
    def __call__(self):
        # This might be slow, but it works as a demonstration
        ctr = ("%032x" % (self.c,)).decode('hex')
        self.c += 1
        return ctr


