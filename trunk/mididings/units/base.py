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

import mididings.constants as _constants
import mididings.arguments as _arguments
import mididings.unitrepr as _unitrepr


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
        return _join_units(_Chain, self, other)

    def __rrshift__(self, other):
        """
        Connect units in series (operator >>).
        """
        if not isinstance(other, _UNIT_TYPES):
            return NotImplemented
        return _join_units(_Chain, other, self)

    def __floordiv__(self, other):
        """
        Connect units in parallel (operator //).
        """
        if not isinstance(other, _UNIT_TYPES):
            return NotImplemented
        return _join_units(_Fork, self, other)

    def __rfloordiv__(self, other):
        """
        Connect units in parallel (operator //).
        """
        if not isinstance(other, _UNIT_TYPES):
            return NotImplemented
        return _join_units(_Fork, other, self)

    def __pos__(self):
        """
        Apply to duplicate (unary operator +)
        """
        return Fork([ Pass(), self ])

    def __repr__(self):
        return _unitrepr.unit_to_string(self)


def _join_units(t, a, b):
    """
    Combine units in a single instance of type t, avoiding nesting if possible.
    """
    if not isinstance(a, t):
        a = [a]
    if not isinstance(b, t):
        b = [b]
    return t(a + b)


class _Chain(_Unit, list):
    def __init__(self, units):
        list.__init__(self, units)

    def __repr__(self):
        return _unitrepr.chain_to_string(self)


class _Fork(_Unit, list):
    def __init__(self, units, remove_duplicates=None):
        list.__init__(self, units)
        self.remove_duplicates = remove_duplicates

    def __repr__(self):
        return _unitrepr.fork_to_string(self)


class _Split(_Unit, dict):
    def __init__(self, d):
        dict.__init__(self, d)

    def __repr__(self):
        return _unitrepr.split_to_string(self)


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
        return _join_selectors(_AndSelector, self, other)

    def __or__(self, other):
        """
        Return disjunction of multiple filters (operator |).
        """
        if not isinstance(other, _Selector):
            return NotImplemented
        return _join_selectors(_OrSelector, self, other)

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


class _AndSelector(_Selector):
    def __init__(self, conditions):
        self.conditions = conditions

    def build(self):
        return Chain(p.build() for p in self.conditions)

    def build_negated(self):
        return Fork(p.build_negated() for p in self.conditions)


class _OrSelector(_Selector):
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
        return _unitrepr.inverted_filter_to_string(self)


# the types we accept as part of a patch
_UNIT_TYPES = (_Unit, list, dict)
_SELECTOR_TYPES = (_Filter, _Selector)


@_arguments.accept([_UNIT_TYPES])
def Chain(units):
    """
    Units connected in series.
    """
    return _Chain(units)


@_arguments.accept([_UNIT_TYPES], (True, False, None))
def Fork(units, remove_duplicates=None):
    """
    Units connected in parallel.
    """
    return _Fork(units, remove_duplicates)


@_arguments.accept({_arguments.nullable(_arguments.reduce_bitmask([_constants._EventType])): _UNIT_TYPES})
def Split(d):
    """
    Split events by type.
    """
    return _Split(d)


@_arguments.accept([_SELECTOR_TYPES])
def AndSelector(conditions):
    """
    Conjunction of multiple filters.
    """
    return _AndSelector(conditions)


@_arguments.accept([_SELECTOR_TYPES])
def OrSelector(conditions):
    """
    Disjunction of multiple filters.
    """
    return _OrSelector(conditions)


@_arguments.accept(_arguments.reduce_bitmask([_constants._EventType]), with_rest=True)
@_unitrepr.store
def Filter(types, *rest):
    """
    Filter by event type.
    """
    return _Filter(_mididings.TypeFilter(types))


@_unitrepr.store
def Pass():
    """
    Pass all events.
    """
    return _Unit(_mididings.Pass(True))


@_unitrepr.store
def Discard():
    """
    Discard all events.
    """
    return _Unit(_mididings.Pass(False))
