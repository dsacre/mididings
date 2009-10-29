# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2009  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import _mididings

import inspect as _inspect


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
    except:
        return False


def make_string_vector(seq):
    vec = _mididings.string_vector()
    for i in seq:
        vec.push_back(i)
    return vec


def make_int_vector(seq):
    vec = _mididings.int_vector()
    for i in seq:
        vec.push_back(i)
    return vec


def call_overload(name, args, kwargs, funcs):
    """
    searches funcs for a function with parameters such that args and kwargs
    can be applied, and calls it if a suitable function is found.
    """
    for f in funcs:
        argspec = _inspect.getargspec(f)[0]
        n = len(args)
        # check if the number of positional arguments fits, and if
        # the remaining parameters can be filled with keyword arguments
        if n <= len(argspec) and set(kwargs) == set(argspec[n:]):
            # make a dict of all positional arguments
            kw = dict(zip(argspec, args))
            # add the keyword arguments
            kw.update(kwargs)
            return f(**kw)
    raise TypeError("no suitable overload for %s() found" % name)
