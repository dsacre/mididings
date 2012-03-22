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

import inspect
import functools
import itertools
import termios
import fcntl
import struct
import sys

import decorator


def flatten(arg):
    """
    Flatten nested sequences into a single list.
    """
    if issequence(arg):
        return list(itertools.chain(*(flatten(i) for i in arg)))
    else:
        return [arg]


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


class deprecated(object):
    def __init__(self, replacement=None):
        self.replacement = None

    def wrapper(self, f, *args, **kwargs):
        # XXX: avoid circular import
        from mididings.setup import get_config

        if not (hasattr(f, '_already_used') and f._already_used) and not get_config('silent'):
            if self.replacement:
                print("%s() is deprecated, please use %s() instead" % (f.__name__, self.replacement))
            else:
                print("%s() is deprecated" % f.__name__)
            f._already_used = True
        return f(*args, **kwargs)

    def __call__(self, f):
        f._deprecated = True
        return decorator.decorator(self.wrapper, f)


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
        if type(other) is not type(self):
            return NotImplemented
        return type(self)(self + other, '%s|%s' % (self.name, other.name))
    def __invert__(self):
        return type(self)(~int(self), ('~%s' if '|' not in self.name else '~(%s)') % self.name)


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
