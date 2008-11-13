# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import _mididings

from .. import event as _event


# base class for all units
class _Unit:
    def __rshift__(self, other):
        a = self.units if isinstance(self, _Chain) else [self]
        b = other.units if isinstance(other, _Chain) else [other]
        return _Chain(a + b)

    def __rrshift__(self, other):
        a = other.units if isinstance(other, _Chain) else [other]
        b = self.units if isinstance(self, _Chain) else [self]
        return _Chain(a + b)

    def __floordiv__(self, other):
        return Fork([ self, other ])

    def __rfloordiv__(self, other):
        return Fork([ other, self ])


# units connected in series
class _Chain(_Unit):
    def __init__(self, units):
        self.units = units


# units connected in parallel
class Fork(list, _Unit):
    def __init__(self, units, types=_event.ANY, remove_duplicates=None):
        if types == _event.ANY:
            list.__init__(self, units)
        else:
            # fork only certain types of events
            l = [ (Filter(types) >> x) for x in units ] + \
                [ ~Filter(types) ]
            list.__init__(self, l)
        self.remove_duplicates = remove_duplicates


# split events by type
class Split(dict, _Unit):
    def __init__(self, d):
        dict.__init__(self, d)


# base class for all filters, supporting operator ~
class _Filter(_Unit):
    def __invert__(self):
        return _InvertedFilter(self)
    def __mod__(self, other):
        return Fork([ self >> other, ~self ])


class _InvertedFilter(_mididings.InvertedFilter, _Filter):
    def __init__(self, filt):
        _mididings.InvertedFilter.__init__(self, filt)


# filters by event type
class Filter(_mididings.Filter, _Filter):
    def __init__(self, *args):
        if len(args) > 1:
            types = reduce(lambda x,y: x|y, args)
        else:
            types = args[0]
        _mididings.Filter.__init__(self, types)


class Pass(_mididings.Pass, _Unit):
    def __init__(self, p=True):
        _mididings.Pass.__init__(self, p)


class Discard(_mididings.Pass, _Unit):
    def __init__(self):
        _mididings.Pass.__init__(self, False)


class Sanitize(_mididings.Sanitize, _Unit):
    def __init__(self):
        _mididings.Sanitize.__init__(self)


class PatchSwitch(_mididings.PatchSwitch, _Unit):
    def __init__(self, num=_event.EVENT_PROGRAM):
        _mididings.PatchSwitch.__init__(self, num)
