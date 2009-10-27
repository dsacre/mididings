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

from mididings import event as _event
from mididings import util as _util

import functools


class _UnitMeta(type):
    """
    meta class for all units.
    changes the c'tor to save its arguments as instance members.
    """
    def __new__(cls, name, bases, attrs):
        if not name.startswith('_') and '__init__' in attrs:
            init = attrs['__init__']

            @functools.wraps(init)
            def init_wrapper(self, *args, **kwargs):
                self._args = args
                self._kwargs = kwargs

                # TODO: this would be a good place to do some argument checking and improve error messages
                return init(self, *args, **kwargs)

            attrs['__init__'] = init_wrapper

        return super(_UnitMeta, cls).__new__(cls, name, bases, attrs)


class _Unit:
    """
    base class for all units.
    """
    __metaclass__ = _UnitMeta

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
        if hasattr(self, '_args') and hasattr(self, '_kwargs'):
            args = ', '.join(repr(a) for a in self._args)
            if len(self._kwargs):
                kwargs = ', ' + ', '.join('%s=%s' % (k, repr(self._kwargs[k])) for k in self._kwargs)
            else:
                kwargs = ''
            return '%s(%s%s)' % (self.__class__.__name__, args, kwargs)
        else:
            return self.__class__.__name__


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
    def __init__(self, units, types=_event.ANY, remove_duplicates=None):
        if types == _event.ANY:
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


class _Filter(_Unit):
    """
    base class for all filters.
    """
    # operator ~ inverts the filter but still acts on the same event types
    def __invert__(self):
        return _InvertedFilter(self, False)

    # operator - inverts the filter ignoring event types
    def __neg__(self):
        return _InvertedFilter(self, True)

    # operator %
    def __mod__(self, other):
        return Fork([ self >> other, -self ])


class _InvertedFilter(_Filter):
    def __init__(self, filt, ignore_types):
        self.filt = filt
        self.ignore_types = ignore_types
        _Filter.__init__(self, _mididings.InvertedFilter(filt.unit, ignore_types))

    def __repr__(self):
        prefix = '-' if self.ignore_types else '~'
        return '%s%s' % (prefix, repr(self.filt))


class Filter(_Filter):
    """
    filter by event type.
    """
    def __init__(self, *args):
        if len(args) > 1:
            types = reduce(lambda x,y: x|y, args)
        else:
            types = args[0]
        _Filter.__init__(self, _mididings.Filter(types))


class Pass(_Unit):
    def __init__(self, p=True):
        _Unit.__init__(self, _mididings.Pass(p))


class Discard(_Unit):
    def __init__(self):
        _Unit.__init__(self, _mididings.Pass(False))


class Sanitize(_Unit):
    def __init__(self):
        _Unit.__init__(self, _mididings.Sanitize())


class SceneSwitch(_Unit):
    def __init__(self, num=_event.EVENT_PROGRAM):
        _Unit.__init__(self, _mididings.SceneSwitch(_util.scene_number(num) if num >= 0 else num))

# for backward compatibility, deprecated
PatchSwitch = SceneSwitch
