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

import mididings.constants as _constants
import mididings.util as _util
import mididings.misc as _misc
from mididings.setup import get_config as _get_config


def _make_get_set(type, data, name=None, offset=lambda: 0):
    def getter(self):
        if not self.type & type and not type == _constants.ANY:
            raise AttributeError("event type '%s' has no attribute '%s'" % (self.type_to_string(), name))
        return getattr(self, data) + offset()

    def setter(self, value):
        if not self.type & type and not type == _constants.ANY:
            raise AttributeError("event type '%s' has no attribute '%s'" % (self.type_to_string(), name))
        setattr(self, data, value - offset())

    return (getter, setter)


class MidiEvent(_mididings.MidiEvent):
    """
    The main MIDI event class.
    All event data is part of the C++ base class.
    """
    def __init__(self, type=0, port_=0, channel_=0, data1=0, data2=0):
        _mididings.MidiEvent.__init__(self)
        self.type = type
        self.port_ = port_
        self.channel_ = channel_
        self.data1 = data1
        self.data2 = data2

    def type_to_string(self):
        try:
            return _constants._EVENT_TYPE_NAMES[self.type]
        except KeyError:
            return 'None'

    def to_string(self, portnames=[], portname_length=0, max_length=0):
        if len(portnames) > self.port_:
            port = portnames[self.port_]
        else:
            port = str(self.port)

        h = '[%*s, %2d]' % (max(portname_length, 2), port, self.channel)
        t = self.type_to_string()

        if self.type == _constants.NOTEON:
            s = '  %3d %3d  (%s)' % (self.note, self.velocity, _util.note_name(self.note))
        elif self.type == _constants.NOTEOFF:
            s = ' %3d %3d  (%s)' % (self.note, self.velocity, _util.note_name(self.note))
        elif self.type == _constants.CTRL:
            s = '     %3d %3d' % (self.param, self.value)
            n = _util.controller_name(self.param)
            if n: s += '  (%s)' % n
        elif self.type == _constants.PITCHBEND:
            s = ' %5d' % self.value
        elif self.type == _constants.AFTERTOUCH:
            s = '   %3d' % self.value
        elif self.type == _constants.POLY_AFTERTOUCH:
            s = ' %3d %3d  (%s)' % (self.note, self.value, _util.note_name(self.note))
        elif self.type == _constants.PROGRAM:
            s = '      %3d' % self.program
        elif self.type == _constants.SYSEX:
            data = self.sysex
            if max_length:
                m = (max_length - len(h) - 25) / 3
                if len(data) > m:
                    hexstring = '%s ...' % _misc.string_to_hex(data[:m])
                else:
                    hexstring = _misc.string_to_hex(data)
            else:
                hexstring = _misc.string_to_hex(data)
            s = '   %8d  [%s]' % (len(data), hexstring)
        elif self.type == _constants.SYSCM_QFRAME:
            s = ' %3d' % self.data1
        elif self.type == _constants.SYSCM_SONGPOS:
            s = '%3d %3d' % (self.data1, self.data2)
        elif self.type == _constants.SYSCM_SONGSEL:
            s = '%3d' % self.data1
        else:
            s = None

        if s:
            return '%s %s:%s' % (h, t, s)
        else:
            return '%s %s' % (h, t)

    def __repr__(self):
        return 'MidiEvent(%d, %d, %d, %d, %d)' % (self.type, self.port_, self.channel_, self.data1, self.data2)

    # port/channel attributes with data offset
    port      = property(*_make_get_set(_constants.ANY, 'port_', offset=lambda: _get_config('data_offset')))
    channel   = property(*_make_get_set(_constants.ANY, 'channel_', offset=lambda: _get_config('data_offset')))

    # event-type specific attributes
    note      = property(*_make_get_set(_constants.NOTE, 'data1', 'note'))
    velocity  = property(*_make_get_set(_constants.NOTE, 'data2', 'velocity'))
    param     = property(*_make_get_set(_constants.CTRL | _constants.POLY_AFTERTOUCH, 'data1', 'param'))
    value     = property(*_make_get_set(_constants.CTRL | _constants.PITCHBEND |
                                        _constants.AFTERTOUCH | _constants.POLY_AFTERTOUCH, 'data2', 'value'))
    program   = property(*_make_get_set(_constants.PROGRAM, 'data2', 'program', offset=lambda: _get_config('data_offset')))

    # for backward compatibility
    type_     = property(*_make_get_set(_constants.ANY, 'type'))


def NoteOnEvent(port, channel, note, velocity):
    return MidiEvent(
        _constants.NOTEON,
        _util.port_number(port),
        _util.channel_number(channel),
        _util.note_number(note, False),
        _util.velocity_value(velocity, False)
    )

def NoteOffEvent(port, channel, note, velocity=0):
    return MidiEvent(
        _constants.NOTEOFF,
        _util.port_number(port),
        _util.channel_number(channel),
        _util.note_number(note, False),
        _util.velocity_value(velocity, False)
    )

def CtrlEvent(port, channel, param, value):
    return MidiEvent(
        _constants.CTRL,
        _util.port_number(port),
        _util.channel_number(channel),
        _util.ctrl_number(param),
        _util.ctrl_value(value, False)
    )

def ProgramEvent(port, channel, program):
    return MidiEvent(
        _constants.PROGRAM,
        _util.port_number(port),
        _util.channel_number(channel),
        0,
        _util.program_number(program, False)
    )
