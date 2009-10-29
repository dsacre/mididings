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

from mididings.units.base import _Filter, _unit_repr

import mididings.util as _util
import mididings.misc as _misc


@_unit_repr
def PortFilter(*args):
    v = _misc.make_int_vector((_util.port_number(p) for p in _misc.flatten(args)))
    return _Filter(_mididings.PortFilter(v))


@_unit_repr
def ChannelFilter(*args):
    v = _misc.make_int_vector((_util.channel_number(c) for c in _misc.flatten(args)))
    return _Filter(_mididings.ChannelFilter(v))


@_unit_repr
def KeyFilter(*args):
    if len(args) == 1:
        args = args[0]
    r = _util.note_range(args)
    return _Filter(_mididings.KeyFilter(r[0], r[1]))


@_unit_repr
def VelocityFilter(min, max):
    return _Filter(_mididings.VelocityFilter(min, max))


@_unit_repr
def CtrlFilter(*args):
    v = _misc.make_int_vector(_util.ctrl_number(c) for c in _misc.flatten(args))
    return _Filter(_mididings.CtrlFilter(v))


@_unit_repr
def CtrlValueFilter(lower, upper=0):
    return _Filter(_mididings.CtrlValueFilter(_util.ctrl_value(lower), _util.ctrl_value(upper)))


@_unit_repr
def ProgFilter(*args):
    v = _misc.make_int_vector(_util.program_number(p) for p in _misc.flatten(args))
    return _Filter(_mididings.ProgFilter(v))
