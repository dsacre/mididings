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

from mididings.units.base import _Filter

import mididings.util as _util
import mididings.overload as _overload
import mididings.arguments as _arguments
import mididings.unitrepr as _unitrepr

import functools as _functools


@_unitrepr.accept(_arguments.flatten(_util.port_number), add_varargs=True)
def PortFilter(ports):
    """
    PortFilter(ports, ...)

    Filter events by port name or number. The *ports* argument can be a single
    port or a list of multiple ports.
    """
    return _Filter(_mididings.PortFilter(map(_util.actual, ports)))


@_unitrepr.accept(_arguments.flatten(_util.channel_number), add_varargs=True)
def ChannelFilter(channels):
    """
    ChannelFilter(channels, ...)

    Filter events by channel number. The *channels* argument can be a single
    channel number or a list of multiple channel numbers.
    System events (which don't carry channel information) are discarded.
    """
    return _Filter(_mididings.ChannelFilter(map(_util.actual, channels)))


@_overload.mark(
    """
    KeyFilter(note_range)
    KeyFilter(lower, upper)
    KeyFilter(lower=...)
    KeyFilter(upper=...)
    KeyFilter(notes=...)

    Filter note events by key (note number or note range). All other events
    are let through.
    The last form expects its argument to be a list of individual note names
    or numbers.
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
    VelocityFilter(value)
    VelocityFilter(lower=...)
    VelocityFilter(upper=...)
    VelocityFilter(lower, upper)

    Filter note-on events by velocity. All other events are let through.
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


@_unitrepr.accept(_arguments.flatten(_util.ctrl_number), add_varargs=True)
def CtrlFilter(ctrls):
    """
    CtrlFilter(ctrls, ...)

    Filter control change events by controller number. The *ctrls* argument
    can be a single controller or a list of multiple controller numbers.
    All other events are discarded.
    """
    return _Filter(_mididings.CtrlFilter(ctrls))


@_overload.mark(
    """
    CtrlValueFilter(value)
    CtrlValueFilter(lower=...)
    CtrlValueFilter(upper=...)
    CtrlValueFilter(lower, upper)

    Filter control change events by controller value. All other events are
    discarded.
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


@_unitrepr.accept(_arguments.flatten(_util.program_number), add_varargs=True)
def ProgramFilter(programs):
    """
    ProgramFilter(programs, ...)

    Filter program change events by program number. The *programs* argument
    can be a single program number or a list of program numbers.
    All other events are discarded.
    """
    return _Filter(_mididings.ProgramFilter(map(_util.actual, programs)))


@_overload.mark(
    r"""
    SysExFilter(sysex)
    SysExFilter(manufacturer=...)

    Filter system exclusive events by the data they contain, specified as a
    string or as a sequence of integers.
    If *sysex* does not end with ``F7``, partial matches that start with the
    given data bytes are accepted.

    Alternatively, a sysex manufacturer id can be specified, which may be
    either a string or a sequence of integers, with a length of one or three
    bytes.

    All non-sysex events are discarded.
    """
)
@_unitrepr.accept(_functools.partial(_util.sysex_data, allow_partial=True))
def SysExFilter(sysex):
    partial = (sysex[-1] != '\xf7')
    return _Filter(_mididings.SysExFilter(sysex, partial))

@_overload.mark
@_unitrepr.accept(_util.sysex_manufacturer)
def SysExFilter(manufacturer):
    sysex = _util.sysex_to_bytearray([0xf0]) + manufacturer
    return _Filter(_mididings.SysExFilter(sysex, True))
