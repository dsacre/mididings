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
import mididings.engine as _engine


class _VoiceFilter(object):
    def __init__(self, voice, time, retrigger):
        self.voice = voice
        self.time = time
        self.retrigger = retrigger
        self.notes = {}                     # all notes currently being played
        self.current_note = None            # note number this voice is playing
        self.diverted = False               # whether we had to fall back to a different voice

    def __call__(self, ev):
        t = _engine.time()

        if ev.type == NOTEON:
            # store new note, its velocity, and its time
            self.notes[ev.note] = (ev.velocity, t)
        elif ev.type == NOTEOFF:
            # delete released note
            del self.notes[ev.note]

        sorted_notes = sorted(self.notes.keys())

        if len(sorted_notes):
            try:
                n = sorted_notes[self.voice]
                d = False
            except IndexError:
                # use the next best note: lowest for negative index, otherwise highest
                n = sorted_notes[0 if self.voice < 0 else -1]
                d = True
        else:
            n = None
            d = False

        dt = (t - self.notes[self.current_note][1]) if self.current_note in self.notes else 0.0

        # change current note if...
        if (n != self.current_note                          # note number changed and...
            and (self.retrigger                             # we're always retriggering notes...
                 or self.voice in (0, -1)                   # lowest/heighest voice are a bit of a special case...
                 or self.current_note not in self.notes     # current note is no longer held...
                 or (ev.type == NOTEON and dt < self.time)  # our previous note is very recent...
                 or self.diverted and not d)):              # or the new note is "better" than previous one
            # yield note-off for previous note (if any)
            if self.current_note:
                yield _event.NoteOffEvent(ev.port, ev.channel, self.current_note, 0)
                self.current_note = None

            dt = (t - self.notes[n][1]) if n in self.notes else 0.0

            # yield note-on for new note (if any)
            if n is not None and (ev.note == n              # if this is the note being played right now...
                              or self.retrigger             # we're retriggering notes whenever a key is pressed or released...
                              or dt < self.time):           # or our previous note is very recent
                yield _event.NoteOnEvent(ev.port, ev.channel, n, self.notes[n][0])
                self.current_note = n
                self.diverted = d


def VoiceFilter(voice='highest', time=0.1, retrigger=False):
    if voice == 'highest':
        voice = -1
    elif voice == 'lowest':
        voice = 0

    return Filter(NOTE) % Process(PerChannel(
        lambda: _VoiceFilter(voice, time, retrigger))
    )


def VoiceSplit(patches, fallback='highest', time=0.1, retrigger=False):
    vf = lambda n: VoiceFilter(n, time, retrigger)

    if fallback == 'lowest':
        return Fork(
            [ vf( 0) >> patches[ 0] ] +
            [ vf( n) >> patches[ n] for n in range(-len(patches) + 1, 0) ]
        )
    else: # highest
        return Fork(
            [ vf( n) >> patches[ n] for n in range(len(patches) - 1) ] +
            [ vf(-1) >> patches[-1] ]
        )
