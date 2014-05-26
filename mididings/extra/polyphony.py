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
from mididings.extra.per_channel import PerChannel as _PerChannel


class _LimitPolyphony(object):
    def __init__(self, max_polyphony, remove_oldest):
        self.max_polyphony = max_polyphony
        self.remove_oldest = remove_oldest
        self.notes = []

    def __call__(self, ev):
        if ev.type == _m.NOTEON:
            if len(self.notes) < self.max_polyphony:
                # polyphony not exceeded, allow note
                self.notes.append(ev.note)
                return ev
            else:
                if self.remove_oldest:
                    # allow note, but send note-off for oldest first
                    noteoff = _event.NoteOffEvent(ev.port, ev.channel,
                                                  self.notes[0], 0)
                    self.notes = self.notes[1:]
                    self.notes.append(ev.note)
                    return [noteoff, ev]
                else:
                    # discard note
                    return None

        elif ev.type == _m.NOTEOFF:
            if ev.note in self.notes:
                self.notes.remove(ev.note)
                return ev
            else:
                return None


class _MakeMonophonic(object):
    def __init__(self):
        self.notes = []

    def __call__(self, ev):
        if ev.type == _m.NOTEON:
            if len(self.notes):
                # send note off for previous note, and note on for current note
                noteoff = _event.NoteOffEvent(ev.port, ev.channel,
                                              self.notes[-1][0], 0)
                self.notes.append((ev.note, ev.velocity))
                return [noteoff, ev]
            else:
                # send note on for current note
                self.notes.append((ev.note, ev.velocity))
                return ev

        elif ev.type == _m.NOTEOFF:
            if len(self.notes) and ev.note == self.notes[-1][0]:
                # note off for currently sounding note
                if len(self.notes) == 1:
                    # only one note left, send note off
                    r = ev
                else:
                    # send note off, and retrigger previous note
                    noteon = _event.NoteOnEvent(ev.port, ev.channel,
                                        self.notes[-2][0], self.notes[-2][1])
                    r = [ev, noteon]
            else:
                # note isn't sounding, discard note off
                r = None

            # remove released note from list
            self.notes = [x for x in self.notes if x[0] != ev.note]

            return r



def LimitPolyphony(max_polyphony, remove_oldest=True):
    """
    Limit the "MIDI polyphony".

    :param max_polyphony:
        The maximum number of simultaneous notes.

    :param remove_oldest:
        If true, the oldest notes will be stopped when the maximum polyphony
        is exceeded.
        If false, no new notes are accepted while *max_polyphony* notes
        are already held.

    Note that the actual polyphony of a connected synthesizer can still be
    higher than the limit set here, e.g. due to a long release phase.
    """
    return (_m.Filter(_m.NOTE) %
        _m.Process(_PerChannel(
            lambda: _LimitPolyphony(max_polyphony, remove_oldest))))


def MakeMonophonic():
    """
    Make the MIDI signal monophonic, i.e. only one note can be played at
    any given time.
    When one note is released while another is still held (but silent),
    the previous one will be retriggered.
    """
    return (_m.Filter(_m.NOTE) %
        _m.Process(_PerChannel(_MakeMonophonic)))
