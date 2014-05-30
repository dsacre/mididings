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
import mididings.engine as _engine
from mididings.extra.per_channel import PerChannel as _PerChannel


class _VoiceFilter(object):
    def __init__(self, voice, time, retrigger):
        self.voice = voice
        self.time = time
        self.retrigger = retrigger

        # all notes currently being played
        self.notes = {}
        # note number this voice is playing
        self.current_note = None
        # if we had to fall back to a different voice
        self.diverted = False

    def __call__(self, ev):
        t = _engine.time()

        if ev.type == _m.NOTEON:
            # store new note, its velocity, and its time
            self.notes[ev.note] = (ev.velocity, t)
        elif ev.type == _m.NOTEOFF:
            # delete released note
            try:
                del self.notes[ev.note]
            except KeyError:
                # ignore unmatched note-offs (just in case...)
                pass

        sorted_notes = sorted(self.notes.keys())

        if len(sorted_notes):
            try:
                n = sorted_notes[self.voice]
                d = False
            except IndexError:
                # use the next best note:
                # lowest for negative index, otherwise highest
                n = sorted_notes[0 if self.voice < 0 else -1]
                d = True
        else:
            n = None
            d = False

        dt = ((t - self.notes[self.current_note][1])
                if self.current_note in self.notes else 0.0)

        # change current note if...
        if (
            # note number changed and...
            n != self.current_note and (
                # we're always retriggering notes
                self.retrigger or
                # lowest/heighest voice are a bit of a special case
                self.voice in (0, -1) or
                # current note is no longer held
                self.current_note not in self.notes or
                # our previous note is very recent
                (ev.type == _m.NOTEON and dt < self.time) or
                # the new note is "better" than previous one
                self.diverted and not d
        )):
            # yield note-off for previous note (if any)
            if self.current_note:
                yield _event.NoteOffEvent(
                            ev.port, ev.channel, self.current_note, 0)
                self.current_note = None

            dt = (t - self.notes[n][1]) if n in self.notes else 0.0

            # yield note-on for new note (if any)
            if n is not None and (
                # this is the note being played right now
                ev.note == n or
                # we're retriggering whenever a key is pressed or released
                self.retrigger or
                # our previous note is very recent
                dt < self.time
            ):
                yield _event.NoteOnEvent(
                            ev.port, ev.channel, n, self.notes[n][0])
                self.current_note = n
                self.diverted = d


def VoiceFilter(voice='highest', time=0.1, retrigger=False):
    """
     Filter individual voices from a chord.

    :param voice:
        The voice to be filtered.

        This can be ``'highest'``, ``'lowest'``, or an integer index
        (positive or negative, the same way Python lists are indexed,
        with 0 being the lowest voice and -1 the highest).

    :param time:
        The period in seconds for which a newly played note may still be
        unassigned from the selected voice, when additional notes are played.

    :param retrigger:
        If true, a new note-on event will be sent when a note is reassigned
        to the selected voice as a result of another note being released.
    """
    if voice == 'highest':
        voice = -1
    elif voice == 'lowest':
        voice = 0

    return _m.Filter(_m.NOTE) % _m.Process(_PerChannel(
        lambda: _VoiceFilter(voice, time, retrigger))
    )


def VoiceSplit(patches, fallback='highest', time=0.1, retrigger=False):
    """
    Create multiple :func:`VoiceFilter()` units to route each voice to
    a different instrument.

    :param patches:
        A list of patches, one for each voice.

    :param fallback:
        Which note to double when the number of notes played is less than
        the number of voices. Can be ``'highest'`` or ``'lowest'``.

    Regardless of the number of voices specified, the lowest and highest
    note played will always be routed to the first and last patch in
    the list, respectively.
    """
    vf = lambda n: VoiceFilter(n, time, retrigger)

    if fallback == 'lowest':
        return _m.Fork(
            [ vf( 0) >> patches[ 0] ] +
            [ vf( n) >> patches[ n] for n in range(-len(patches) + 1, 0) ]
        )
    else: # highest
        return _m.Fork(
            [ vf( n) >> patches[ n] for n in range(len(patches) - 1) ] +
            [ vf(-1) >> patches[-1] ]
        )
