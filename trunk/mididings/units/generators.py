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

from mididings.units.base import _Unit

import mididings.constants as _constants
import mididings.util as _util
import mididings.overload as _overload
import mididings.unitrepr as _unitrepr


@_unitrepr.accept(_util.event_type, _util.port_number_ref, _util.channel_number_ref, int, int)
def Generator(type, port, channel, data1=0, data2=0):
    """
    Generic generator.
    """
    return _Unit(_mididings.Generator(
        type,
        _util.actual_ref(port),
        _util.actual_ref(channel),
        data1,
        data2
    ))


@_overload.mark(
    """
    Generate note-on event.
    """
)
@_unitrepr.accept(_util.port_number_ref, _util.channel_number_ref, _util.note_number_ref, _util.velocity_value_ref)
def NoteOn(port, channel, note, velocity):
    return _Unit(_mididings.Generator(
        _constants.NOTEON,
        _util.actual_ref(port),
        _util.actual_ref(channel),
        note,
        velocity
    ))

@_overload.mark
def NoteOn(note, velocity):
    return NoteOn(_constants.EVENT_PORT, _constants.EVENT_CHANNEL, note, velocity)


@_overload.mark(
    """
    Generate note-off event.
    """
)
@_unitrepr.accept(_util.port_number_ref, _util.channel_number_ref, _util.note_number_ref, _util.velocity_value_ref)
def NoteOff(port, channel, note, velocity):
    return _Unit(_mididings.Generator(
        _constants.NOTEOFF,
        _util.actual_ref(port),
        _util.actual_ref(channel),
        note,
        velocity
    ))

@_overload.mark
def NoteOff(note, velocity):
    return NoteOff(_constants.EVENT_PORT, _constants.EVENT_CHANNEL, note, velocity)


@_overload.mark(
    """
    Generate control change event.
    """
)
@_unitrepr.accept(_util.port_number_ref, _util.channel_number_ref, _util.ctrl_number_ref, _util.ctrl_value_ref)
def Ctrl(port, channel, ctrl, value):
    return _Unit(_mididings.Generator(
        _constants.CTRL,
        _util.actual_ref(port),
        _util.actual_ref(channel),
        ctrl,
        value
    ))

@_overload.mark
def Ctrl(ctrl, value):
   return Ctrl(_constants.EVENT_PORT, _constants.EVENT_CHANNEL, ctrl, value)


@_overload.mark(
    """
    Generate pitch-bend event.
    """
)
@_unitrepr.accept(_util.port_number_ref, _util.channel_number_ref, int)
def Pitchbend(port, channel, value):
    return _Unit(_mididings.Generator(
        _constants.PITCHBEND,
        _util.actual_ref(port),
        _util.actual_ref(channel),
        0,
        value
    ))

@_overload.mark
def Pitchbend(value):
    return Pitchbend(_constants.EVENT_PORT, _constants.EVENT_CHANNEL, value)


@_overload.mark(
    """
    Generate aftertouch event.
    """
)
@_unitrepr.accept(_util.port_number_ref, _util.channel_number_ref, int)
def Aftertouch(port, channel, value):
    return _Unit(_mididings.Generator(
        _constants.AFTERTOUCH,
        _util.actual_ref(port),
        _util.actual_ref(channel),
        0,
        value
    ))

@_overload.mark
def Aftertouch(value):
    return Aftertouch(_constants.EVENT_PORT, _constants.EVENT_CHANNEL, value)


@_overload.mark(
    """
    Generate program change event.
    """
)
@_unitrepr.accept(_util.port_number_ref, _util.channel_number_ref, _util.program_number_ref)
def Program(port, channel, program):
    return _Unit(_mididings.Generator(
        _constants.PROGRAM,
        _util.actual_ref(port),
        _util.actual_ref(channel),
        0,
        _util.actual_ref(program)
    ))

@_overload.mark
def Program(program):
    return Program(_constants.EVENT_PORT, _constants.EVENT_CHANNEL, program)



@_overload.mark(
    """
    Generate sysex event.
    """
)
@_unitrepr.accept(_util.port_number_ref, _util.sysex_data)
def SysEx(port, sysex):
    return _Unit(_mididings.SysExGenerator(
        _util.actual_ref(port),
        sysex,
    ))

@_overload.mark
def SysEx(sysex):
    return SysEx(_constants.EVENT_PORT, sysex)
