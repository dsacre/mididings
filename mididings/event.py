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
TYPE_CONTROLLER = 1 << 2
TYPE_PITCHBEND  = 1 << 3
TYPE_PGMCHANGE  = 1 << 4
TYPE_ANY        = ~0


PORT      = -1
CHANNEL   = -2
# generic
DATA1     = -3
DATA2     = -4
# note
NOTE      = -3
VELOCITY  = -4
# controller
PARAM     = -3
VALUE     = -4
# program change
PROGRAM   = -4


class _MidiEventEx(_mididings.MidiEvent):
    def make_get_set(typ, data, offset=None):
        def getter(self):
            if not self.type & typ:
                print "midi event attribute error"
            off = offset() if offset else 0
            return getattr(self, data) + off

        def setter(self, value):
            if not self.type & typ:
                print "midi event attribute error"
            off = offset() if offset else 0
            setattr(self, data, value - off)

        return (getter, setter)

    port      = property(*make_get_set(TYPE_ANY, 'port_', _main._port_offset))
    channel   = property(*make_get_set(TYPE_ANY, 'channel_', _main._channel_offset))

    note      = property(*make_get_set(TYPE_NOTE, 'data1'))
    velocity  = property(*make_get_set(TYPE_NOTE, 'data2'))
    param     = property(*make_get_set(TYPE_CONTROLLER, 'data1'))
    value     = property(*make_get_set(TYPE_CONTROLLER | TYPE_PITCHBEND, 'data2'))
    program   = property(*make_get_set(TYPE_PGMCHANGE, 'data2', _main._program_offset))
