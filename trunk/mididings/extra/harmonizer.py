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
import mididings.misc as _misc

import itertools as _itertools
from operator import itemgetter as _itemgetter


_MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
_HARMONIC_MINOR_SCALE = [0, 2, 3, 5, 7, 8, 11]

_MODES = ['ionian', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian']

_INTERVALS = ['unison', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'octave',
             'ninth', 'tenth', 'eleventh', 'twelfth', 'thirteenth']


class _Harmonizer(object):
    def __init__(self, tonic, scale, interval, non_harmonic):
        self.tonic = tonic
        self.lookup = {}

        # for each note in the scale, calculate the transpose interval
        for x in scale:
            l = len(scale)
            i = scale.index(x) + interval

            hx = scale[i % l] + ((i / l) * 12)

            self.lookup[x] = hx - x

        r = list(range(12))
        if non_harmonic == 'above':
            # reverse order to make sure higher notes are already calculated
            r.reverse()
        # fill the gaps (notes not in the scale)
        for x in r:
            if x not in scale:
                if non_harmonic == 'below':
                    self.lookup[x] = self.lookup[x-1]
                elif non_harmonic == 'above':
                    self.lookup[x] = self.lookup[(x+1) % 12]
                elif non_harmonic == 'same':
                    self.lookup[x] = 0
                else: # skip
                    self.lookup[x] = None

    def note_offset(self, note):
        n = (note - self.tonic) % 12
        return self.lookup[n]

    def __call__(self, ev):
        off = self.note_offset(ev.note)
        if off is not None:
            ev.note += off
            return True
        else:
            return False


def Harmonize(tonic, scale, interval, non_harmonic='below'):
    t = _util.tonic_note_number(tonic)

    if _misc.issequence(scale):
        shift = 0
    elif isinstance(scale, str):
        if scale == 'major':
            scale = _MAJOR_SCALE
            shift = 0
        elif scale == 'minor':
            scale = _MAJOR_SCALE
            shift = 5
        elif scale == 'minor_harmonic':
            scale = _HARMONIC_MINOR_SCALE
            shift = 0
        elif scale in _MODES:
            shift = _MODES.index(scale)
            scale = _MAJOR_SCALE

    # shift scale to the correct mode
    s = [x - scale[shift] for x in scale[shift:]] + \
        [x + 12 - scale[shift] for x in scale[:shift]]

    if not _misc.issequence(interval):
        interval = [interval]

    # convert all interval names to numbers
    iv = [(_INTERVALS.index(x) if x in _INTERVALS else x) for x in interval]

    # python version:
#    f = [ Process(_Harmonizer(t, s, i, non_harmonic)) for i in iv ]

    # pure mididings version:
    f = []
    for i in iv:
        h = _Harmonizer(t, s, i, non_harmonic)
        # get offset for each key
        offsets = [(x, h.note_offset(x)) for x in range(128)]
        # group by offset
        groups = _itertools.groupby(sorted(offsets, key=_itemgetter(1)), key=_itemgetter(1))

        # create one KeyFilter()/Transpose() pair for each offset
        for off, keys in groups:
            if off is not None:
                f.append(KeyFilter(notes=[k[0] for k in keys]) >> Transpose(off))

    return Filter(NOTE) % f
