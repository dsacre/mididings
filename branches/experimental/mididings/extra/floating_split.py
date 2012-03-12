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
import mididings.util as _util
import mididings.engine as _engine


class _FloatingKeySplitAnalyze(object):
    def __init__(self, threshold_lower, threshold_upper, hold_time, margin_lower, margin_upper):
        self.threshold_lower = _util.note_number(threshold_lower)
        self.threshold_upper = _util.note_number(threshold_upper)
        self.margin_lower = margin_lower
        self.margin_upper = margin_upper
        self.hold_time = hold_time

        self.notes_lower = {}
        self.notes_upper = {}

    def __call__(self, ev):
        now = _engine.time()

        # remove old notes from the lists if hold_time has elapsed
        for k, t in list(self.notes_lower.items()):
            if t and t < now - self.hold_time:
                del self.notes_lower[k]
        for k, t in list(self.notes_upper.items()):
            if t and t < now - self.hold_time:
                del self.notes_upper[k]

        # calculate new threshold
        lower = max(self.notes_lower) if len(self.notes_lower) else self.threshold_lower - self.margin_lower
        upper = min(self.notes_upper) if len(self.notes_upper) else self.threshold_upper + self.margin_upper
        self.threshold = min(max((lower + upper + 1) / 2, self.threshold_lower), self.threshold_upper)

        if ev.type == NOTEON:
            # add notes to the appropriate list
            if ev.note < self.threshold:
                self.notes_lower[ev.note] = 0
            else:
                self.notes_upper[ev.note] = 0
        elif ev.type == NOTEOFF:
            # mark notes for removal
            if ev.note in self.notes_lower:
                self.notes_lower[ev.note] = now
            if ev.note in self.notes_upper:
                self.notes_upper[ev.note] = now

        return ev


class _FloatingKeySplitFilter(object):
    def __init__(self, analyze, index):
        self.analyze = analyze
        self.index = index

    def __call__(self, ev):
        # the split point can never move past a note that's still being held, so this is
        # valid for both note-on and note-off events
        if (self.index == 0 and ev.note < self.analyze.threshold or
            self.index == 1 and ev.note >= self.analyze.threshold):
            return ev
        else:
            return None


def FloatingKeySplit(threshold_lower, threshold_upper, patch_lower, patch_upper,
                     hold_time=1.0, margin_lower=12, margin_upper=12):
    analyze = _FloatingKeySplitAnalyze(threshold_lower, threshold_upper, hold_time, margin_lower, margin_upper)
    return Split({
        NOTE:   Process(analyze) >> [
                    Process(_FloatingKeySplitFilter(analyze, 0)) >> patch_lower,
                    Process(_FloatingKeySplitFilter(analyze, 1)) >> patch_upper,
                ],
        None:   [ patch_lower, patch_upper ],
    })
