# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2011  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import unittest

from mididings import *
from mididings.event import *
from mididings import engine, setup, misc


class SimpleTestCase(unittest.TestCase):
    def setUp(self):
        config(data_offset=0)
        self.noteon66   = MidiEvent(NOTEON, 0, 0, 66, 23)
        self.noteon42   = MidiEvent(NOTEON, 0, 0, 42, 127)
        self.noteon23   = MidiEvent(NOTEON, 0, 1, 23, 127)
        self.ctrl23     = MidiEvent(CTRL, 0, 0, 23, 42)
        self.ctrl42     = MidiEvent(CTRL, 0, 0, 42, 123)
        self.prog7      = MidiEvent(PROG, 0, 0, 0, 7)

    def tearDown(self):
        pass


    def run_scenes_test(self, scenes, events):
        setup.config(False, backend='dummy')
        e = engine.Engine(scenes, None, None, None)
        r = []
        if not misc.issequence(events):
            events = [events]
        for ev in events:
            r += e.process(ev)[:]
        return r

    def run_test(self, patch, events):
        return self.run_scenes_test({ setup.get_config('data_offset'): patch }, events)

    def check_scenes(self, scenes, d):
        for ev, expected in d.items():
            r = self.run_scenes_test(scenes, ev)
            for x in r:
                x.__class__ = MidiEvent
            if isinstance(expected, bool):
                # boolean value: ensure that at most one event was returned
                assert len(r) <= 1
                # ensure that event is unchanged
                if len(r):
                    assert r[0] == ev
                # check if the result is as expected
                assert bool(len(r)) == expected, "scenes=%s\nev=%s\nexpected=%s" % (repr(scenes), repr(ev), repr(expected))
            else:
                # list: check if the result is exactly as expected
                assert r == expected, "scenes=%s\nev=%s\nr=%s\nexpected=%s" % (repr(scenes), repr(ev), repr(r), repr(expected))

    def check_patch(self, patch, d):
        self.check_scenes({ setup.get_config('data_offset'): patch }, d)

    def check_filter(self, filt, d):
        for ev, expected in d.items():
            for f, p in zip((filt, ~filt, -filt), [expected[0], expected[1], not expected[0]]):
                self.check_patch(f, {ev: p})

    def modify_event(self, ev, **kwargs):
        r = MidiEvent(ev.type_, ev.port, ev.channel, ev.data1, ev.data2)
        for k, v in kwargs.items():
            setattr(r, k, v)
        return r


    def testPass(self):
        self.check_patch(Pass(), {
            self.noteon66:  [self.noteon66],
        })
        self.check_patch(Discard(), {
            self.noteon66:  [],
        })

    def testFork(self):
        p = Fork([Pass(), Pass()])
        self.check_patch(p, {
            self.noteon42:  True,
        })
        p = Fork([Pass(), Pass()], remove_duplicates=False)
        self.check_patch(p, {
            self.noteon42:  [self.noteon42, self.noteon42],
        })
        p = Fork([Pass(), Discard()], remove_duplicates=False)
        self.check_patch(p, {
            self.noteon42:  True,
        })

    def testFilter(self):
        self.check_filter(Filter(PROG), {
            self.noteon66:  (False, True),
            self.prog7:     (True, False),
        })

    def testPortFilter(self):
        self.check_filter(PortFilter(0), {
            self.noteon66:  (True, False),
        })
        self.check_filter(PortFilter(1), {
            self.noteon66:  (False, True),
        })

    def testVelocityFilter(self):
        self.check_filter(VelocityFilter(64, 128), {
            self.noteon66:  (False, True),
            self.noteon42:  (True, False),
            self.prog7:     (True, True),
        })

    def testCtrlFilter(self):
        self.check_filter(CtrlFilter(23), {
            self.ctrl23:    (True, False),
            self.ctrl42:    (False, True),
            self.noteon66:  (True, True),
        })

    def testSelector(self):
        p = CtrlFilter(23) % CtrlValueFilter(123)
        self.check_patch(p, {
            self.noteon66:  True,
            self.ctrl23:    False,
            self.ctrl42:    True,
        })
        p = CtrlFilter(42) % CtrlValueFilter(123)
        self.check_patch(p, {
            self.noteon66:  True,
            self.ctrl23:    True,
            self.ctrl42:    True,
        })
        p = (Filter(CTRL) & CtrlFilter(42) & CtrlValueFilter(123)) % Discard()
        self.check_patch(p, {
            self.noteon66:  True,
            self.ctrl23:    True,
            self.ctrl42:    False,
        })
        p = (CtrlFilter(42) | CtrlValueFilter(123)) % Discard()
        self.check_patch(p, {
            self.noteon66:  False,
            self.ctrl23:    True,
            self.ctrl42:    False,
        })
        p = (Filter(NOTE) | (CtrlFilter(42) & CtrlValueFilter(123))) % Discard()
        self.check_patch(p, {
            self.noteon66:  False,
            self.ctrl23:    True,
            self.ctrl42:    False,
        })
        p = CtrlFilter(42) % (CtrlValueFilter(123) % Discard())
        self.check_patch(p, {
            self.noteon66:  False,
            self.ctrl23:    True,
            self.ctrl42:    False,
        })

    def testSplit(self):
        p = Split({ NOTE: Channel(1), PROG: Channel(2) })
        self.check_patch(p, {
            self.noteon66:  [self.modify_event(self.noteon66, channel_=1)],
            self.prog7:     [self.modify_event(self.prog7, channel_=2)],
            self.ctrl23:    [],
        })

    def testChannelSplit(self):
        p = ChannelSplit({ 0: Discard(), (1, 2): Pass() })
        self.check_patch(p, {
            self.noteon66:  [],
            self.noteon23:  [self.noteon23],
        })
        p = ChannelSplit({ 0: Discard(), (2, 3): Discard(), None: Pass() })
        self.check_patch(p, {
            self.noteon66:  [],
            self.noteon23:  [self.noteon23],
        })

    def testKeySplit(self):
        p = KeySplit(55, Channel(3), Channel(7))
        self.check_patch(p, {
            self.noteon66:  [self.modify_event(self.noteon66, channel_=7)],
            self.noteon42:  [self.modify_event(self.noteon42, channel_=3)],
            self.prog7:     [self.modify_event(self.prog7, channel_=3), self.modify_event(self.prog7, channel_=7)],
        })

    def testProcess(self):
        def foo(ev):
            assert ev.port == 0
            assert ev.channel == 0
            assert ev.note == 66
            assert ev.velocity == 23
            ev.velocity = 42
            return ev
        def bar(ev):
            assert ev.velocity == 42
            return None
        p = Process(foo) >> Process(bar)
        self.check_patch(p, {
            self.noteon66:  [],
        })

    def testGenerateEvent(self):
        p = Ctrl(23, 42)
        self.check_patch(p, {
            MidiEvent(NOTEON, 0, 8, 15, 16): [MidiEvent(CTRL, 0, 8, 23, 42)],
        })
        p = Ctrl(23, EVENT_NOTE)
        self.check_patch(p, {
            MidiEvent(NOTEON, 0, 8, 15, 16): [MidiEvent(CTRL, 0, 8, 23, 15)],
        })

    def testDataOffset(self):
        config(data_offset = 1)
        p = Channel(6)
        ev = MidiEvent(PROG, 1, 1, 0, 41)
        assert ev.channel_ == 0
        assert ev.data2 == 41
        def foo(ev):
            assert ev.channel == 1
            assert ev.channel_ == 0
            assert ev.program == 42
            assert ev.data2 == 41
            ev.channel = 6
        r = self.run_test(p, ev)
        assert r[0].channel_ == 5

    def testSanitize(self):
        def foo(ev):
            ev.port = 42
        def bar(ev):
            assert False
        p = Process(foo) >> Sanitize() >> Process(bar)
        self.run_test(p, self.noteon66)
        p = Velocity(+666) >> Sanitize()
        r = self.run_test(p, self.noteon66)
        assert len(r) == 1
        assert r[0].data2 == 127

    def testSceneSwitch(self):
        config(silent=True)
        p = {
            0:  Split({
                    PROG:  SceneSwitch(),
                    ~PROG: Channel(7),
                }),
            1: Channel(13),
        }
        events = (
            MidiEvent(NOTEON, 0, 0, 69, 123),
            MidiEvent(PROG, 0, 0, 0, 1),
            MidiEvent(NOTEON, 0, 0, 23, 42),
            MidiEvent(NOTEOFF, 0, 0, 69, 0),
        )
        results = [
            MidiEvent(NOTEON, 0, 7, 69, 123),
            MidiEvent(NOTEON, 0, 13, 23, 42),
            MidiEvent(NOTEOFF, 0, 7, 69, 0),
        ]
        self.check_scenes(p, {
            events: results,
        })

    def testNamedPorts(self):
        config(out_ports = ['foo', 'bar', 'baz'])
        self.check_patch(Port('bar'), {
            self.noteon66:  [self.modify_event(self.noteon66, port_=1)],
        })


if __name__ == "__main__":
    unittest.main()
