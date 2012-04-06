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
import mididings.arguments as _arguments
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
    @_arguments.accept(None, _constants._EventType, _util.port_number, _util.channel_number,
                       int, int, _arguments.nullable(_util.sysex_data))
    def __init__(self, type, port=_util.NoDataOffset(0), channel=_util.NoDataOffset(0), data1=0, data2=0, sysex=None):
        _mididings.MidiEvent.__init__(self)
        self.type = type
        self.port = port
        self.channel = channel
        self.data1 = data1
        self.data2 = data2
        if sysex is not None:
            self.sysex_ = sysex

    def __getinitargs__(self):
        self._finalize()
        return (self.type, self.port, self.channel, self.data1, self.data2,
                self.sysex if self.type == _constants.SYSEX else None)

    def _check_type_attribute(self, type, name):
        if not self.type & type:
            message = "MidiEvent type '%s' has no attribute '%s'" % (self._type_to_string(), name)
            raise AttributeError(message)

    def _type_to_string(self):
        try:
            return _constants._EVENT_TYPES[self.type].name
        except KeyError:
            return 'NONE'

    def _sysex_to_hex(self, max_length):
        data = self.sysex
        if max_length:
            m = max(0, max_length // 3)
            if len(data) > m:
                return '%s ...' % _misc.sequence_to_hex(data[:m])
        return _misc.sequence_to_hex(data)

    _to_string_mapping = {
        _constants.NOTEON:          lambda self: 'Note On:  %3d %3d  (%s)' % (self.note, self.velocity, _util.note_name(self.note)),
        _constants.NOTEOFF:         lambda self: 'Note Off: %3d %3d  (%s)' % (self.note, self.velocity, _util.note_name(self.note)),
        _constants.CTRL:            lambda self: 'Ctrl:     %3d %3d' % (self.ctrl, self.value) +
                                                    ('  (%s)' % _util.controller_name(self.ctrl) if _util.controller_name(self.ctrl) else ''),
        _constants.PITCHBEND:       lambda self: 'Pitchbend:  %5d' % self.value,
        _constants.AFTERTOUCH:      lambda self: 'Aftertouch:   %3d' % self.value,
        _constants.POLY_AFTERTOUCH: lambda self: 'Poly Aftertouch: %3d %3d  (%s)' % (self.note, self.value, _util.note_name(self.note)),
        _constants.PROGRAM:         lambda self: 'Program:      %3d' % self.program,
        _constants.SYSCM_QFRAME:    lambda self: 'SysCm QFrame: %3d' % self.data1,
        _constants.SYSCM_SONGPOS:   lambda self: 'SysCm SongPos:%3d %3d' % (self.data1, self.data2),
        _constants.SYSCM_SONGSEL:   lambda self: 'SysCm SongSel:%3d' % self.data1,
        _constants.SYSCM_TUNEREQ:   lambda self: 'SysCm TuneReq',
        _constants.SYSRT_CLOCK:     lambda self: 'SysRt Clock',
        _constants.SYSRT_START:     lambda self: 'SysRt Start',
        _constants.SYSRT_CONTINUE:  lambda self: 'SysRt Continue',
        _constants.SYSRT_STOP:      lambda self: 'SysRt Stop',
        _constants.SYSRT_SENSING:   lambda self: 'SysRt Sensing',
        _constants.SYSRT_RESET:     lambda self: 'SysRt Reset',
        _constants.DUMMY:           lambda self: 'Dummy',
    }

    _repr_mapping = {
        _constants.NOTEON:          lambda self: 'NoteOnEvent(port=%d, channel=%d, note=%d, velocity=%d)' % (self.port, self.channel, self.note, self.velocity),
        _constants.NOTEOFF:         lambda self: 'NoteOffEvent(port=%d, channel=%d, note=%d, velocity=%d)' % (self.port, self.channel, self.note, self.velocity),
        _constants.CTRL:            lambda self: 'CtrlEvent(port=%d, channel=%d, ctrl=%d, value=%d)' % (self.port, self.channel, self.ctrl, self.value),
        _constants.PITCHBEND:       lambda self: 'PitchbendEvent(port=%d, channel=%d, value=%d)' % (self.port, self.channel, self.value),
        _constants.AFTERTOUCH:      lambda self: 'AftertouchEvent(port=%d, channel=%d, value=%d)' % (self.port, self.channel, self.value),
        _constants.PROGRAM:         lambda self: 'ProgramEvent(port=%d, channel=%d, program=%d)' % (self.port, self.channel, self.program),
        _constants.SYSEX:           lambda self: 'SysExEvent(port=%d, sysex=%r)' % (self.port, _misc.bytestring(self._get_sysex())),
    }

    def to_string(self, portnames=[], portname_length=0, max_length=0):
        if len(portnames) > self.port_:
            port = portnames[self.port_]
        else:
            port = str(self.port)

        header = '[%*s, %2d]' % (max(portname_length, 2), port, self.channel)

        if self.type_ == _constants.SYSEX:
            maxsysex = (max_length - len(header) - 25) if max_length else 0
            sysexstr = self._sysex_to_hex(maxsysex)
            desc = 'SysEx:   %8d  [%s]' % (len(self.sysex), sysexstr)
        else:
            desc = MidiEvent._to_string_mapping.get(
                self.type_,
                lambda self: 'None'
            )(self)

        return '%s %s' % (header, desc)

    def __repr__(self):
        return MidiEvent._repr_mapping.get(
            self.type_,
            lambda self: 'MidiEvent(%s, %d, %d, %d, %d)' % (self._type_to_string(), self.port, self.channel, self.data1, self.data2)
        )(self)


    def __eq__(self, other):
        if not isinstance(other, MidiEvent):
            return NotImplemented
        self._finalize()
        other._finalize()
        return _mididings.MidiEvent.__eq__(self, other)

    def __ne__(self, other):
        if not isinstance(other, MidiEvent):
            return NotImplemented
        self._finalize()
        other._finalize()
        return _mididings.MidiEvent.__ne__(self, other)

    def __hash__(self):
        self._finalize()
        return _mididings.MidiEvent.__hash__(self)

    def _finalize(self):
        if hasattr(self, '_sysex_tmp'):
            self.sysex_ = _util.sysex_data(self._sysex_tmp)
            delattr(self, '_sysex_tmp')


    def _type_getter(self):
        # return an event type constant, rather than the plain int stored in
        # self.type_
        return _constants._EVENT_TYPES[self.type_]

    def _type_setter(self, type):
        self.type_ = type

    def _get_sysex(self):
        if hasattr(self, '_sysex_tmp'):
            return self._sysex_tmp
        else:
            return _util.sysex_to_sequence(self.sysex_)

    def _sysex_getter(self):
        self._check_type_attribute(_constants.SYSEX, 'sysex')
        self._sysex_tmp = self._get_sysex()
        return self._sysex_tmp

    def _sysex_setter(self, sysex):
        self._check_type_attribute(_constants.SYSEX, 'sysex')
        self._sysex_tmp = _util.sysex_to_sequence(sysex)


    type = property(_type_getter, _type_setter)

    # port/channel attributes with data offset
    port      = _make_property(_constants.ANY, 'port_', offset=True)
    channel   = _make_property(_constants.ANY, 'channel_', offset=True)

    # event-type specific attributes
    note      = _make_property(_constants.NOTE | _constants.POLY_AFTERTOUCH, 'data1', 'note')
    velocity  = _make_property(_constants.NOTE, 'data2', 'velocity')
    ctrl      = _make_property(_constants.CTRL, 'data1', 'ctrl')
    value     = _make_property(_constants.CTRL | _constants.PITCHBEND |
                               _constants.AFTERTOUCH | _constants.POLY_AFTERTOUCH,
                               'data2', 'value')
    program   = _make_property(_constants.PROGRAM, 'data2', 'program', offset=True)

    sysex = property(_sysex_getter, _sysex_setter)



@_arguments.accept(_util.port_number, _util.channel_number, _util.note_number, _util.velocity_value)
def NoteOnEvent(port, channel, note, velocity):
    """
    Create a new note-on event object.
    """
    return MidiEvent(_constants.NOTEON, port, channel, note, velocity)

@_arguments.accept(_util.port_number, _util.channel_number, _util.note_number, _util.velocity_value)
def NoteOffEvent(port, channel, note, velocity=0):
    """
    Create a new note-off event object.
    """
    return MidiEvent(_constants.NOTEOFF, port, channel, note, velocity)

@_arguments.accept(_util.port_number, _util.channel_number, _util.ctrl_number, _util.ctrl_value)
def CtrlEvent(port, channel, ctrl, value):
    """
    Create a new control change event object.
    """
    return MidiEvent(_constants.CTRL, port, channel, ctrl, value)

@_arguments.accept(_util.port_number, _util.channel_number, int)
def PitchbendEvent(port, channel, value):
    """
    Create a new pitch bend event object.
    """
    return MidiEvent(_constants.PITCHBEND, port, channel, 0, value)

@_arguments.accept(_util.port_number, _util.channel_number, int)
def AftertouchEvent(port, channel, value):
    """
    Create a new aftertouch event object.
    """
    return MidiEvent(_constants.AFTERTOUCH, port, channel, 0, value)

@_arguments.accept(_util.port_number, _util.channel_number, _util.program_number)
def ProgramEvent(port, channel, program):
    """
    Create a new program change event object.
    """
    return MidiEvent(_constants.PROGRAM, port, channel, 0, _util.actual(program))

@_arguments.accept(_util.port_number, _util.sysex_data)
def SysExEvent(port, sysex):
    """
    Create a new sysex event object.
    """
    return MidiEvent(_constants.SYSEX, port, sysex=sysex)
