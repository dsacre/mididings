# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2010  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import _mididings
from setup import get_config as _get_config

import inspect as _inspect
import itertools as _itertools


def flatten(seq):
    r = []
    for i in seq:
        if isinstance(i, (tuple, list)):
            r.extend(flatten(i))
        else:
            r.append(i)
    return r


def issequence(seq, accept_string=False):
    if not accept_string and isinstance(seq, str):
        return False
    try:
        iter(seq)
        return True
    except TypeError:
        return False


def seq_to_string(seq):
    if issequence(seq):
        return ''.join(map(chr, seq))
    else:
        return seq


def _fill_vector(vec, seq):
    for i in seq:
        vec.push_back(i)
    return vec

def make_int_vector(seq):
    return _fill_vector(_mididings.int_vector(), seq)

def make_float_vector(seq):
    return _fill_vector(_mididings.float_vector(), seq)

def make_string_vector(seq):
    return _fill_vector(_mididings.string_vector(), seq)


def call_overload(name, args, kwargs, funcs):
    """
    searches funcs for a function with parameters such that args and kwargs
    can be applied, and calls it if a suitable function is found.
    """
    for f in funcs:
        n = len(args)
        # get argument names and the number of default arguments of f
        argspec = _inspect.getargspec(f)
        names = argspec[0]
        ndef = len(argspec[3]) if argspec[3] else 0

        # names of the default arguments not overridden by positional arguments
        defargs = names[max(len(names)-ndef, n):]

        # check if the number of positional arguments fits, and if the remaining
        # parameters can be filled with keyword and default arguments
        if n <= len(names) and set(kwargs)|set(defargs) == set(names[n:]):
            # call f with all original arguments
            return f(*args, **kwargs)

    candidates = []
    for f in funcs:
        argspec = _inspect.getargspec(f)
        names = argspec[0]
        defvals = argspec[3] if argspec[3] else ()

        argstr = ', '.join(_itertools.chain(
            names[:len(names)-len(defvals)],
            ('%s=%s' % a for a in _itertools.izip(names[-len(defvals):], defvals)),
        ))
        candidates.append('%s(%s)' % (name, argstr))

    raise TypeError("no suitable overload found for %s(), candidates are:\n%s" % (name, '\n'.join(candidates)))


class deprecated:
    """
    marks a function as deprecated, optionally suggesting a replacement.
    """
    already_used = []

    def __init__(self, replacement=None):
        self.replacement = replacement

    def __call__(self, f):
        def deprecated_wrapper(*args, **kwargs):
            if _get_config('verbose') and f not in deprecated.already_used:
                if self.replacement:
                    print "%s() is deprecated, please use %s() instead" % (f.func_name, self.replacement)
                else:
                    print "%s() is deprecated" % f.func_name
                deprecated.already_used.append(f)
            return f(*args, **kwargs)
        return deprecated_wrapper


class NamedFlag(int):
    def __new__(cls, value, name):
        return int.__new__(cls, value)
    def __init__(self, value, name):
        self.name = name
    def __repr__(self):
        return self.name


class NamedBitMask(NamedFlag):
    def __or__(self, other):
        return NamedBitMask(self + other, '%s|%s' % (self.name, other.name))
    def __invert__(self):
        return NamedBitMask(~int(self), ('~%s' if '|' not in self.name else '~(%s)') % self.name)


def prune_globals(g):
    return [n for (n, m) in g.items() if not _inspect.ismodule(m) and not n.startswith('_')]
