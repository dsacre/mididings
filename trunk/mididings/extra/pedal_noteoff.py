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

from mididings import *
from mididings.extra import CallPerChannel


class _PedalToNoteoff:
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
                # pedal released
                r = [NoteoffEvent(ev.port, ev.channel, x, 0) for x in self.notes]
                self.notes = []
                return r
        elif ev.type_ == NOTEON and self.pedal:
            try:
                # remove note if key is pressed again
                self.notes.remove(ev.note)
            except ValueError:
                pass
            return ev
        elif ev.type_ == NOTEOFF and self.pedal:
            # delay noteoff until pedal released
            self.notes.append(ev.note)
            return None

        # everything else: return as is
        return ev


def PedalToNoteoff(ctrl=64):
    return Filter(NOTE | CTRL) % (CtrlFilter(ctrl) %
        CallPerChannel(lambda: _PedalToNoteoff(ctrl))
    )
