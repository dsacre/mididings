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

from mididings import overload
from mididings import arguments
from mididings import misc

import inspect
import sys

import decorator


@decorator.decorator
def store(f, *args, **kwargs):
    """
    Decorator that modifies the function f to store its own arguments in the
    unit it returns.
    """
    unit = f(*args, **kwargs)

    # store the unit's name, the function object, and the value of each argument
    unit._name = f.name if isinstance(f, overload._Overload) else f.__name__
    unit._function = f
    unit._args = args

    return unit


def accept(*constraints, **kwargs):
    """
    @arguments.accept() and @unitrepr.store composed into a single decorator
    for convenience.
    """
    def composed(f):
        return arguments.accept(*constraints, **kwargs) (store(f))
    return composed



def unit_to_string(unit):
    # can't do anything for units that didn't go through @store (or @accept)
    assert hasattr(unit, '_name')

    argnames = misc.getargspec(unit._function)[0]

    if sys.version_info >= (2, 6):
        args = [
            misc.bytestring(a) if isinstance(a, bytearray) else a
            for a in unit._args
        ]
    else:
        args = unit._args

    # (ab)use inspect module to format the arguments used
    formatted = inspect.formatargspec(args=argnames, defaults=args)
    return unit._name + formatted


def chain_to_string(chain):
    return ' >> '.join(repr(u) for u in chain)


def fork_to_string(fork):
    if fork.remove_duplicates is not None:
        args = ('units', 'remove_duplicates')
        defaults = (list(fork), fork.remove_duplicates)
        formatted = inspect.formatargspec(args, defaults=defaults)
        return 'Fork' + formatted
    else:
        return list.__repr__(fork)


def split_to_string(split):
    return dict.__repr__(split)


def inverted_filter_to_string(invfilt):
    prefix = '-' if invfilt.negate else '~'
    return '%s%r' % (prefix, invfilt.filt)
