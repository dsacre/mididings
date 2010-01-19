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
def KeyFilter(*args, **kwargs):
    note_range = _misc.call_overload(args, kwargs, [
            lambda note_range: _util.note_range(note_range),
            lambda note: (_util.note_number(note), 0),
            lambda lower, upper: _util.note_range((lower, upper)),
        ]
    )
    return _Filter(_mididings.KeyFilter(*note_range))


@_unit_repr
def VelocityFilter(*args, **kwargs):
    lower, upper = _misc.call_overload(args, kwargs, [
            lambda value: (value, 0),
            lambda lower, upper: (lower, upper),
        ]
    )
    return _Filter(_mididings.VelocityFilter(lower, upper))


@_unit_repr
def CtrlFilter(*args):
    v = _misc.make_int_vector(_util.ctrl_number(c) for c in _misc.flatten(args))
    return _Filter(_mididings.CtrlFilter(v))


@_unit_repr
def CtrlValueFilter(*args, **kwargs):
    lower, upper = _misc.call_overload(args, kwargs, [
            lambda value: (value, 0),
            lambda lower, upper: (lower, upper),
        ]
    )
    return _Filter(_mididings.CtrlValueFilter(lower, upper))


@_unit_repr
def ProgFilter(*args):
    v = _misc.make_int_vector(_util.program_number(p) for p in _misc.flatten(args))
    return _Filter(_mididings.ProgFilter(v))


@_unit_repr
@_misc.overload
def SysExFilter(sysex):
    sysex = _util.sysex_data(sysex, allow_partial=True)
    partial = (sysex[-1] != '\xf7')
    return _Filter(_mididings.SysExFilter(sysex, partial))

@_unit_repr
@_misc.overload
def SysExFilter(manufacturer):
    sysex = '\xf0' + _util.sysex_manufacturer(manufacturer)
    return _Filter(_mididings.SysExFilter(sysex, True))
