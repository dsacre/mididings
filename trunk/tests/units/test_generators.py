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

from tests.helpers import *

from mididings import *


class GeneratorsTestCase(MididingsTestCase):

    @data_offsets
    def test_NoteOn(self, off):
        ev = self.make_event(CTRL)

        p = NoteOn(60, 127)
        self.check_patch(p, {
            ev: [self.make_event(NOTEON, ev.port, ev.channel, 60, 127)],
        })
        p = NoteOn(port=off(2), channel=off(3), note=EVENT_CTRL, velocity=42)
        self.check_patch(p, {
            ev: [self.make_event(NOTEON, off(2), off(3), ev.ctrl, 42)],
        })

    @data_offsets
    def test_NoteOff(self, off):
        ev = self.make_event(CTRL)

        p = NoteOff(60, 127)
        self.check_patch(p, {
            ev: [self.make_event(NOTEOFF, ev.port, ev.channel, 60, 127)],
        })
        p = NoteOff(port=off(2), channel=off(3), note=EVENT_CTRL, velocity=42)
        self.check_patch(p, {
            ev: [self.make_event(NOTEOFF, off(2), off(3), ev.ctrl, 42)],
        })

    @data_offsets
    def test_Ctrl(self, off):
        ev = self.make_event(NOTEON)

        p = Ctrl(23, 42)
        self.check_patch(p, {
            ev: [self.make_event(CTRL, ev.port, ev.channel, 23, 42)],
        })
        p = Ctrl(port=off(2), channel=off(3), ctrl=23, value=EVENT_NOTE)
        self.check_patch(p, {
            ev: [self.make_event(CTRL, off(2), off(3), 23, ev.note)],
        })

    @data_offsets
    def test_Pitchbend(self, off):
        ev = self.make_event(CTRL)

        p = Pitchbend(8191)
        self.check_patch(p, {
            ev: [self.make_event(PITCHBEND, ev.port, ev.channel, 0, 8191)],
        })
        p = Pitchbend(port=off(2), channel=off(3), value=EVENT_VALUE)
        self.check_patch(p, {
            ev: [self.make_event(PITCHBEND, off(2), off(3), 0, ev.value)],
        })

    @data_offsets
    def test_Aftertouch(self, off):
        ev = self.make_event(CTRL)

        p = Aftertouch(42)
        self.check_patch(p, {
            ev: [self.make_event(AFTERTOUCH, ev.port, ev.channel, 0, 42)],
        })
        p = Aftertouch(port=off(2), channel=off(3), value=EVENT_VALUE)
        self.check_patch(p, {
            ev: [self.make_event(AFTERTOUCH, off(2), off(3), 0, ev.value)],
        })

    @data_offsets
    def test_Program(self, off):
        ev = self.make_event(NOTEON)

        p = Program(off(42))
        self.check_patch(p, {
            ev: [self.make_event(PROGRAM, ev.port, ev.channel, 0, 42)],
        })
        p = Program(port=off(2), channel=off(3), program=EVENT_NOTE)
        self.check_patch(p, {
            ev: [self.make_event(PROGRAM, off(2), off(3), 0, ev.note)],
        })

    @data_offsets
    def test_SysEx(self, off):
        ev = self.make_event(NOTEON)

        p = SysEx([0xf0, 4, 8, 15, 16, 23, 42, 0xf7])
        self.check_patch(p, {
            ev: [SysExEvent(ev.port, [0xf0, 4, 8, 15, 16, 23, 42, 0xf7])],
        })
        p = SysEx(port=off(2), sysex=[0xf0, 4, 8, 15, 16, 23, 42, 0xf7])
        self.check_patch(p, {
            ev: [SysExEvent(off(2), [0xf0, 4, 8, 15, 16, 23, 42, 0xf7])],
        })
