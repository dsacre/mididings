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

from mididings import *
from mididings.extra import PerChannel
import mididings.event as _event


class _LimitPolyphony(object):
    def __init__(self, max_polyphony, remove_oldest):
        self.max_polyphony = max_polyphony
        self.remove_oldest = remove_oldest
        self.notes = []

    def __call__(self, ev):
        if ev.type == NOTEON:
            if len(self.notes) < self.max_polyphony:
                # polyphony not exceeded, allow note
                self.notes.append(ev.note)
                return ev
            else:
                if self.remove_oldest:
                    # allow note, but send note-off for oldest first
                    noteoff = _event.NoteOffEvent(ev.port, ev.channel, self.notes[0], 0)
                    self.notes = self.notes[1:]
                    self.notes.append(ev.note)
                    return [noteoff, ev]
                else:
                    # discard note
                    return None

        elif ev.type == NOTEOFF:
            if ev.note in self.notes:
                self.notes.remove(ev.note)
                return ev
            else:
                return None


class _MakeMonophonic(object):
    def __init__(self):
        self.notes = []

    def __call__(self, ev):
        if ev.type == NOTEON:
            if len(self.notes):
                # send note off for previous note, and note on for current note
                noteoff = _event.NoteOffEvent(ev.port, ev.channel, self.notes[-1][0], 0)
                self.notes.append((ev.note, ev.velocity))
                return [noteoff, ev]
            else:
                # send note on for current note
                self.notes.append((ev.note, ev.velocity))
                return ev

        elif ev.type == NOTEOFF:
            if len(self.notes) and ev.note == self.notes[-1][0]:
                # note off for currently sounding note
                if len(self.notes) == 1:
                    # only one note left, send note off
                    r = ev
                else:
                    # send note off, and retrigger previous note
                    noteon = _event.NoteOnEvent(ev.port, ev.channel, self.notes[-2][0], self.notes[-2][1])
                    r = [ev, noteon]
            else:
                # note isn't sounding, discard note off
                r = None

            # remove released note from list
            self.notes = [x for x in self.notes if x[0] != ev.note]

            return r



def LimitPolyphony(max_polyphony, remove_oldest=True):
    return Filter(NOTE) % Process(PerChannel(lambda: _LimitPolyphony(max_polyphony, remove_oldest)))


def MakeMonophonic():
    return Filter(NOTE) % Process(PerChannel(_MakeMonophonic))
