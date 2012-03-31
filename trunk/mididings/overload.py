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
        varargs = argspec[1]
        ndef = len(argspec[3]) if argspec[3] else 0

        # names of the default arguments not overridden by positional arguments
        defargs = names[max(len(names)-ndef, n):]

        # check if the number of positional arguments fits, and if the remaining
        # parameters can be filled with keyword and default arguments.
        # alternatively, a suitable function with varargs is also accepted.
        if ((n <= len(names) and set(kwargs)|set(defargs) == set(names[n:])) or
            (n >= len(names) and varargs is not None)):
            # call f with all original arguments
            return f(*args, **kwargs)

    # no overload found, generate a comprehensible error message
    if name is None:
        name = inspect.stack()[1][3]
    candidates = ((name + inspect.formatargspec(*inspect.getargspec(f))) for f in funcs)

    message = "no suitable overload found for %s(), candidates are:\n%s" % (name, '\n'.join(candidates))
    raise TypeError(message)


# mapping of all overloaded function names to the corresponding _Overload object
_registry = {}


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


def mark(f, docstring=None):
    """
    Decorator that marks a function as being overloaded.
    """
    if isinstance(f, str):
        # called with docstring argument. return this function to be used as
        # the actual decorator
        return functools.partial(mark, docstring=f)

    k = (f.__module__, f.__name__)
    # create a new _Overload object if necessary, add function f to it
    if k not in _registry:
        _registry[k] = _Overload(f.__name__, docstring)
    _registry[k].add(f)

    @functools.wraps(f)
    def call_overload(*args, **kwargs):
        return _registry[k](*args, **kwargs)

    # use the overload's docstring if there is one
    if _registry[k].docstring is not None:
        call_overload.__doc__ = _registry[k].docstring

    # return a function that, instead of calling f, calls the _Overload object
    return call_overload
