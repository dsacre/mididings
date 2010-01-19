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

from mididings.units.base import _Unit, _unit_repr

import mididings.constants as _constants
import mididings.util as _util
import mididings.misc as _misc


@_unit_repr
def Generator(type, port, channel, data1=0, data2=0):
    return _Unit(_mididings.Generator(
        _util.event_type(type),
        _util.port_number(port) if isinstance(port, str) or port >= 0 else port,
        _util.channel_number(channel) if channel >= 0 else channel,
        data1, data2
    ))


def Ctrl(*args, **kwargs):
    port, channel, ctrl, value = _misc.call_overload(args, kwargs, [
        lambda ctrl, value: (_constants.EVENT_PORT, _constants.EVENT_CHANNEL, ctrl, value),
        lambda port, channel, ctrl, value: (port, channel, ctrl, value)
    ])
    return Generator(
        _constants.CTRL,
        port, channel,
        _util.ctrl_number(ctrl) if ctrl >= 0 else ctrl,
        _util.ctrl_value(value) if value >= 0 else value
    )

@_misc.deprecated('Ctrl')
def CtrlChange(*args, **kwargs):
    return Ctrl(*args, **kwargs)


def Prog(*args, **kwargs):
    port, channel, program = _misc.call_overload(args, kwargs, [
        lambda program: (_constants.EVENT_PORT, _constants.EVENT_CHANNEL, program),
        lambda port, channel, program: (port, channel, program)
    ])
    return Generator(
        _constants.PROGRAM,
        port, channel,
        0, _util.program_number(program)
    )

@_misc.deprecated('Prog')
def ProgChange(*args, **kwargs):
    return Prog(*args, **kwargs)


def NoteOn(*args, **kwargs):
    port, channel, note, velocity = _misc.call_overload(args, kwargs, [
        lambda note, velocity: (_constants.EVENT_PORT, _constants.EVENT_CHANNEL, note, velocity),
        lambda port, channel, note, velocity: (port, channel, note, velocity)
    ])
    return Generator(
        _constants.NOTEON,
        port, channel,
        _util.note_number(note) if note >= 0 else note,
        _util.velocity_value(velocity) if velocity >= 0 else velocity
    )


def NoteOff(*args, **kwargs):
    port, channel, note, velocity = _misc.call_overload(args, kwargs, [
        lambda note, velocity: (_constants.EVENT_PORT, _constants.EVENT_CHANNEL, note, velocity),
        lambda port, channel, note, velocity: (port, channel, note, velocity)
    ])
    return Generator(
        _constants.NOTEOFF,
        port, channel,
        _util.note_number(note) if note >= 0 else note,
        _util.velocity_value(velocity) if velocity >= 0 else velocity
    )


def SysEx(*args, **kwargs):
    port, sysex = _misc.call_overload(args, kwargs, [
        lambda sysex: (_constants.EVENT_PORT, sysex),
        lambda port, sysex: (port, sysex)
    ])
    sysex = _util.sysex_data(sysex)
    return _Unit(_mididings.SysExGenerator(port, sysex))
