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

from tests.helpers import *

from mididings import *

import random


class ModifiersTestCase(MididingsTestCase):

    @data_offsets
    def test_Port(self, off):
        ev = self.make_event()

        self.check_patch(Port(off(7)), {
            ev: [self.modify_event(ev, port=off(7))],
        })
        self.check_patch(Port(port=off(8)), {
            ev: [self.modify_event(ev, port=off(8))],
        })

        with self.assertRaises(TypeError):
            Port(123.456)

    @data_offsets
    def test_Channel(self, off):
        ev = self.make_event()

        self.check_patch(Channel(off(7)), {
            ev: [self.modify_event(ev, channel=off(7))],
        })
        self.check_patch(Channel(channel=off(8)), {
            ev: [self.modify_event(ev, channel=off(8))],
        })

        with self.assertRaises(TypeError):
            Channel(123.456)
        with self.assertRaises(TypeError):
            Channel('blah')
        with self.assertRaises(ValueError):
            Channel(17)

    @data_offsets
    def test_Transpose(self, off):
        ev1 = self.make_event(NOTEON, note=random.randrange(0, 115))
        ev2 = self.make_event(NOTEON, note=random.randrange(0, 115))
        ev3 = self.make_event(CTRL)

        self.check_patch(Transpose(12), {
            ev1: [self.modify_event(ev1, note=ev1.note + 12)],
            ev2: [self.modify_event(ev2, note=ev2.note + 12)],
            ev3: [ev3],
        })

        with self.assertRaises(TypeError):
            Transpose(123.456)
        with self.assertRaises(TypeError):
            Transpose('blah')

    @data_offsets
    def test_Key(self, off):
        ev = self.make_event(NOTE)
        ev2 = self.make_event(CTRL)

        self.check_patch(Key(42), {
            ev: [self.modify_event(ev, note=42)],
            ev2: [ev2],
        })

        with self.assertRaises(TypeError):
            Key(123.456)
        with self.assertRaises(ValueError):
            Key('blah')
        with self.assertRaises(ValueError):
            Key(-1)
        with self.assertRaises(ValueError):
            Key(128)

    @data_offsets
    def test_Velocity(self, off):
        ev = self.make_event(NOTEON, velocity=42)
        ev2 = self.make_event(PROGRAM)

        self.check_patch(Velocity(23), {
            ev: [self.modify_event(ev, velocity=65)],
            ev2: [ev2],
        })

        self.check_patch(Velocity(multiply=1.5), {
            ev: [self.modify_event(ev, velocity=63)],
            ev2: [ev2],
        })

        self.check_patch(Velocity(fixed=108), {
            ev: [self.modify_event(ev, velocity=108)],
            ev2: [ev2],
        })

        self.check_patch(Velocity(gamma=2.0), {
            ev: [self.modify_event(ev, velocity=73)],
            ev2: [ev2],
        })

        self.check_patch(Velocity(curve=-2.0), {
            ev: [self.modify_event(ev, velocity=18)],
            ev2: [ev2],
        })

        self.check_patch(Velocity(multiply=1.5, offset=23), {
            ev: [self.modify_event(ev, velocity=86)],
            ev2: [ev2],
        })

        with self.assertRaises(TypeError):
            Velocity('blah')
        with self.assertRaises(TypeError):
            Velocity(something=123)

    @data_offsets
    def test_VelocitySlope(self, off):
        ev0 = self.make_event(NOTEON, note=0, velocity=42)
        ev23 = self.make_event(NOTEON, note=23, velocity=42)
        ev32 = self.make_event(NOTEON, note=32, velocity=42)
        ev42 = self.make_event(NOTEON, note=42, velocity=42)
        ev127 = self.make_event(NOTEON, note=127, velocity=42)

        self.check_patch(VelocitySlope((23, 42), (-13, +13)), {
            ev0: [self.modify_event(ev0, velocity=29)],
            ev23: [self.modify_event(ev23, velocity=29)],
            ev32: [self.modify_event(ev32, velocity=42)],
            ev42: [self.modify_event(ev42, velocity=55)],
            ev127: [self.modify_event(ev127, velocity=55)],
        })

        self.check_patch(VelocitySlope(('b-1', 'f#1'), multiply=(0.5, 2.0)), {
            ev0: [self.modify_event(ev0, velocity=21)],
            ev23: [self.modify_event(ev23, velocity=21)],
            ev32: [self.modify_event(ev32, velocity=50)],
            ev42: [self.modify_event(ev42, velocity=84)],
            ev127: [self.modify_event(ev127, velocity=84)],
        })

        self.check_patch(VelocitySlope((23, 42), fixed=(13, 113)), {
            ev0: [self.modify_event(ev0, velocity=13)],
            ev23: [self.modify_event(ev23, velocity=13)],
            ev32: [self.modify_event(ev32, velocity=60)],
            ev42: [self.modify_event(ev42, velocity=113)],
            ev127: [self.modify_event(ev127, velocity=113)],
        })

        self.check_patch(VelocitySlope(('b-1', 'f#1'), gamma=(1.0, 2.0)), {
            ev0: [self.modify_event(ev0, velocity=42)],
            ev23: [self.modify_event(ev23, velocity=42)],
            ev32: [self.modify_event(ev32, velocity=60)],
            ev42: [self.modify_event(ev42, velocity=73)],
            ev127: [self.modify_event(ev127, velocity=73)],
        })

        self.check_patch(VelocitySlope((23, 42), curve=(0, -2.0)), {
            ev0: [self.modify_event(ev0, velocity=42)],
            ev23: [self.modify_event(ev23, velocity=42)],
            ev32: [self.modify_event(ev32, velocity=29)],
            ev42: [self.modify_event(ev42, velocity=18)],
            ev127: [self.modify_event(ev127, velocity=18)],
        })

        self.check_patch(VelocitySlope((23, 42), (0.5, 2.0), (-13, +13)), {
            ev0: [self.modify_event(ev0, velocity=8)],
            ev23: [self.modify_event(ev23, velocity=8)],
            ev32: [self.modify_event(ev32, velocity=50)],
            ev42: [self.modify_event(ev42, velocity=97)],
            ev127: [self.modify_event(ev127, velocity=97)],
        })

        with self.assertRaises(TypeError):
            VelocitySlope((23, 42, 66.6), (4, 8, 15))
        with self.assertRaises(ValueError):
            VelocitySlope((23, 42, 66), (4, 8))
        with self.assertRaises(ValueError):
            VelocitySlope((23, 66, 42), (4, 8, 15))

    @data_offsets
    def test_VelocityLimit(self, off):
        ev23 = self.make_event(NOTEON, velocity=23)
        ev42 = self.make_event(NOTEON, velocity=42)
        ev108 = self.make_event(NOTEON, velocity=108)
        ev_noteoff = self.make_event(NOTEOFF)
        ev_ctrl = self.make_event(CTRL)

        self.check_patch(VelocityLimit(32, 69), {
            ev23: [self.modify_event(ev23, velocity=32)],
            ev42: [self.modify_event(ev42, velocity=42)],
            ev108: [self.modify_event(ev108, velocity=69)],
            ev_noteoff: [ev_noteoff],
            ev_ctrl: [ev_ctrl],
        })

        self.check_patch(VelocityLimit(max=69), {
            ev23: [self.modify_event(ev23, velocity=23)],
            ev42: [self.modify_event(ev42, velocity=42)],
            ev108: [self.modify_event(ev108, velocity=69)],
            ev_noteoff: [ev_noteoff],
            ev_ctrl: [ev_ctrl],
        })

        self.check_patch(VelocityLimit(min=32), {
            ev23: [self.modify_event(ev23, velocity=32)],
            ev42: [self.modify_event(ev42, velocity=42)],
            ev108: [self.modify_event(ev108, velocity=108)],
            ev_noteoff: [ev_noteoff],
            ev_ctrl: [ev_ctrl],
        })

    @data_offsets
    def test_CtrlMap(self, off):
        ev1 = self.make_event(CTRL, ctrl=23)
        ev2 = self.make_event(CTRL, ctrl=42)
        ev3 = self.make_event(PROGRAM)

        self.check_patch(CtrlMap(23, 69), {
            ev1: [self.modify_event(ev1, ctrl=69)],
            ev2: [ev2],
            ev3: [ev3],
        })

    @data_offsets
    def test_CtrlRange(self, off):
        ev1 = self.make_event(CTRL, ctrl=23, value=0)
        ev2 = self.make_event(CTRL, ctrl=23, value=64)
        ev3 = self.make_event(CTRL, ctrl=23, value=127)

        self.check_patch(CtrlRange(23, 42, 69), {
            ev1: [self.modify_event(ev1, value=42)],
            ev2: [self.modify_event(ev2, value=55)],
            ev3: [self.modify_event(ev3, value=69)],
        })

        self.check_patch(CtrlRange(23, 42, 69, 64, 127), {
            ev1: [self.modify_event(ev1, value=42)],
            ev2: [self.modify_event(ev2, value=42)],
            ev3: [self.modify_event(ev3, value=69)],
        })

    @data_offsets
    def test_CtrlCurve(self, off):
        ev = self.make_event(CTRL, ctrl=23, value=42)
        ev2 = self.make_event(AFTERTOUCH)

        self.check_patch(CtrlCurve(23, offset=23), {
            ev: [self.modify_event(ev, value=65)],
            ev2: [ev2],
        })

        self.check_patch(CtrlCurve(23, multiply=1.5), {
            ev: [self.modify_event(ev, value=63)],
            ev2: [ev2],
        })

        self.check_patch(CtrlCurve(23, gamma=2.0), {
            ev: [self.modify_event(ev, value=73)],
            ev2: [ev2],
        })

        self.check_patch(CtrlCurve(23, curve=-2.0), {
            ev: [self.modify_event(ev, value=18)],
            ev2: [ev2],
        })

        self.check_patch(CtrlCurve(23, 1.5, 23), {
            ev: [self.modify_event(ev, value=86)],
            ev2: [ev2],
        })

    @data_offsets
    def test_Pitchbend(self, off):
        ev1 = self.make_event(PITCHBEND, value=-8192)
        ev2 = self.make_event(PITCHBEND, value=0)
        ev3 = self.make_event(PITCHBEND, value=8191)

        self.check_patch(PitchbendRange(-1234, 5678), {
            ev1: [self.modify_event(ev1, value=-1234)],
            ev2: [self.modify_event(ev2, value=0)],
            ev3: [self.modify_event(ev3, value=5678)],
        })

        self.check_patch(PitchbendRange(-12, 2, range=12), {
            ev1: [self.modify_event(ev1, value=-8192)],
            ev2: [self.modify_event(ev2, value=0)],
            ev3: [self.modify_event(ev3, value=1365)],
        })
