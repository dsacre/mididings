# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2012  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import _mididings

import inspect
import functools
import termios
import fcntl
import struct
import sys
from decorator import decorator


def flatten(seq):
    """
    Flatten nested sequences into a single list.
    """
    r = []
    for i in seq:
        if issequence(i):
            r.extend(flatten(i))
        else:
            r.append(i)
    return r


def issequence(seq, accept_string=False):
    """
    Return whether seq is of a sequence type. By default, strings are not
    considered sequences.
    """
    if not accept_string and isinstance(seq, str):
        return False

    try:
        iter(seq)
        return True
    except TypeError:
        return False

def issequenceof(seq, t):
    """
    Return whether seq is a sequence with elements of type t.
    """
    return issequence(seq) and all(isinstance(v, t) for v in seq)


def deprecated(replacement=None):
    """
    Mark a function as deprecated, optionally suggesting a replacement.
    """
    # XXX: avoid circular import
    from mididings.setup import get_config

    def deprecated_wrapper(f, *args, **kwargs):
        if f not in deprecated._already_used and not get_config('silent'):
            if replacement:
                print("%s() is deprecated, please use %s() instead" % (f.__name__, replacement))
            else:
                print("%s() is deprecated" % f.__name__)
            deprecated._already_used.append(f)
        return f(*args, **kwargs)
    deprecated_wrapper._deprecated = True
    return decorator(deprecated_wrapper)

deprecated._already_used = []



#def rename_ctor(f):
#    assert f.__name__ == '__init__'
#
#    @functools.wraps(f)
#    def wrapper(self, *args, **kwargs):
#        try:
#            f(self, *args, **kwargs)
#        except TypeError:
#            _, ex, _ = sys.exc_info()
#            ex.args = (ex.args[0].replace('__init__', type(self).__name__),)
#            raise
#
#    return wrapper


class NamedFlag(int):
    """
    An integer type where each value has a name attached to it.
    """
    def __new__(cls, value, name):
        return int.__new__(cls, value)
    def __init__(self, value, name):
        self.name = name
    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name


class NamedBitMask(NamedFlag):
    """
    Like NamedFlag, but bit operations | and ~ are also reflected in the
    resulting value's string representation.
    """
    def __or__(self, other):
        return NamedBitMask(self + other, '%s|%s' % (self.name, other.name))
    def __invert__(self):
        return NamedBitMask(~int(self), ('~%s' if '|' not in self.name else '~(%s)') % self.name)


def prune_globals(g):
    return [n for (n, m) in g.items()
        if not inspect.ismodule(m)
        and not n.startswith('_')
        #and not (hasattr(m, '_deprecated'))
    ]


def string_to_hex(s):
    return ' '.join(hex(ord(c))[2:].zfill(2) for c in s)


def get_terminal_size():
    """
    Return the height and width of the terminal.
    """
    try:
        s = struct.pack("HHHH", 0, 0, 0, 0)
        fd = sys.stdout.fileno()
        x = fcntl.ioctl(fd, termios.TIOCGWINSZ, s)
        t = struct.unpack("HHHH", x)
        return t[0], t[1]
    except Exception:
        return 25, 80
