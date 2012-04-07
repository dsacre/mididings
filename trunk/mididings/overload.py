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

from mididings import misc

import inspect
import functools


def call(args, kwargs, funcs, name=None):
    """
    Search funcs for a function with parameters such that args and kwargs can
    be applied, and call the first suitable function that is found.
    """
    for f in funcs:
        n = len(args)

        # get argument names and the number of default arguments of f
        argspec = misc.getargspec(f)
        names = argspec[0]
        varargs = argspec[1]
        ndef = len(argspec[3]) if argspec[3] else 0

        # names of the default arguments not overridden by positional arguments
        npos = max(len(names) - ndef, n)
        defargs = names[npos:]

        # check if the number of positional arguments fits, and if the remaining
        # parameters can be filled with keyword and default arguments.
        # alternatively, a suitable function with varargs is also accepted.
        if ((n <= len(names) and set(kwargs) | set(defargs) == set(names[n:])) or
            (n >= len(names) and varargs is not None)):
            # call f with all original arguments
            return f(*args, **kwargs)

    # no overload found, generate a comprehensible error message
    if name is None:
        name = inspect.stack()[1][3]

    # format arg spec for each candidate
    formatargspec = lambda f: inspect.formatargspec(*misc.getargspec(f))
    candidates = ('    %s%s' % (name, formatargspec(f)) for f in funcs)

    # formatargspec() doesn't seem to care that the first argument mixes
    # asterisks and argument names
    argx = ['*'] * len(args)
    kwargx = ['*'] * len(kwargs)
    formatvalue = lambda v: '=%s' % v
    args_used = inspect.formatargspec(argx + list(kwargs.keys()), defaults=kwargx, formatvalue=formatvalue)

    message = "no suitable overload found for %s%s, candidates are:\n%s" % (name, args_used, '\n'.join(candidates))
    raise TypeError(message)



class _Overload(object):
    """
    Wrapper class for an arbitrary number of overloads.
    """
    def __init__(self, name, docstring):
        self.name = name
        self.docstring = docstring
        self.funcs = []

    def add(self, f):
        self.funcs.append(f)

    def __call__(self, *args, **kwargs):
        return call(args, kwargs, self.funcs, self.name)


# mapping of all overloaded function names to the corresponding _Overload object
_registry = {}


def _register_overload(f, docstring):
    k = (f.__module__, f.__name__)
    # create a new _Overload object if necessary, add function f to it
    if k not in _registry:
        _registry[k] = _Overload(f.__name__, docstring)
    _registry[k].add(f)
    return k


def mark(f, docstring=None):
    """
    Decorator that marks a function as being overloaded.
    """
    if isinstance(f, str):
        # called with docstring argument. return this function to be used as
        # the actual decorator
        return functools.partial(mark, docstring=f)

    k = _register_overload(f, docstring)

    @functools.wraps(f)
    def call_overload(*args, **kwargs):
        return _registry[k](*args, **kwargs)

    # use the overload's docstring if there is one
    if _registry[k].docstring is not None:
        call_overload.__doc__ = _registry[k].docstring

    # return a function that, instead of calling f, calls the _Overload object
    return call_overload


class partial(object):
    """
    Decorator that adds functools.partial objects as overloads for the given
    function.
    """
    def __init__(self, *partial_args):
        self.partial_args = partial_args

    def __call__(self, f):
        k = _register_overload(f, None)

        # register partial objects as overloads
        for part in self.partial_args:
            _registry[k].add(functools.partial(f, *part))

        @functools.wraps(f)
        def call_overload(*args, **kwargs):
            return _registry[k](*args, **kwargs)

        return call_overload
