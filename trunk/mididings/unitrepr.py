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

import mididings.overload as overload
import mididings.arguments as arguments

import inspect
import decorator


@decorator.decorator
def store(f, *args, **kwargs):
    """
    Decorator that modifies the function f to store its own arguments in the
    unit it returns.
    """
    unit = f(*args, **kwargs)
    unit._name = f.name if isinstance(f, overload._Overload) else f.__name__
#    unit._args = args
    arg_names = inspect.getargspec(f)[0]
    unit._args = zip(arg_names, args)
    unit._kwargs = kwargs
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
    if hasattr(unit, '_name'):
        # anything that went through @store (or @accept) will have _name, _args
        # and _kwargs attributes
        name = unit._name
#        args = ', '.join(repr(a) for a in unit._args)
        args = ', '.join('%s=%r' % a for a in unit._args)
        kwargs = ', '.join('%s=%r' % (k, unit._kwargs[k]) for k in unit._kwargs)
        sep = ', ' if args and kwargs else ''
        return '%s(%s%s%s)' % (name, args, sep, kwargs)
    else:
        # is this the best we can do?
        return unit.__class__.__name__


def chain_to_string(chain):
    return ' >> '.join(repr(u) for u in chain)


def fork_to_string(fork):
    r = '[' + ', '.join(repr(u) for u in fork) + ']'
    if fork.remove_duplicates != None:
        return 'Fork(%s, remove_duplicates=%r)' % (r, fork.remove_duplicates)
    else:
        return r


def split_to_string(split):
    return '{' + ', '.join('%r: %r' % (t, split[t]) for t in split.keys()) + '}'


def inverted_filter_to_string(invfilt):
    prefix = '-' if invfilt.negate else '~'
    return '%s%r' % (prefix, invfilt.filt)
