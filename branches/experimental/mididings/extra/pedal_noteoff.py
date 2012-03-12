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


class _SustainToNoteoff(object):
    def __init__(self, ctrl):
        self.ctrl = ctrl
        self.pedal = False
        self.notes = set()

    def __call__(self, ev):
        if ev.type == CTRL and ev.ctrl == self.ctrl:
            self.pedal = (ev.value >= 64)
            if self.pedal:
                # pedal pressed
                return None
            else:
                # pedal released, send note offs for all sustained notes
                r = [_event.NoteOffEvent(ev.port, ev.channel, x, 0) for x in self.notes]
                self.notes.clear()
                return r
        elif ev.type == NOTEON and self.pedal:
            # note on while pedal is held
            return ev
        elif ev.type == NOTEOFF and self.pedal:
            # delay note off until pedal released
            self.notes.add(ev.note)
            return None
        else:
            # everything else: return as is
            return ev


class _SostenutoToNoteoff(object):
    def __init__(self, ctrl):
        self.ctrl = ctrl
        self.pedal = False
        self.held_notes = set()
        self.sustained_notes = set()

    def __call__(self, ev):
        if ev.type == CTRL and ev.ctrl == self.ctrl:
            self.pedal = (ev.value >= 64)
            if self.pedal:
                # pedal pressed, remember currently held notes
                self.sustained_notes |= self.held_notes
                return None
            else:
                # pedal released, send note offs for all sustained notes
                r = [_event.NoteOffEvent(ev.port, ev.channel, x, 0) for x in self.sustained_notes if x not in self.held_notes]
                self.sustained_notes.clear()
                return r
        elif ev.type == NOTEON:
            self.held_notes.add(ev.note)
            return ev
        elif ev.type == NOTEOFF:
            self.held_notes.discard(ev.note)

            # send note off only if the note is not currently being sustained
            if ev.note not in self.sustained_notes:
                return ev
            else:
                return None
        else:
            # everything else: return as is
            return ev


def PedalToNoteoff(ctrl=64, sostenuto=False):
    if sostenuto:
        proc = Process(PerChannel(lambda: _SostenutoToNoteoff(ctrl)))
    else:
        proc = Process(PerChannel(lambda: _SustainToNoteoff(ctrl)))

    return (Filter(NOTE) | CtrlFilter(ctrl)) % proc
