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
import constants as _constants
import util as _util
from setup import get_config as _get_config


def _make_get_set(type_, data, offset=lambda: 0):
    def getter(self):
        if not self.type_ & type_ and not type_ == _constants.ANY:
            print "midi event attribute error"
        return getattr(self, data) + offset()

    def setter(self, value):
        if not self.type_ & type_ and not type_ == _constants.ANY:
            print "midi event attribute error"
        setattr(self, data, value - offset())

    return (getter, setter)


class MidiEvent(_mididings.MidiEvent):
    def __init__(self, type_=0, port_=0, channel_=0, data1=0, data2=0):
        _mididings.MidiEvent.__init__(self)
        self.type_ = type_
        self.port_ = port_
        self.channel_ = channel_
        self.data1 = data1
        self.data2 = data2

    def to_string(self, portnames=[], portname_length=0):
        if len(portnames) > self.port_:
            port = portnames[self.port_]
        else:
            port = str(self.port)

        channel = self.channel

        if self.type_ == _constants.NOTEON:
            s = 'Note on:  %3d %3d  (%s)' % (self.note, self.velocity, _util.note_name(self.note))
        elif self.type_ == _constants.NOTEOFF:
            s = 'Note off: %3d %3d  (%s)' % (self.note, self.velocity, _util.note_name(self.note))
        elif self.type_ == _constants.CTRL:
            s = 'Control:  %3d %3d' % (self.param, self.value)
            n = _util.controller_name(self.param)
            if n: s += '  (%s)' % n
        elif self.type_ == _constants.PITCHBEND:
            s = 'Pitch bend: %+5d' % self.value
        elif self.type_ == _constants.AFTERTOUCH:
            s = 'Aftertouch:   %3d' % self.value
        elif self.type_ == _constants.POLY_AFTERTOUCH:
            s = 'PolyAt:   %3d %3d  (%s)' % (self.note, self.value, _util.note_name(self.note))
        elif self.type_ == _constants.PROGRAM:
            s = 'Program:      %3d' % self.program
        elif self.type_ == _constants.SYSEX:
            d = self.get_sysex_data()
            s = 'SysEx:   %8d  [%s]' % (len(d), ' '.join([ (hex(v/16).upper()[-1] + hex(v%16).upper()[-1]) for v in map(ord, d) ]))
        elif self.type_ == _constants.SYSCM_QFRAME:
            s = 'SysCm QFrame: %3d' % self.data1
        elif self.type_ == _constants.SYSCM_SONGPOS:
            s = 'SysCm SongPos:%3d %3d' % (self.data1, self.data2)
        elif self.type_ == _constants.SYSCM_SONGSEL:
            s = 'SysCm SongSel:%3d' % self.data1
        elif self.type_ == _constants.SYSCM_TUNEREQ:
            s = 'SysCm TuneReq'
        elif self.type_ == _constants.SYSRT_CLOCK:
            s = 'SysRt Clock'
        elif self.type_ == _constants.SYSRT_START:
            s = 'SysRt Start'
        elif self.type_ == _constants.SYSRT_CONTINUE:
            s = 'SysRt Continue'
        elif self.type_ == _constants.SYSRT_STOP:
            s = 'SysRt Stop'
        elif self.type_ == _constants.SYSRT_SENSING:
            s = 'SysRt Sensing'
        elif self.type_ == _constants.SYSRT_RESET:
            s = 'SysRt Reset'
        elif self.type_ == _constants.DUMMY:
            s = 'Dummy'
        else:
            s = 'None'

        return '[%*s, %2d] %s' % (max(portname_length, 2), port, channel, s)

    def __repr__(self):
        return 'MidiEvent(%d, %d, %d, %d, %d)' % (self.type, self.port_, self.channel_, self.data1, self.data2)

    type      = property(*_make_get_set(_constants.ANY, 'type_'))
    port      = property(*_make_get_set(_constants.ANY, 'port_', lambda: _get_config('data_offset')))
    channel   = property(*_make_get_set(_constants.ANY, 'channel_', lambda: _get_config('data_offset')))

    note      = property(*_make_get_set(_constants.NOTE, 'data1'))
    velocity  = property(*_make_get_set(_constants.NOTE, 'data2'))
    param     = property(*_make_get_set(_constants.CTRL | _constants.POLY_AFTERTOUCH, 'data1'))
    value     = property(*_make_get_set(_constants.CTRL | _constants.PITCHBEND | _constants.AFTERTOUCH | _constants.POLY_AFTERTOUCH, 'data2'))
    program   = property(*_make_get_set(_constants.PROGRAM, 'data2', lambda: _get_config('data_offset')))


def NoteOnEvent(port, channel, note, velocity):
    return MidiEvent(
        _constants.NOTEON,
        _util.port_number(port),
        _util.channel_number(channel),
        _util.note_number(note),
        _util.velocity_value(velocity)
    )

def NoteOffEvent(port, channel, note, velocity=0):
    return MidiEvent(
        _constants.NOTEOFF,
        _util.port_number(port),
        _util.channel_number(channel),
        _util.note_number(note),
        _util.velocity_value(velocity)
    )

def CtrlChangeEvent(port, channel, param, value):
    return MidiEvent(
        _constants.CTRL,
        _util.port_number(port),
        _util.channel_number(channel),
        _util.ctrl_number(param),
        _util.ctrl_value(value)
    )

def ProgChangeEvent(port, channel, program):
    return MidiEvent(
        _constants.PROGRAM,
        _util.port_number(port),
        _util.channel_number(channel),
        0,
        _util.program_number(program)
    )
