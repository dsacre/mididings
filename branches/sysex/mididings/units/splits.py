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
from mididings.units.filters import CtrlFilter, CtrlValueFilter, ProgFilter

from mididings import event as _event


def PortSplit(d):
    return Fork([ (PortFilter(p) >> w) for p, w in d.items() ])


def ChannelSplit(d):
    return Fork([ (ChannelFilter(c) >> w) for c, w in d.items() ])


def KeySplit(*args):
    if len(args) == 1:
        # KeySplit(d)
        return Fork([
            (KeyFilter(k) >> w) for k, w in args[0].items()
        ])
    elif len(args) == 3:
        # KeySplit(key, unit_lower, unit_upper)
        key, unit_lower, unit_upper = args
        filt = KeyFilter(0, key)
        return Fork([
            filt  >> unit_lower,
            ~filt >> unit_upper
        ])
    else:
        raise TypeError("KeySplit() must be called with either one or three arguments")


def VelocitySplit(*args):
    if len(args) == 1:
        # VelocitySplit(d)
        return Fork([
            (VelocityFilter(v) >> w) for v, w in args[0].items()
        ])
    elif len(args) == 3:
        # VelocitySplit(thresh, unit_lower, unit_upper)
        thresh, unit_lower, unit_upper = args
        filt = VelocityFilter(0, thresh)
        return Fork([
            filt  >> unit_lower,
            ~filt >> unit_upper
        ])
    else:
        raise TypeError("VelocitySplit() must be called with either one or three arguments")


def CtrlSplit(d):
    return Filter(_event.CTRL) % [ (CtrlFilter(c) >> w) for c, w in d.items() ]


def CtrlValueSplit(*args):
    if len(args) == 1:
        # CtrlValueSplit(d)
        return Filter(_event.CTRL) % [
            ((CtrlValueFilter(*v) if isinstance(v, tuple) else CtrlValueFilter(v)) >> w) for v, w in args[0].items()
        ]
    elif len(args) == 3:
        # CtrlValueSplit(thresh, unit_lower, unit_upper)
        thresh, unit_lower, unit_upper = args
        filt = CtrlValueFilter(0, thresh)
        return Filter(_event.CTRL) % [
            filt  >> unit_lower,
            ~filt >> unit_upper
        ]
    raise TypeError("CtrlValueSplit() must be called with either one or three arguments")


def ProgSplit(d):
    return Filter(_event.PROGRAM) % [ (ProgFilter(p) >> w) for p, w in d.items() ]
