# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2014  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import mididings as _m
import mididings.event as _event
import mididings.util as _util
from mididings.extra.per_channel import PerChannel as _PerChannel


class _LatchNotes(object):
    def __init__(self, polyphonic, reset):
        self.polyphonic = polyphonic
        self.reset = _util.note_number(reset) if reset is not None else None
        self.notes = []

    def __call__(self, ev):
        if ev.type == _m.NOTEON:
            if ev.note == self.reset:
                # reset all notes
                r = [_event.NoteOffEvent(ev.port, ev.channel, x, 0) for x in self.notes]
                self.notes = []
                return r

            if self.polyphonic:
                if ev.note not in self.notes:
                    # turn note on
                    self.notes.append(ev.note)
                    return ev
                else:
                    # turn note off
                    self.notes.remove(ev.note)
                    return _event.NoteOffEvent(ev.port, ev.channel, ev.note, 0)
            else:
                # turn off previous note, play new note
                r = [_event.NoteOffEvent(ev.port, ev.channel, self.notes[0], 0)] if len(self.notes) else []
                self.notes = [ev.note]
                return r + [ev]

        elif ev.type == _m.NOTEOFF:
            # ignore all note-off events
            return None


def LatchNotes(polyphonic=False, reset=None):
    return (_m.Filter(_m.NOTE) %
                _m.Process(_PerChannel(lambda: _LatchNotes(polyphonic, reset))))
