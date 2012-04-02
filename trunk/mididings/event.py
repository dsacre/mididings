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

import mididings.constants as _constants
import mididings.util as _util
import mididings.misc as _misc



def _make_property(type, data, name=None, offset=False):
    if isinstance(data, str) and not offset:
        def getter(self):
            self._check_type_attribute(type, name)
            return getattr(self, data)
        def setter(self, value):
            self._check_type_attribute(type, name)
            setattr(self, data, value)

    elif isinstance(data, str) and offset:
        def getter(self):
            self._check_type_attribute(type, name)
            return _util.offset(getattr(self, data))
        def setter(self, value):
            self._check_type_attribute(type, name)
            setattr(self, data, _util.actual(value))

    return property(getter, setter)


class MidiEvent(_mididings.MidiEvent):
    """
    The main MIDI event class.
    All event data is part of the C++ base class.
    """
    def __init__(self, type=_constants.NONE, port=_util.NoDataOffset(0), channel=_util.NoDataOffset(0), data1=0, data2=0):
        _mididings.MidiEvent.__init__(self)
        self.type = type
        self.port = _util.port_number(port)
        self.channel = _util.channel_number(channel)
        self.data1 = data1
        self.data2 = data2

    def __getinitargs__(self):
        return (self.type, self.port, self.channel, self.data1, self.data2)

    def _check_type_attribute(self, type, name):
        if not self.type & type:
            message = "MidiEvent type '%s' has no attribute '%s'" % (self._type_to_string(), name)
            raise AttributeError(message)

    def _type_to_string(self):
        try:
            return _constants._EVENT_TYPE_NAMES[self.type]
        except KeyError:
            return 'NONE'

    def to_string(self, portnames=[], portname_length=0, max_length=0):
        if len(portnames) > self.port_:
            port = portnames[self.port_]
        else:
            port = str(self.port)

        h = '[%*s, %2d]' % (max(portname_length, 2), port, self.channel)

        if self.type == _constants.NOTEON:
            s = 'Note On:  %3d %3d  (%s)' % (self.note, self.velocity, _util.note_name(self.note))
        elif self.type == _constants.NOTEOFF:
            s = 'Note Off: %3d %3d  (%s)' % (self.note, self.velocity, _util.note_name(self.note))
        elif self.type == _constants.CTRL:
            s = 'Ctrl:     %3d %3d' % (self.ctrl, self.value)
            n = _util.controller_name(self.ctrl)
            if n:
                s += '  (%s)' % n
        elif self.type == _constants.PITCHBEND:
            s = 'Pitchbend:  %5d' % self.value
        elif self.type == _constants.AFTERTOUCH:
            s = 'Aftertouch:   %3d' % self.value
        elif self.type == _constants.POLY_AFTERTOUCH:
            s = 'Poly Aftertouch: %3d %3d  (%s)' % (self.note, self.value, _util.note_name(self.note))
        elif self.type == _constants.PROGRAM:
            s = 'Program:      %3d' % self.program
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
            s = 'SysEx:   %8d  [%s]' % (len(data), hexstring)
        elif self.type == _constants.SYSCM_QFRAME:
            s = 'SysCm QFrame: %3d' % self.data1
        elif self.type == _constants.SYSCM_SONGPOS:
            s = 'SysCm SongPos:%3d %3d' % (self.data1, self.data2)
        elif self.type == _constants.SYSCM_SONGSEL:
            s = 'SysCm SongSel:%3d' % self.data1
        elif self.type == _constants.SYSCM_TUNEREQ:
            s = 'SysCm TuneReq'
        elif self.type == _constants.SYSRT_CLOCK:
            s = 'SysRt Clock'
        elif self.type == _constants.SYSRT_START:
            s = 'SysRt Start'
        elif self.type == _constants.SYSRT_CONTINUE:
            s = 'SysRt Continue'
        elif self.type == _constants.SYSRT_STOP:
            s = 'SysRt Stop'
        elif self.type == _constants.SYSRT_SENSING:
            s = 'SysRt Sensing'
        elif self.type == _constants.SYSRT_RESET:
            s = 'SysRt Reset'
        elif self.type == _constants.DUMMY:
            s = 'Dummy'
        else:
            s = 'None'

        return '%s %s' % (h, s)

    def __repr__(self):
        return 'MidiEvent(%s, %d, %d, %d, %d)' % (self._type_to_string(), self.port, self.channel, self.data1, self.data2)


    # port/channel attributes with data offset
    port      = _make_property(
                    _constants.ANY,
                   'port_',
                    offset=True)
    channel   = _make_property(
                    _constants.ANY,
                    'channel_',
                    offset=True)

    # event-type specific attributes
    note      = _make_property(
                    _constants.NOTE | _constants.POLY_AFTERTOUCH,
                   'data1', 'note')
    velocity  = _make_property(
                    _constants.NOTE,
                    'data2', 'velocity')
    ctrl      = _make_property(
                    _constants.CTRL,
                    'data1', 'ctrl')
    value     = _make_property(
                    _constants.CTRL | _constants.PITCHBEND | _constants.AFTERTOUCH | _constants.POLY_AFTERTOUCH,
                    'data2', 'value')
    program   = _make_property(
                    _constants.PROGRAM,
                    'data2', 'program',
                    offset=True)

    # for backward compatibility
    param     = ctrl


    def _sysex_getter(self):
        self._check_type_attribute(_constants.SYSEX, 'sysex')
        return _util.sysex_to_sequence(self._get_sysex_data())

    def _sysex_setter(self, sysex):
        self._check_type_attribute(_constants.SYSEX, 'sysex')
        self._set_sysex_data(_util.sysex_data(sysex))

    sysex = property(_sysex_getter, _sysex_setter)



def NoteOnEvent(port, channel, note, velocity):
    """
    Create a new note-on event object.
    """
    return MidiEvent(
        _constants.NOTEON,
        port,
        channel,
        _util.note_number(note, False),
        _util.velocity_value(velocity, False)
    )

def NoteOffEvent(port, channel, note, velocity=0):
    """
    Create a new note-off event object.
    """
    return MidiEvent(
        _constants.NOTEOFF,
        port,
        channel,
        _util.note_number(note, False),
        _util.velocity_value(velocity, False)
    )

def CtrlEvent(port, channel, ctrl, value):
    """
    Create a new control change event object.
    """
    return MidiEvent(
        _constants.CTRL,
        port,
        channel,
        _util.ctrl_number(ctrl),
        _util.ctrl_value(value, False)
    )

def PitchbendEvent(port, channel, value):
    """
    Create a new pitch bend event object.
    """
    return MidiEvent(
        _constants.PITCHBEND,
        port,
        channel,
        0,
        value
    )

def AftertouchEvent(port, channel, value):
    """
    Create a new aftertouch event object.
    """
    return MidiEvent(
        _constants.AFTERTOUCH,
        port,
        channel,
        value
    )

def ProgramEvent(port, channel, program):
    """
    Create a new program change event object.
    """
    return MidiEvent(
        _constants.PROGRAM,
        port,
        channel,
        0,
        _util.actual(_util.program_number(program, False))
    )

def SysExEvent(port, sysex):
    """
    Create a new sysex event object.
    """
    ev = MidiEvent(_constants.SYSEX, port)
    ev.sysex = sysex
    return ev
