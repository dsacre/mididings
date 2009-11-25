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

from mididings.units.base import _Unit, _unit_repr

import mididings.event as _event
import mididings.util as _util
import mididings.misc as _misc


@_unit_repr
def GenerateEvent(type_, port, channel, data1, data2):
    return _Unit(_mididings.GenerateEvent(
        type_,
        _util.port_number(port) if isinstance(port, str) or port >= 0 else port,
        _util.channel_number(channel) if channel >= 0 else channel,
        data1, data2
    ))


@_unit_repr
def CtrlChange(*args, **kwargs):
    port, channel, ctrl, value = _misc.call_overload(
        'CtrlChange', args, kwargs, [
            lambda ctrl, value: (_event.EVENT_PORT, _event.EVENT_CHANNEL, ctrl, value),
            lambda port, channel, ctrl, value: (port, channel, ctrl, value)
        ]
    )
    return GenerateEvent(
        _event.CTRL,
        port, channel,
        _util.ctrl_number(ctrl) if ctrl >= 0 else ctrl,
        _util.ctrl_value(value) if value >= 0 else value
    )


@_unit_repr
def ProgChange(*args, **kwargs):
    port, channel, program = _misc.call_overload(
        'ProgChange', args, kwargs, [
            lambda program: (_event.EVENT_PORT, _event.EVENT_CHANNEL, program),
            lambda port, channel, program: (port, channel, program)
        ]
    )
    return GenerateEvent(
        _event.PROGRAM,
        port, channel,
        0, _util.program_number(program)
    )


@_unit_repr
def NoteOn(*args, **kwargs):
    port, channel, note, velocity = _misc.call_overload(
        'NoteOn', args, kwargs, [
            lambda note, velocity: (_event.EVENT_PORT, _event.EVENT_CHANNEL, note, velocity),
            lambda port, channel, note, velocity: (port, channel, note, velocity)
        ]
    )
    return GenerateEvent(
        _event.NOTEON,
        port, channel,
        _util.note_number(note) if note >= 0 else note,
        _util.velocity_value(velocity) if velocity >= 0 else velocity
    )


@_unit_repr
def NoteOff(*args, **kwargs):
    port, channel, note, velocity = _misc.call_overload(
        'NoteOff', args, kwargs, [
            lambda note, velocity: (_event.EVENT_PORT, _event.EVENT_CHANNEL, note, velocity),
            lambda port, channel, note, velocity: (port, channel, note, velocity)
        ]
    )
    return GenerateEvent(
        _event.NOTEOFF,
        port, channel,
        _util.note_number(note) if note >= 0 else note,
        _util.velocity_value(velocity) if velocity >= 0 else velocity
    )


@_unit_repr
def SysEx(*args, **kwargs):
    port, sysex = _misc.call_overload(
        'SysEx', args, kwargs, [
            lambda sysex: (_event.EVENT_PORT, sysex),
            lambda port, sysex: (port, sysex)
        ]
    )
    sysex = _util.sysex_data(sysex)
    return _Unit(_mididings.GenerateSysEx(port, sysex))
