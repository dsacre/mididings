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

from mididings.units.base import Fork, Filter
from mididings.units.filters import PortFilter, ChannelFilter, KeyFilter, VelocityFilter
from mididings.units.filters import CtrlFilter, CtrlValueFilter, ProgFilter, SysExFilter

import mididings.event as _event
import mididings.misc as _misc


def PortSplit(d):
    return Fork((PortFilter(p) >> w) for p, w in d.items())


def ChannelSplit(d):
    return Fork((ChannelFilter(c) >> w) for c, w in d.items())


def KeySplit(*args, **kwargs):
    def KeySplitDict(d):
        return Fork(
            (KeyFilter(*(k if isinstance(k, tuple) else (k,))) >> w) for k, w in d.items()
        )
    def KeySplitThreshold(key, patch_lower, patch_upper):
        filt = KeyFilter(0, key)
        return Fork([
            filt  >> patch_lower,
            ~filt >> patch_upper
        ])
    return _misc.call_overload(
        'KeySplit', args, kwargs,
        [KeySplitDict, KeySplitThreshold]
    )


def VelocitySplit(*args, **kwargs):
    def VelocitySplitDict(d):
        return Fork(
            (VelocityFilter(*(v if isinstance(v, tuple) else (v,))) >> w) for v, w in d.items()
        )
    def VelocitySplitThreshold(threshold, patch_lower, patch_upper):
        filt = VelocityFilter(0, threshold)
        return Fork([
            filt  >> patch_lower,
            ~filt >> patch_upper
        ])
    return _misc.call_overload(
        'VelocitySplit', args, kwargs,
        [VelocitySplitDict, VelocitySplitThreshold]
    )


def CtrlSplit(d):
    return Fork((CtrlFilter(c) >> w) for c, w in d.items())


def CtrlValueSplit(*args, **kwargs):
    def CtrlValueSplitDict(d):
        return Fork(
            (CtrlValueFilter(*(v if isinstance(v, tuple) else (v,))) >> w) for v, w in d.items()
        )
    def CtrlValueSplitThreshold(threshold, patch_lower, patch_upper):
        filt = CtrlValueFilter(0, threshold)
        return Fork([
            filt  >> patch_lower,
            ~filt >> patch_upper
        ])
    return _misc.call_overload(
        'CtrlValueSplit', args, kwargs,
        [CtrlValueSplitDict, CtrlValueSplitThreshold]
    )


def ProgSplit(d):
    return Fork((ProgFilter(p) >> w) for p, w in d.items())


def SysExSplit(d):
    return Fork((SysExFilter(v) >> w) for v, w in d.items())
