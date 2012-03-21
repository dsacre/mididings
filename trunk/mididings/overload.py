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
import itertools
import functools


def call(args, kwargs, funcs, name=None):
    """
    Search funcs for a function with parameters such that args and kwargs can
    be applied, and call the first suitable function that is found.
    """
    for f in funcs:
        n = len(args)
        # get argument names and the number of default arguments of f
        argspec = inspect.getargspec(f)
        names = argspec[0]
        ndef = len(argspec[3]) if argspec[3] else 0

        # names of the default arguments not overridden by positional arguments
        defargs = names[max(len(names)-ndef, n):]

        # check if the number of positional arguments fits, and if the remaining
        # parameters can be filled with keyword and default arguments
        if n <= len(names) and set(kwargs)|set(defargs) == set(names[n:]):
            # call f with all original arguments
            return f(*args, **kwargs)

    # no overload found, generate a comprehensible error message
    if not name:
        name = inspect.stack()[1][3]
    candidates = []
    for f in funcs:
        argspec = inspect.getargspec(f)
        names = argspec[0]
        defvals = argspec[3] if argspec[3] else ()

        argstr = ', '.join(itertools.chain(
            names[:len(names)-len(defvals)],
            ('%s=%s' % a for a in zip(names[-len(defvals):], defvals)),
        ))
        candidates.append('%s(%s)' % (name, argstr))

    raise TypeError("no suitable overload found for %s(), candidates are:\n%s" % (name, '\n'.join(candidates)))


# mapping of all overloaded function names to the corresponding Overload object
_registry = {}


class Overload(object):
    """
    Wrapper class for an arbitrary number of overloads.
    """
    def __init__(self, name):
        self.name = name
        self.funcs = []
    def add(self, f):
        self.funcs.append(f)
    def __call__(self, *args, **kwargs):
        return call(args, kwargs, self.funcs, self.name)


def mark(f):
    """
    Decorator that marks a function as being overloaded.
    """
    k = (f.__module__, f.__name__)
    # create a new Overload object if necessary, add function f to it
    if k not in _registry:
        _registry[k] = Overload(f.__name__)
    _registry[k].add(f)

    # return a function that, instead of calling f, calls the Overload object
    @functools.wraps(f)
    def overload_function(*args, **kwargs):
        return _registry[k](*args, **kwargs)

    return overload_function
