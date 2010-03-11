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

from mididings import *
from mididings.extra import PerChannel
import mididings.event as _event

import time as _time


class _VoiceFilter(object):
    def __init__(self, voice, time, retrigger):
        self.voice = voice
        self.time = time
        self.retrigger = retrigger
        self.notes = {}
        self.current_voice = None

    def __call__(self, ev):
        prev_voice = self.current_voice

        if ev.type == NOTEON:
            # store new note, its velocity, and its time
            self.notes[ev.note] = (ev.velocity, _time.time())
        elif ev.type == NOTEOFF:
            # delete released note
            del self.notes[ev.note]

        # update note number for this voice
        try:
            self.current_voice = sorted(self.notes.keys())[self.voice]
        except IndexError:
            self.current_voice = None

        if self.current_voice != prev_voice:
            # yield note-off for previous note
            if prev_voice:
                yield _event.NoteOffEvent(ev.port, ev.channel, prev_voice, 0)
            # yield note-on for new note
            if self.current_voice and (ev.note == self.current_voice or
                                       self.retrigger or
                                      _time.time() < self.notes[self.current_voice][1] + self.time):
                yield _event.NoteOnEvent(ev.port, ev.channel, self.current_voice, self.notes[self.current_voice][0])


def VoiceFilter(voice='highest', time=0.2, retrigger=False):
    if voice == 'highest':
        voice = -1
    elif voice == 'lowest':
        voice = 0
    return Filter(NOTE) % Process(PerChannel(lambda: _VoiceFilter(voice, time, retrigger)))
