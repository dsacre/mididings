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
import mididings.util as _util
import mididings.engine as _engine


class _FloatingKeySplitAnalyzer(object):
    """
    Analyzer class that determines the current split point based on the
    given parameters and the notes being played.
    """
    def __init__(self, threshold_lower, threshold_upper,
                 hold_time, margin_lower, margin_upper):
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

        # the lower reference point is the highest note played in the region
        # below the split point, but never below the lower threshold by more
        # than the set margin
        lower = self.threshold_lower - self.margin_lower
        if len(self.notes_lower):
            m = max(self.notes_lower)
            lower = max(m, lower)

        # the upper reference point is the lowest note played in the region
        # above the split point, but never above the upper threshold by more
        # than the set margin
        upper = self.threshold_upper + self.margin_upper
        if len(self.notes_upper):
            m = min(self.notes_upper)
            upper = min(m, upper)

        # calculate new threshold as the center between upper and lower
        # reference point, but confined by the given thresholds
        self.threshold = min(max((lower + upper + 1) // 2,
                                 self.threshold_lower),
                             self.threshold_upper)

        if ev.type == _m.NOTEON:
            # add notes to the appropriate list
            if ev.note < self.threshold:
                self.notes_lower[ev.note] = 0
            else:
                self.notes_upper[ev.note] = 0
        elif ev.type == _m.NOTEOFF:
            # mark notes for removal
            if ev.note in self.notes_lower:
                self.notes_lower[ev.note] = now
            if ev.note in self.notes_upper:
                self.notes_upper[ev.note] = now

        return ev


class _FloatingKeySplitFilter(object):
    """
    Filter class that filters events based on the state of the given analyser.
    """
    def __init__(self, analyzer, index):
        self.analyzer = analyzer
        self.index = index

    def __call__(self, ev):
        # the split point can never move past a note that's still being held,
        # so this is valid for both note-on and note-off events
        if (self.index == 0 and ev.note < self.analyzer.threshold or
            self.index == 1 and ev.note >= self.analyzer.threshold):
            return ev
        else:
            return None


def FloatingKeySplit(threshold_lower, threshold_upper,
                     patch_lower, patch_upper,
                     hold_time=1.0,
                     margin_lower=12, margin_upper=12):
    """
    Create a floating split point that moves dynamically depending on what
    you are playing, allowing a region of the keyboard to be shared between
    two split zones.

    :param threshold_lower:
    :param threshold_upper:
        The lowest and highest notes between which the split point is
        allowed to move.

    :param patch_lower:
    :param patch_upper:
        The patch to which notes below/above the split point will be sent.

    :param hold_time:
        How long released notes will still be taken into account when
        determining the split point (in seconds).

    :param margin_lower:
    :param margin_upper:
        How close you must get to the split point before it starts getting
        pushed into the opposite direction (in semitones).
    """
    # create a single analyzer instance
    analyzer = _FloatingKeySplitAnalyzer(threshold_lower, threshold_upper,
                                         hold_time, margin_lower, margin_upper)

    return _m.Split({
        # separate filter instances are needed for both regions, in order to
        # be able to send note events to different patches
        _m.NOTE:
                _m.Process(analyzer) >> [
                    _m.Process(_FloatingKeySplitFilter(analyzer, 0))
                        >> patch_lower,
                    _m.Process(_FloatingKeySplitFilter(analyzer, 1))
                        >> patch_upper,
                ],
        # non-note-events are sent to both patches
        None:   [ patch_lower, patch_upper ],
    })
