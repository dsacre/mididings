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

from __future__ import with_statement

try:
    import unittest2 as unittest
except:
    import unittest

import random
import itertools
import sys
import copy

from mididings import *
from mididings import setup, engine, misc, constants
from mididings.event import *

import mididings
import mididings.event


def data_offsets(f):
    """
    Runs the test f twice, with data offsets 0 and 1
    """
    def data_offset_wrapper(self):
        for offset in (0, 1):
            def off(n):
                return n + offset
            config(data_offset = offset)
            f(self, off)
    return data_offset_wrapper


class MididingsTestCase(unittest.TestCase):
    def setUp(self):
        setup.reset()
        setup.config(data_offset = 0)

        self.mididings_dict = mididings.__dict__.copy()
        self.mididings_dict.update(mididings.event.__dict__)

    def check_patch(self, patch, d):
        """
        Test the given patch. d must be a mapping from events to the expected
        list of resulting events.
        """
        self.check_scenes({ setup.get_config('data_offset'): patch }, d)

    def check_scenes(self, scenes, d):
        """
        Test the given scenes. d must be a mapping from events to the expected
        list of resulting events.
        """
        for ev, expected in d.items():
            r = self.run_scenes(scenes, ev)
            if isinstance(expected, bool):
                # boolean value: ensure that at most one event was returned
                self.assertLessEqual(len(r), 1)
                # ensure that event is unchanged
                if len(r):
                    self.assertEqual(r[0], ev)
                # check if the result is as expected
                self.assertEqual(bool(len(r)), expected,
                        "\nscenes=%s\nev=%s\nexpected=%s" % (repr(scenes), repr(ev), repr(expected)))
            else:
                # list: check if the result is exactly as expected
                self.assertEqual(r, expected,
                        "\nscenes=%s\nev=%s\nr=%s\nexpected=%s" % (repr(scenes), repr(ev), repr(r), repr(expected)))

    def check_filter(self, filt, d):
        """
        Test if the filter filt works as expected.
        d must be a mapping from events to a tuple of two booleans, where the
        first value specifies if the event should match the filter as is, and
        the second value specifies if the event should match the inverted
        filter.
        """
        for ev, expected in d.items():
            for f, p in zip((filt, ~filt, -filt), [expected[0], expected[1], not expected[0]]):
                self.check_patch(f, {ev: p})

    def run_patch(self, patch, events):
        """
        Run the given events through the given patch, return the list of
        resulting events.
        """
        return self.run_scenes({ setup.get_config('data_offset'): patch }, events)

    def run_scenes(self, scenes, events):
        """
        Run the given events through the given scenes, return the list of
        resulting events.
        """
        # run scenes
        r1 = self._run_scenes(scenes, events)

        # check if events can be rebuilt from their repr()
        for ev in r1:
            rebuilt = eval(repr(ev), self.mididings_dict)
            self.assertEqual(rebuilt, ev)

        rebuilt = self._rebuild_repr(scenes)
        if rebuilt is not None:
            # run scenes rebuilt from their repr(), result should be identical
            r2 = self._run_scenes(rebuilt, events)
            self.assertEqual(r2, r1)

        return r1

    def _rebuild_repr(self, scenes):
        r = {}
        for k, v in scenes.items():
            rep = repr(v)
            if 'Process' in rep:
                # patches with Process() units are too tricky for now
                return None
            w = eval(rep, self.mididings_dict)
            # the repr() of the rebuilt patch should be identical to the repr()
            # string it was built from
            self.assertEqual(repr(w), rep)
            r[k] = w
        return r

    def _run_scenes(self, scenes, events):
        setup._config_impl(
            backend='dummy'
        )
        e = engine.Engine()
        e.setup(scenes, None, None, None)
        r = []
        if not misc.issequence(events):
            events = [events]
        for ev in events:
            r += e.process_event(ev)[:]
        for ev in r:
            ev.__class__ = MidiEvent
        return r

    def make_event(self, *args, **kwargs):
        """
        Create a new MIDI event. Attributes can be specified in args or
        kwargs, unspecified attributes are filled with random values.
        """
        type, port, channel, data1, data2, sysex = itertools.islice(itertools.chain(args, itertools.repeat(None)), 6)

        for k, v in kwargs.items():
            if k == 'type': type = v
            if k == 'port': port = v
            elif k == 'channel': channel = v
            elif k in ('data1', 'note', 'ctrl'): data1 = v
            elif k in ('data2', 'velocity', 'value'): data2 = v
            elif k == 'program': data2 = v - setup.get_config('data_offset')
            elif k == 'sysex': sysex = v

        if type is None:
            if channel is None:
                type = random.choice(list(set(constants._EVENT_TYPES.values()) - set([DUMMY])))
            else:
                type = random.choice([NOTEON, NOTEOFF, CTRL, PITCHBEND, AFTERTOUCH, POLY_AFTERTOUCH, PROGRAM])
        elif type == NOTE:
            type = random.choice([NOTEON, NOTEOFF])
        elif misc.issequence(type):
            type = random.choice(type)

        if port is None:
            port = random.randrange(0, 42) + setup.get_config('data_offset')
        if channel is None:
            channel = random.randrange(0, 16) + setup.get_config('data_offset')
        if data1 is None:
            data1 = random.randrange(0, 128)
        if data2 is None:
            data2 = (random.randrange(1, 128) if type == NOTEON
                     else 0 if type == NOTEOFF
                     else random.randrange(0, 128))

        if type == SYSEX and sysex is None:
            sysex = [0xf0] + [random.randrange(0, 128) for n in range(random.randrange(1024))] + [0xf7]

        return MidiEvent(type, port, channel, data1, data2, sysex)

    def modify_event(self, ev, **kwargs):
        """
        Make a copy of the event ev, replacing arbitrary attributes with the
        values given in kwargs.
        """
        r = copy.copy(ev)
        for k, v in kwargs.items():
            setattr(r, k, v)
        return r

    def native_sysex(self, sysex):
        if isinstance(sysex, str):
            sysex = map(ord, sysex)

        if sys.version_info >= (2, 6):
            return bytearray(sysex)
        else:
            return list(sysex)
