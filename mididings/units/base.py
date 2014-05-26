# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2014  Dominic Sacré  <dominic.sacre@gmx.de>
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
        return self.add()

    def add(self):
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
    def __init__(self, mapping):
        dict.__init__(self, mapping)

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
        if isinstance(other, tuple) and len(other) in (1, 2):
            return self.apply(*other)
        else:
            return self.apply(other)

    def apply(self, patch, else_patch=None):
        if else_patch is None:
            return Fork([
                self.build() >> patch,
                self.build_negated(),
            ])
        else:
            return Fork([
                self.build() >> patch,
                self.build_negated() >> else_patch,
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
_UNIT_TYPES = (_Unit, list, dict, _constants._EventType)
_SELECTOR_TYPES = (_Filter, _Selector, _constants._EventType)


@_arguments.accept([_UNIT_TYPES], add_varargs=True)
def Chain(units):
    """
    Units connected in series.
    """
    # handle a single list argument differently for backward compatibility
    if len(units) == 1 and type(units[0]) == list:
        units = units[0]

    return _Chain(units)


@_arguments.accept([_UNIT_TYPES], add_varargs=True,
                   kwargs={'remove_duplicates': (True, False, None)})
def Fork(units, **kwargs):
    """
    Units connected in parallel.
    """
    remove_duplicates = (kwargs['remove_duplicates']
                            if 'remove_duplicates' in kwargs else None)

    # handle a single list argument differently for backward compatibility
    if len(units) == 1 and type(units[0]) == list:
        units = units[0]

    return _Fork(units, remove_duplicates)


@_arguments.accept({
    _arguments.nullable(_arguments.reduce_bitmask([_constants._EventType])):
        _UNIT_TYPES
})
def Split(mapping):
    """
    Split(mapping)

    Split by event type.
    """
    return _Split(mapping)


@_arguments.accept([_SELECTOR_TYPES])
def And(conditions):
    """
    Conjunction of multiple filters.
    """
    return _AndSelector(conditions)


@_arguments.accept([_SELECTOR_TYPES])
def Or(conditions):
    """
    Disjunction of multiple filters.
    """
    return _OrSelector(conditions)


# for backward compatibility
AndSelector = And
OrSelector = Or


@_unitrepr.accept(_arguments.reduce_bitmask([_constants._EventType]),
                  add_varargs=True)
def Filter(types):
    """
    Filter(types, ...)

    Filter by event type. Multiple types can be given as bitmasks, lists, or
    separate parameters.
    """
    return _Filter(_mididings.TypeFilter(types))


@_unitrepr.store
def Pass():
    """
    Do nothing. This is sometimes useful/necessary as a placeholder, much like
    the ``pass`` statement in Python.
    """
    return _Unit(_mididings.Pass(True))


@_unitrepr.store
def Discard():
    """
    Stop processing the incoming event. Note that it is rarely neccessary to
    use this, as filters and splits already take care of removing unwanted
    events.
    """
    return _Unit(_mididings.Pass(False))
