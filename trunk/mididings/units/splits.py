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

from mididings.units.base import Chain, Fork, Filter
from mididings.units.filters import PortFilter, ChannelFilter, KeyFilter, VelocityFilter
from mididings.units.filters import CtrlFilter, CtrlValueFilter, ProgFilter, SysExFilter

import mididings.event as _event
import mididings.misc as _misc


def _make_split(t, d, unpack=False):
    if unpack:
        # if dictionary key is a tuple, unpack and pass as individual parameters to ctor
        t = lambda p, t=t: t(*(p if isinstance(p, tuple) else (p,)))

    # build dict with all items from d, except d[None]
    dd = dict((k, v) for k, v in d.items() if k != None)

    # build fork from all normal items
    r = Fork((t(k) >> w) for k, w in dd.items())

    # add else-rule, if any
    if None in d:
        f = Chain(~t(k) for k in dd.keys())
        r.append(f >> d[None])

    return r


def _make_threshold(f, patch_lower, patch_upper):
    return Fork([
        f >> patch_lower,
        ~f >> patch_upper,
    ])


def PortSplit(d):
    return _make_split(PortFilter, d)


def ChannelSplit(d):
    return _make_split(ChannelFilter, d)


@_misc.overload
def KeySplit(d):
    return _make_split(KeyFilter, d, unpack=True)

@_misc.overload
def KeySplit(key, patch_lower, patch_upper):
    return _make_threshold(KeyFilter(0, key), patch_lower, patch_upper)


@_misc.overload
def VelocitySplit(d):
    return _make_split(VelocityFilter, d, unpack=True)

@_misc.overload
def VelocitySplit(threshold, patch_lower, patch_upper):
    return _make_threshold(VelocityFilter(0, threshold), patch_lower, patch_upper)


def CtrlSplit(d):
    return _make_split(CtrlFilter, d)


@_misc.overload
def CtrlValueSplit(d):
    return _make_split(CtrlValueFilter, d, unpack=True)

@_misc.overload
def CtrlValueSplit(threshold, patch_lower, patch_upper):
    return _make_threshold(CtrlValueFilter(0, threshold), patch_lower, patch_upper)


def ProgSplit(d):
    return _make_split(ProgFilter, d)


@_misc.overload
def SysExSplit(d):
    return _make_split(SysExFilter, d)

@_misc.overload
def SysExSplit(manufacturers):
    return _make_split(lambda m: SysExFilter(manufacturer=m), manufacturers)
