# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2011  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import _mididings

import mididings.misc as _misc

import functools as _functools
import sys as _sys
if _sys.version_info < (2,6):
    _functools.reduce = reduce


class _Unit(object):
    """
    Wrapper class for all units.
    """
    def __init__(self, unit):
        self.unit = unit

    def __rshift__(self, other):
        """
        Connect units in series (operator >>).
        """
        if not isinstance(other, _UNIT_TYPES):
            return NotImplemented
        return _join_units(Chain, self, other)

    def __rrshift__(self, other):
        """
        Connect units in series (operator >>).
        """
        if not isinstance(other, _UNIT_TYPES):
            return NotImplemented
        return _join_units(Chain, other, self)

    def __floordiv__(self, other):
        """
        Connect units in parallel (operator //).
        """
        if not isinstance(other, _UNIT_TYPES):
            return NotImplemented
        return _join_units(Fork, self, other)

    def __rfloordiv__(self, other):
        """
        Connect units in parallel (operator //).
        """
        if not isinstance(other, _UNIT_TYPES):
            return NotImplemented
        return _join_units(Fork, other, self)

    def __pos__(self):
        """
        Apply to duplicate (unary operator +)
        """
        return Fork([ Pass(), self ])

    def __repr__(self):
        if hasattr(self, '_name'):
            # anything that went through @_unit_repr will have _name, _args
            # and _kwargs attributes
            name = self._name
            args = ', '.join(repr(a) for a in self._args)
            kwargs = ', '.join('%s=%r' % (k, self._kwargs[k]) for k in self._kwargs)
            sep = ', ' if args and kwargs else ''
            return '%s(%s%s%s)' % (name, args, sep, kwargs)
        else:
            # is this the best we can do?
            return self.__class__.__name__


# the types we accept as part of a patch
_UNIT_TYPES = (_Unit, list, dict)


def _join_units(t, a, b):
    """
    Combine units in a single instance of type t, avoiding nesting if possible.
    """
    if not isinstance(a, t):
        a = [a]
    if not isinstance(b, t):
        b = [b]
    return t(a + b)


def _unit_repr(f):
    """
    Decorator that modifies the target function f to store its arguments in the
    returned unit.
    """
    @_functools.wraps(f)
    def unit_wrapper(*args, **kwargs):
        u = f(*args, **kwargs)
        u._name = f.name if isinstance(f, _misc.Overload) else f.__name__
        u._args = args
        u._kwargs = kwargs
        return u
    return unit_wrapper


class Chain(_Unit, list):
    """
    Units connected in series.
    """
    def __init__(self, units):
        list.__init__(self, units)

    def __repr__(self):
        return ' >> '.join(repr(u) for u in self)


class Fork(_Unit, list):
    """
    Units connected in parallel.
    """
    def __init__(self, units, remove_duplicates=None):
        list.__init__(self, units)
        self.remove_duplicates = remove_duplicates

    def __repr__(self):
        r = '[' + ', '.join(repr(u) for u in self) + ']'
        if self.remove_duplicates != None:
            return 'Fork(%s, remove_duplicates=%r)' % (r, self.remove_duplicates)
        else:
            return r


class Split(_Unit, dict):
    """
    Split events by type.
    """
    def __init__(self, d):
        dict.__init__(self, d)

    def __repr__(self):
        return '{' + ', '.join('%r: %r' % (t, self[t]) for t in self.keys()) + '}'


class _Selector(object):
    """
    Base class for anything that can act as a selector.
    Derived classes must implement methods build() and build_negated().
    """
    def __and__(self, other):
        """
        Return conjunction of multiple filters (operator &).
        """
        if not isinstance(other, _Selector):
            return NotImplemented
        return _join_selectors(AndSelector, self, other)

    def __or__(self, other):
        """
        Return disjunction of multiple filters (operator |).
        """
        if not isinstance(other, _Selector):
            return NotImplemented
        return _join_selectors(OrSelector, self, other)

    def __mod__(self, other):
        """
        Apply the selector (operator %).
        """
        return self.apply(other)

    def apply(self, patch):
        return Fork([
            self.build() >> patch,
            self.build_negated(),
        ])


class AndSelector(_Selector):
    """
    Conjunction of multiple filters.
    """
    def __init__(self, conditions):
        self.conditions = conditions

    def build(self):
        return Chain(p.build() for p in self.conditions)

    def build_negated(self):
        return Fork(p.build_negated() for p in self.conditions)


class OrSelector(_Selector):
    """
    Disjunction of multiple filters.
    """
    def __init__(self, conditions):
        self.conditions = conditions

    def build(self):
        return Fork(p.build() for p in self.conditions)

    def build_negated(self):
        return Chain(p.build_negated() for p in self.conditions)


def _join_selectors(t, a, b):
    """
    Combine selectors in a single instance of type t.
    """
    if isinstance(a, t):
        a = a.conditions
    else:
        a = [a]
    if isinstance(b, t):
        b = b.conditions
    else:
        b = [b]
    return t(a + b)


class _Filter(_Unit, _Selector):
    """
    Wrapper class for all filters.
    """
    def __init__(self, unit):
        _Unit.__init__(self, unit)

    def __invert__(self):
        """
        Invert the filter (still act on the same event types, unary
        operator ~).
        """
        return self.invert()

    def __neg__(self):
        """
        Negate the filter (ignoring event types, unary operator -)
        """
        return self.negate()

    def invert(self):
        return _InvertedFilter(self, False)

    def negate(self):
        return _InvertedFilter(self, True)

    def build(self):
        return self

    def build_negated(self):
        return self.negate()


class _InvertedFilter(_Filter):
    """
    Inverted filter. keeps a reference to the original filter unit.
    """
    def __init__(self, filt, negate):
        self.filt = filt
        self.negate = negate
        _Filter.__init__(self, _mididings.InvertedFilter(filt.unit, negate))

    def __repr__(self):
        prefix = '-' if self.negate else '~'
        return '%s%r' % (prefix, self.filt)


@_unit_repr
def Filter(*args):
    """
    Filter by event type.
    """
    if len(args) > 1:
        # reduce all arguments to a single bitmask
        types = _functools.reduce(lambda x,y: x|y, args)
    else:
        types = args[0]
    return _Filter(_mididings.TypeFilter(types))


@_unit_repr
def Pass(p=True):
    """
    Pass all events.
    """
    return _Unit(_mididings.Pass(p))


@_unit_repr
def Discard():
    """
    Discard all events.
    """
    return _Unit(_mididings.Pass(False))
