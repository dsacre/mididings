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

import mididings.constants as _constants
import mididings.misc as _misc


class _Unit(object):
    """
    wrapper class for all units.
    """
    def __init__(self, unit):
        self.unit = unit

    # operator >> connects units in series
    def __rshift__(self, other):
        a = self if isinstance(self, Chain) else [self]
        b = other if isinstance(other, Chain) else [other]
        return Chain(a + b)

    def __rrshift__(self, other):
        a = other if isinstance(other, Chain) else [other]
        b = self if isinstance(self, Chain) else [self]
        return Chain(a + b)

    # operator // connects units in parallel
    def __floordiv__(self, other):
        return Fork([ self, other ])

    def __rfloordiv__(self, other):
        return Fork([ other, self ])

    def __repr__(self):
        name = self._name if hasattr(self, '_name') else self.__class__.__name__

        if hasattr(self, '_args') and hasattr(self, '_kwargs'):
            args = ', '.join(repr(a) for a in self._args)
            kwargs = ', '.join('%s=%s' % (k, repr(self._kwargs[k])) for k in self._kwargs)
            sep = ', ' if args and kwargs else ''
            return '%s(%s%s%s)' % (name, args, sep, kwargs)
        else:
            return name


def _unit_repr(f):
    """
    decorator that modifies the target function f to store its arguments in the returned unit.
    """
    def unit_wrapper(*args, **kwargs):
        u = f(*args, **kwargs)
        u._name = f.name if isinstance(f, _misc.Overload) else f.__name__
        u._args = args
        u._kwargs = kwargs
        return u
    return unit_wrapper


class Chain(_Unit, list):
    """
    units connected in series.
    """
    def __init__(self, units):
        list.__init__(self, units)

    def __repr__(self):
        return ' >> '.join(repr(u) for u in self)


class Fork(_Unit, list):
    """
    units connected in parallel.
    """
    def __init__(self, units, types=_constants.ANY, remove_duplicates=None):
        if types == _constants.ANY:
            list.__init__(self, units)
        else:
            # fork only certain types of events
            l = [ (Filter(types) >> x) for x in units ] + [ -Filter(types) ]
            list.__init__(self, l)
        self.remove_duplicates = remove_duplicates

    def __repr__(self):
        r = '[' + ', '.join(repr(u) for u in self) + ']'
        if self.remove_duplicates != None:
            return 'Fork(%s, remove_duplicates=%s)' % (r, repr(self.remove_duplicates))
        else:
            return r


class Split(_Unit, dict):
    """
    split events by type.
    """
    def __init__(self, d):
        dict.__init__(self, d)

    def __repr__(self):
        return '{' + ', '.join('%s: %s' % (repr(t), repr(self[t])) for t in self.keys()) + '}'


class _Selector(object):
    def __init__(self, filters):
        self.filters = filters

    # operator %
    def __mod__(self, other):
        return Fork([
            Chain(f for f in self.filters) >> other,
            Fork(-f for f in self.filters)
        ])

    # operator &
    def __and__(self, other):
        if not isinstance(other, _Filter):
            return NotImplemented
        return _Selector(self.filters + [other])


class _Filter(_Unit, _Selector):
    """
    wrapper class for all filters.
    """
    def __init__(self, unit):
        _Unit.__init__(self, unit)
        _Selector.__init__(self, [self])

    # operator ~ inverts the filter, but still acts on the same event types
    def __invert__(self):
        return _InvertedFilter(self, False)

    # operator - inverts the filter, ignoring event types
    def __neg__(self):
        return _InvertedFilter(self, True)


class _InvertedFilter(_Filter):
    def __init__(self, filt, ignore_types):
        self.filt = filt
        self.ignore_types = ignore_types
        _Filter.__init__(self, _mididings.InvertedFilter(filt.unit, ignore_types))

    def __repr__(self):
        prefix = '-' if self.ignore_types else '~'
        return '%s%s' % (prefix, repr(self.filt))


@_unit_repr
def Filter(*args):
    """
    filter by event type.
    """
    if len(args) > 1:
        types = reduce(lambda x,y: x|y, args)
    else:
        types = args[0]
    return _Filter(_mididings.TypeFilter(types))


@_unit_repr
def Pass(p=True):
    return _Unit(_mididings.Pass(p))


@_unit_repr
def Discard():
    return _Unit(_mididings.Pass(False))
