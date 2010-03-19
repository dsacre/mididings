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

import mididings.misc as _misc


class _Unit(object):
    """
    wrapper class for all units.
    """
    def __init__(self, unit):
        self.unit = unit

    def __rshift__(self, other):
        """operator >>: connect units in series"""
        if not isinstance(other, _UNIT_TYPES):
            return NotImplemented
        return _join_units(Chain, self, other)

    def __rrshift__(self, other):
        """operator >>: connect units in series"""
        if not isinstance(other, _UNIT_TYPES):
            return NotImplemented
        return _join_units(Chain, other, self)

    def __floordiv__(self, other):
        """operator //: connect units in parallel"""
        if not isinstance(other, _UNIT_TYPES):
            return NotImplemented
        return _join_units(Fork, self, other)

    def __rfloordiv__(self, other):
        """operator //: connect units in parallel"""
        if not isinstance(other, _UNIT_TYPES):
            return NotImplemented
        return _join_units(Fork, other, self)

    def __pos__(self):
        """unary operator +: add Pass() in parallel to this unit"""
        return Fork([ Pass(), self ])

    def __repr__(self):
        # anything that went through @_unit_repr will have _name, _args and _kwargs attributes
        if hasattr(self, '_name'):
            name = self._name
            args = ', '.join(repr(a) for a in self._args)
            kwargs = ', '.join('%s=%s' % (k, repr(self._kwargs[k])) for k in self._kwargs)
            sep = ', ' if args and kwargs else ''
            return '%s(%s%s%s)' % (name, args, sep, kwargs)
        else:
            # is this the best we can do?
            return self.__class__.__name__


# the types we accept as part of a patch
_UNIT_TYPES = (_Unit, list, dict)


def _join_units(t, a, b):
    """
    combine units in a single instance of type t, avoiding nesting if possible.
    """
    if not isinstance(a, t):
        a = [a]
    if not isinstance(b, t):
        b = [b]
    return t(a + b)


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
    def __init__(self, units, remove_duplicates=None):
        list.__init__(self, units)
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
    """
    base class for anything that can act as a selector.
    derived classes must implement methods build() and build_inverted().
    """
    def __and__(self, other):
        """operator &"""
        if not isinstance(other, _Selector):
            return NotImplemented
        return _join_units(_AndSelector, self, other)

    def __or__(self, other):
        """operator |"""
        if not isinstance(other, _Selector):
            return NotImplemented
        return _join_units(_OrSelector, self, other)

    def __mod__(self, other):
        """operator %: apply the selector"""
        return Fork([
            self.build() >> other,
            self.build_inverted(),
        ])


class _AndSelector(_Selector):
    def __init__(self, conditions):
        self.conditions = conditions

    def build(self):
        return Chain(p.build() for p in self.conditions)

    def build_inverted(self):
        return Fork(p.build_inverted() for p in self.conditions)


class _OrSelector(_Selector):
    def __init__(self, conditions):
        self.conditions = conditions

    def build(self):
        return Fork(p.build() for p in self.conditions)

    def build_inverted(self):
        return Chain(p.build_inverted() for p in self.conditions)


class _Filter(_Unit, _Selector):
    """
    wrapper class for all filters.
    """
    def __init__(self, unit):
        _Unit.__init__(self, unit)

    def __invert__(self):
        """unary operator ~: invert the filter, but still act on the same event types"""
        return _InvertedFilter(self, False)

    def __neg__(self):
        """unary operator -: invert the filter, ignoring event types"""
        return _InvertedFilter(self, True)

    def build(self):
        return self

    def build_inverted(self):
        return -self


class _InvertedFilter(_Filter):
    """
    inverted filter. keeps a reference to the original filter unit.
    """
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
        # reduce all arguments to a single bitmask
        types = reduce(lambda x,y: x|y, args)
    else:
        types = args[0]
    return _Filter(_mididings.TypeFilter(types))


@_unit_repr
def Pass(p=True):
    """
    pass all events.
    """
    return _Unit(_mididings.Pass(p))


@_unit_repr
def Discard():
    """
    discard all events.
    """
    return _Unit(_mididings.Pass(False))
