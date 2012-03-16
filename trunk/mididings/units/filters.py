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

from mididings.units.base import _Filter, _unit_repr

import mididings.util as _util
import mididings.misc as _misc
import mididings.overload as _overload


@_unit_repr
def PortFilter(*args):
    ports = (_util.port_number(p) for p in _misc.flatten(args))
    return _Filter(_mididings.PortFilter(ports))


@_unit_repr
def ChannelFilter(*args):
    channels = (_util.channel_number(c) for c in _misc.flatten(args))
    return _Filter(_mididings.ChannelFilter(channels))


@_unit_repr
def KeyFilter(*args, **kwargs):
    note_range = _overload.call(args, kwargs, [
        lambda note_range: _util.note_range(note_range),
        lambda lower, upper: _util.note_range((lower, upper)),
        lambda lower: _util.note_range((lower, 0)),
        lambda upper: _util.note_range((0, upper)),
        lambda notes: list(notes),
    ])
    if isinstance(note_range, list):
        notes = (_util.note_number(k) for k in note_range)
        return _Filter(_mididings.KeyFilter(0, 0, notes))
    else:
        return _Filter(_mididings.KeyFilter(note_range[0], note_range[1], []))


@_unit_repr
def VelocityFilter(*args, **kwargs):
    lower, upper = _overload.call(args, kwargs, [
        lambda value: (value, value+1),
        lambda lower: (lower, 0),
        lambda upper: (0, upper),
        lambda lower, upper: (lower, upper),
    ])
    return _Filter(_mididings.VelocityFilter(lower, upper))


@_unit_repr
def CtrlFilter(*args):
    ctrls = (_util.ctrl_number(c) for c in _misc.flatten(args))
    return _Filter(_mididings.CtrlFilter(ctrls))


@_unit_repr
def CtrlValueFilter(*args, **kwargs):
    lower, upper = _overload.call(args, kwargs, [
        lambda value: (value, value+1),
        lambda lower: (lower, 0),
        lambda upper: (0, upper),
        lambda lower, upper: (lower, upper),
    ])
    return _Filter(_mididings.CtrlValueFilter(lower, upper))


@_unit_repr
def ProgramFilter(*args):
    progs = (_util.program_number(p) for p in _misc.flatten(args))
    return _Filter(_mididings.ProgramFilter(progs))


@_unit_repr
@_overload.mark
def SysExFilter(sysex):
    sysex = _util.sysex_data(sysex, allow_partial=True)
    partial = (sysex[-1] != '\xf7')
    return _Filter(_mididings.SysExFilter(sysex, partial))

@_unit_repr
@_overload.mark
def SysExFilter(manufacturer):
    sysex = '\xf0' + _util.sysex_manufacturer(manufacturer)
    return _Filter(_mididings.SysExFilter(sysex, True))
