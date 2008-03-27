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


TYPE_NONE       = 0
TYPE_NOTEON     = 1 << 0
TYPE_NOTEOFF    = 1 << 1
TYPE_NOTE       = TYPE_NOTEON | TYPE_NOTEOFF
TYPE_CTRL       = 1 << 2
TYPE_PITCHBEND  = 1 << 3
TYPE_PROGRAM    = 1 << 4
TYPE_ANY        = ~0


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
    def __init__(self, type_=TYPE_NONE, port=-1, channel=-1, data1=-1, data2=-1):
        _mididings.MidiEvent.__init__(self)
        self.type_ = type_
        self.port_ = port - _main._data_offset() if port >= 0 else 0
        self.channel_ = channel - _main._data_offset() if channel >= 0 else 0
        if data1 >= 0 and data2 >= 0:
            if type_ == TYPE_PROGRAM:
                self.data1 = 0
                self.program = data2
            else:
                self.data1 = data1
                self.data2 = data2
        else:
            self.data1 = 0
            self.data2 = 0

    def make_get_set(type_, data, offset=None):
        def getter(self):
            if not self.type_ & type_ and not type_ == TYPE_ANY:
                print "midi event attribute error"
            off = offset() if offset else 0
            return getattr(self, data) + off

        def setter(self, value):
            if not self.type_ & type_ and not type_ == TYPE_ANY:
                print "midi event attribute error"
            off = offset() if offset else 0
            setattr(self, data, value - off)

        return (getter, setter)

    port      = property(*make_get_set(TYPE_ANY, 'port_', _main._data_offset))
    channel   = property(*make_get_set(TYPE_ANY, 'channel_', _main._data_offset))

    note      = property(*make_get_set(TYPE_NOTE, 'data1'))
    velocity  = property(*make_get_set(TYPE_NOTE, 'data2'))
    param     = property(*make_get_set(TYPE_CTRL, 'data1'))
    value     = property(*make_get_set(TYPE_CTRL | TYPE_PITCHBEND, 'data2'))
    program   = property(*make_get_set(TYPE_PROGRAM, 'data2', _main._data_offset))

