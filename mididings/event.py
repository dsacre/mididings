# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import _mididings
import main as _main
import util as _util


NONE      = 0
NOTEON    = 1 << 0
NOTEOFF   = 1 << 1
NOTE      = NOTEON | NOTEOFF
CTRL      = 1 << 2
PITCHBEND = 1 << 3
PROGRAM   = 1 << 4
ANY       = ~0


EVENT_PORT      = -1
EVENT_CHANNEL   = -2
# generic
EVENT_DATA1     = -3
EVENT_DATA2     = -4
# note
EVENT_NOTE      = -3
EVENT_VELOCITY  = -4
# controller
EVENT_PARAM     = -3
EVENT_VALUE     = -4
# program change
EVENT_PROGRAM   = -4


class MidiEvent(_mididings.MidiEvent):
    def __init__(self, type_=0, port_=0, channel_=0, data1=0, data2=0):
        _mididings.MidiEvent.__init__(self)
        self.type_ = type_
        self.port_ = port_
        self.channel_ = channel_
        self.data1 = data1
        self.data2 = data2

    def __str__(self):
        return self.to_string()

    def to_string(self, portnames=[], portname_length=0):
        if len(portnames) > self.port_:
            port = portnames[self.port_]
        else:
            port = str(self.port)

        channel = self.channel

        if self.type_ == NOTEON:
            s = 'Note on:  %3d %3d  (%s)' % (self.note, self.velocity, _util.note_name(self.note))
        elif self.type_ == NOTEOFF:
            s = 'Note off: %3d %3d  (%s)' % (self.note, self.velocity, _util.note_name(self.note))
        elif self.type_ == CTRL:
            s = 'Control:  %3d %3d' % (self.param, self.value)
            n = _util.controller_name(self.param)
            if n: s += '  (%s)' % n
        elif self.type_ == PITCHBEND:
            s = 'Pitch bend: %+5d' % self.value
        elif self.type_ == PROGRAM:
            s = 'Program:      %3d' % self.program
        else:
            s = 'None'

        return '[%*s, %2d] %s' % (portname_length, port, channel, s)

    def make_get_set(type_, data, offset=lambda: 0):
        def getter(self):
            if not self.type_ & type_ and not type_ == ANY:
                print "midi event attribute error"
            return getattr(self, data) + offset()

        def setter(self, value):
            if not self.type_ & type_ and not type_ == ANY:
                print "midi event attribute error"
            setattr(self, data, value - offset())

        return (getter, setter)

    port      = property(*make_get_set(ANY, 'port_', lambda: _main._config['data_offset']))
    channel   = property(*make_get_set(ANY, 'channel_', lambda: _main._config['data_offset']))

    note      = property(*make_get_set(NOTE, 'data1'))
    velocity  = property(*make_get_set(NOTE, 'data2'))
    param     = property(*make_get_set(CTRL, 'data1'))
    value     = property(*make_get_set(CTRL | PITCHBEND, 'data2'))
    program   = property(*make_get_set(PROGRAM, 'data2', lambda: _main._config['data_offset']))
