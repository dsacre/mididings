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

from mididings.units.base import _Filter

import mididings.util as _util
import mididings.overload as _overload
import mididings.arguments as _arguments
import mididings.unitrepr as _unitrepr

import functools as _functools


@_unitrepr.accept(_arguments.flatten(_util.port_number), with_rest=True)
def PortFilter(ports, *rest):
    """
    Filter by port.
    """
    return _Filter(_mididings.PortFilter(map(_util.actual, ports)))


@_unitrepr.accept(_arguments.flatten(_util.channel_number), with_rest=True)
def ChannelFilter(channels, *rest):
    """
    Filter by channel.
    """
    return _Filter(_mididings.ChannelFilter(map(_util.actual, channels)))


@_overload.mark(
    """
    Filter by key.
    """
)
@_unitrepr.accept(_util.note_range)
def KeyFilter(note_range):
    return _Filter(_mididings.KeyFilter(note_range[0], note_range[1], []))

@_overload.mark
@_unitrepr.accept(_util.note_limit, _util.note_limit)
def KeyFilter(lower, upper):
    return _Filter(_mididings.KeyFilter(lower, upper, []))

@_overload.mark
@_unitrepr.accept(_util.note_limit)
def KeyFilter(lower):
    return _Filter(_mididings.KeyFilter(lower, 0, []))

@_overload.mark
@_unitrepr.accept(_util.note_limit)
def KeyFilter(upper):
    return _Filter(_mididings.KeyFilter(0, upper, []))

@_overload.mark
@_unitrepr.accept([_util.note_number])
def KeyFilter(notes):
    return _Filter(_mididings.KeyFilter(0, 0, notes))


@_overload.mark(
    """
    Filter by note-on velocity.
    """
)
@_unitrepr.accept(_util.velocity_value)
def VelocityFilter(value):
    return _Filter(_mididings.VelocityFilter(value, value + 1))

@_overload.mark
@_unitrepr.accept(_util.velocity_limit)
def VelocityFilter(lower):
    return _Filter(_mididings.VelocityFilter(lower, 0))

@_overload.mark
@_unitrepr.accept(_util.velocity_limit)
def VelocityFilter(upper):
    return _Filter(_mididings.VelocityFilter(0, upper))

@_overload.mark
@_unitrepr.accept(_util.velocity_limit, _util.velocity_limit)
def VelocityFilter(lower, upper):
    return _Filter(_mididings.VelocityFilter(lower, upper))


@_unitrepr.accept(_arguments.flatten(_util.ctrl_number), with_rest=True)
def CtrlFilter(ctrls, *rest):
    """
    Filter by controller number.
    """
    return _Filter(_mididings.CtrlFilter(ctrls))


@_overload.mark(
    """
    Filter by controller value.
    """
)
@_unitrepr.accept(_util.ctrl_value)
def CtrlValueFilter(value):
    return _Filter(_mididings.CtrlValueFilter(value, value + 1))

@_overload.mark
@_unitrepr.accept(_util.ctrl_limit)
def CtrlValueFilter(lower):
    return _Filter(_mididings.CtrlValueFilter(lower, 0))

@_overload.mark
@_unitrepr.accept(_util.ctrl_limit)
def CtrlValueFilter(upper):
    return _Filter(_mididings.CtrlValueFilter(0, upper))

@_overload.mark
@_unitrepr.accept(_util.ctrl_limit, _util.ctrl_limit)
def CtrlValueFilter(lower, upper):
    return _Filter(_mididings.CtrlValueFilter(lower, upper))


@_unitrepr.accept(_arguments.flatten(_util.program_number), with_rest=True)
def ProgramFilter(programs, *rest):
    """
    Filter by program number.
    """
    return _Filter(_mididings.ProgramFilter(map(_util.actual, programs)))


@_overload.mark(
    """
    Filter by sysex data.
    """
)
@_unitrepr.accept(_functools.partial(_util.sysex_data, allow_partial=True))
def SysExFilter(sysex):
    partial = (sysex[-1] != '\xf7')
    return _Filter(_mididings.SysExFilter(sysex, partial))

@_overload.mark
@_unitrepr.accept(_util.sysex_manufacturer)
def SysExFilter(manufacturer):
    sysex = _util.sysex_to_sequence([0xf0]) + manufacturer
    return _Filter(_mididings.SysExFilter(sysex, True))
