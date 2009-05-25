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

from mididings.units.base import _Unit

from mididings import event as _event
from mididings import util as _util


class GenerateEvent(_mididings.GenerateEvent, _Unit):
    def __init__(self, type_, port, channel, data1, data2):
        _mididings.GenerateEvent.__init__(
            self, type_,
            _util.port_number(port) if isinstance(port, str) or port >= 0 else port,
            _util.channel_number(channel) if channel >= 0 else channel,
            data1, data2
        )


def CtrlChange(*args):
    if len(args) == 2:
        # CrtlChange(ctrl, value)
        ctrl, value = args
        port, channel = _event.EVENT_PORT, _event.EVENT_CHANNEL
    elif len(args) == 4:
        # CrtlChange(port, channel, ctrl, value)
        port, channel, ctrl, value = args
    else:
        raise TypeError("CtrlChange() must be called with either two or four arguments")

    return GenerateEvent(
            _event.CTRL,
            port,
            channel,
            _util.ctrl_number(ctrl) if ctrl >= 0 else ctrl,
            _util.ctrl_value(value) if value >= 0 else value
        )


def ProgChange(*args):
    if len(args) == 1:
        # ProgChange(program)
        program = args[0]
        port, channel = _event.EVENT_PORT, _event.EVENT_CHANNEL
    elif len(args) == 3:
        # ProgChange(port, channel, program)
        port, channel, program = args
    else:
        raise TypeError("ProgChange() must be called with either one or three arguments")

    return GenerateEvent(
            _event.PROGRAM,
            port,
            channel,
            0,
            _util.program_number(program)
        )


def NoteOn(*args):
    if len(args) == 2:
        # NoteOn(note, velocity)
        note, velocity = args
        port, channel = _event.EVENT_PORT, _event.EVENT_CHANNEL
    elif len(args) == 4:
        # NoteOn(port, channel, note, velocity)
        port, channel, note, velocity = args
    else:
        raise TypeError("NoteOn() must be called with either two or four arguments")

    return GenerateEvent(
            _event.NOTEON,
            port,
            channel,
            _util.note_number(note) if note >= 0 else note,
            _util.velocity_value(velocity) if velocity >= 0 else velocity
        )


def NoteOff(*args):
    if len(args) == 2:
        # NoteOff(note, velocity)
        note, velocity = args
        port, channel = _event.EVENT_PORT, _event.EVENT_CHANNEL
    elif len(args) == 4:
        # NoteOff(port, channel, note, velocity)
        port, channel, note, velocity = args
    else:
        raise TypeError("NoteOff() must be called with either two or four arguments")

    return GenerateEvent(
            _event.NOTEOFF,
            port,
            channel,
            _util.note_number(note) if note >= 0 else note,
            _util.velocity_value(velocity) if velocity >= 0 else velocity
        )
