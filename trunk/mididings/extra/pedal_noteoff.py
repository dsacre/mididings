# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2009  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

from mididings import *
from mididings.extra import PerChannel


class _SustainToNoteoff(object):
    def __init__(self, ctrl):
        self.ctrl = ctrl
        self.pedal = False
        self.notes = []

    def __call__(self, ev):
        if ev.type_ == CTRL and ev.param == self.ctrl:
            self.pedal = (ev.value >= 64)
            if self.pedal:
                # pedal pressed
                return None
            else:
                # pedal released, send note offs for all stored notes
                r = [NoteoffEvent(ev.port, ev.channel, x, 0) for x in self.notes]
                self.notes = []
                return r
        elif ev.type_ == NOTEON and self.pedal:
            # note on while pedal is held
            return ev
        elif ev.type_ == NOTEOFF and self.pedal:
            # delay note off until pedal released
            self.notes.append(ev.note)
            return None
        else:
            # everything else: return as is
            return ev


class _SostenutoToNoteoff(object):
    def __init__(self, ctrl):
        self.ctrl = ctrl
        self.pedal = False
        self.held_notes = []
        self.sustained_notes = []

    def __call__(self, ev):
        if ev.type_ == CTRL and ev.param == self.ctrl:
            self.pedal = (ev.value >= 64)
            if self.pedal:
                # pedal pressed, remember currently held notes
                if not self.sustained_notes:
                    self.sustained_notes = self.held_notes
                    self.held_notes = []
                return None
            else:
                # pedal released, send note offs for all stored notes
                r = [NoteoffEvent(ev.port, ev.channel, x, 0) for x in self.sustained_notes]
                self.sustained_notes = []
                return r
        elif ev.type_ == NOTEON:
            self.held_notes.append(ev.note)
            return ev
        elif ev.type_ == NOTEOFF:
            # send note off only if the note is currently being held.
            # notes can be both in held_notes and sustained_notes, so checking for
            # ev.note in self.sustained_notes does not do the right thing!
            if ev.note in self.held_notes:
                self.held_notes.remove(ev.note)
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

    return Filter(NOTE | CTRL) % (CtrlFilter(ctrl) % proc)
