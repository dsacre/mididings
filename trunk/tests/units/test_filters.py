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


class FiltersTestCase(MididingsTestCase):

    @data_offsets
    def test_PortFilter(self, off):
        config(in_ports = ['foo', 'bar', 'baz'])

        self.check_filter(PortFilter(off(0)), {
            self.make_event(port=off(0)): (True, False),
            self.make_event(port=off(1)): (False, True),
        })

        self.check_filter(PortFilter(ports=off(1)), {
            self.make_event(port=off(0)): (False, True),
            self.make_event(port=off(1)): (True, False),
        })

        self.check_filter(PortFilter(off(0), off(1), off(2)), {
            self.make_event(port=off(0)): (True, False),
            self.make_event(port=off(1)): (True, False),
            self.make_event(port=off(2)): (True, False),
            self.make_event(port=off(3)): (False, True),
        })

        self.check_filter(PortFilter(ports=['foo', 'baz']), {
            self.make_event(port=off(0)): (True, False),
            self.make_event(port=off(1)): (False, True),
            self.make_event(port=off(2)): (True, False),
            self.make_event(port=off(3)): (False, True),
        })

        with self.assertRaises(TypeError):
            PortFilter()
        with self.assertRaises(TypeError):
            PortFilter(123.456)
        with self.assertRaises(ValueError):
            PortFilter('nonexist')
        with self.assertRaises(ValueError):
            PortFilter(off(-1))

    @data_offsets
    def test_ChannelFilter(self, off):
        self.check_filter(ChannelFilter(off(2)), {
            self.make_event(channel=off(2)): (True, False),
            self.make_event(channel=off(3)): (False, True),
        })

        self.check_filter(ChannelFilter(channels=[off(3)]), {
            self.make_event(channel=off(2)): (False, True),
            self.make_event(channel=off(3)): (True, False),
        })

        self.check_filter(ChannelFilter(off(3), off(4), off(5)), {
            self.make_event(channel=off(2)): (False, True),
            self.make_event(channel=off(3)): (True, False),
            self.make_event(channel=off(4)): (True, False),
            self.make_event(channel=off(5)): (True, False),
        })

        self.check_filter(ChannelFilter([off(3), off(4), off(5)]), {
            self.make_event(channel=off(2)): (False, True),
            self.make_event(channel=off(3)): (True, False),
            self.make_event(channel=off(4)): (True, False),
            self.make_event(channel=off(5)): (True, False),
        })

        with self.assertRaises(TypeError):
            ChannelFilter()
        with self.assertRaises(TypeError):
            ChannelFilter('blah')
        with self.assertRaises(ValueError):
            ChannelFilter(off(-1))
        with self.assertRaises(ValueError):
            ChannelFilter(off(16))

    @data_offsets
    def test_KeyFilter(self, off):
        self.check_filter(KeyFilter('e2:a3'), {
            self.make_event(NOTE, note=51): (False, True),
            self.make_event(NOTE, note=52): (True, False),
            self.make_event(NOTE, note=68): (True, False),
            self.make_event(NOTE, note=69): (False, True),
            self.make_event(PROGRAM): (True, True),
            self.make_event(CTRL): (True, True),
        })

        self.check_filter(KeyFilter('c3'), {
            self.make_event(NOTE, note=59): (False, True),
            self.make_event(NOTE, note=60): (True, False),
            self.make_event(NOTE, note=61): (False, True),
        })

        self.check_filter(KeyFilter('e2', 'a3'), {
            self.make_event(NOTE, note=23): (False, True),
            self.make_event(NOTE, note=60): (True, False),
        })

        self.check_filter(KeyFilter(lower='c3'), {
            self.make_event(NOTE, note=23): (False, True),
            self.make_event(NOTE, note=59): (False, True),
            self.make_event(NOTE, note=60): (True, False),
            self.make_event(NOTE, note=108): (True, False),
        })

        self.check_filter(KeyFilter(upper=60), {
            self.make_event(NOTE, note=23): (True, False),
            self.make_event(NOTE, note=59): (True, False),
            self.make_event(NOTE, note=60): (False, True),
            self.make_event(NOTE, note=108): (False, True),
        })

        self.check_filter(KeyFilter(notes=[23, 42]), {
            self.make_event(NOTE, note=16): (False, True),
            self.make_event(NOTE, note=23): (True, False),
            self.make_event(NOTE, note=32): (False, True),
            self.make_event(NOTE, note=42): (True, False),
            self.make_event(NOTE, note=69): (False, True),
        })

        with self.assertRaises(TypeError):
            KeyFilter()
        with self.assertRaises(TypeError):
            KeyFilter(123.456)

    @data_offsets
    def test_VelocityFilter(self, off):
        self.check_filter(VelocityFilter(42), {
            self.make_event(NOTEON, velocity=23): (False, True),
            self.make_event(NOTEON, velocity=42): (True, False),
            self.make_event(NOTEOFF, velocity=23): (True, True),
            self.make_event(NOTEOFF, velocity=42): (True, True),
            self.make_event(PROGRAM): (True, True),
            self.make_event(CTRL): (True, True),
        })

        self.check_filter(VelocityFilter(lower=42), {
            self.make_event(NOTEON, velocity=41): (False, True),
            self.make_event(NOTEON, velocity=42): (True, False),
            self.make_event(NOTEON, velocity=69): (True, False),
        })

        self.check_filter(VelocityFilter(upper=108), {
            self.make_event(NOTEON, velocity=23): (True, False),
            self.make_event(NOTEON, velocity=107): (True, False),
            self.make_event(NOTEON, velocity=108): (False, True),
        })

        self.check_filter(VelocityFilter(lower=64, upper=128), {
            self.make_event(NOTEON, velocity=23): (False, True),
            self.make_event(NOTEON, velocity=127): (True, False),
            self.make_event(NOTEOFF, velocity=23): (True, True),
            self.make_event(NOTEOFF, velocity=127): (True, True),
            self.make_event(PROGRAM): (True, True),
            self.make_event(CTRL): (True, True),
        })

        with self.assertRaises(TypeError):
            VelocityFilter()
        with self.assertRaises(TypeError):
            VelocityFilter(123.456)
        with self.assertRaises(TypeError):
            VelocityFilter('blah')
        with self.assertRaises(ValueError):
            VelocityFilter(-1)
        with self.assertRaises(ValueError):
            VelocityFilter(128)

    @data_offsets
    def test_CtrlFilter(self, off):
        self.check_filter(CtrlFilter(23), {
            self.make_event(CTRL, ctrl=23): (True, False),
            self.make_event(CTRL, ctrl=42): (False, True),
            self.make_event(NOTEON): (False, False),
            self.make_event(PROGRAM): (False, False),
        })

        self.check_filter(CtrlFilter(23, 42), {
            self.make_event(CTRL, ctrl=23): (True, False),
            self.make_event(CTRL, ctrl=42): (True, False),
            self.make_event(CTRL, ctrl=69): (False, True),
        })

        self.check_filter(CtrlFilter(ctrls=[23, 42]), {
            self.make_event(CTRL, ctrl=23): (True, False),
            self.make_event(CTRL, ctrl=42): (True, False),
            self.make_event(CTRL, ctrl=69): (False, True),
        })

        with self.assertRaises(TypeError):
            CtrlFilter(123.456)
        with self.assertRaises(TypeError):
            CtrlFilter('blah')
        with self.assertRaises(ValueError):
            CtrlFilter(-1)
        with self.assertRaises(ValueError):
            CtrlFilter(128)

    @data_offsets
    def test_CtrlValueFilter(self, off):
        self.check_filter(CtrlValueFilter(value=23), {
            self.make_event(CTRL, value=16): (False, True),
            self.make_event(CTRL, value=23): (True, False),
            self.make_event(CTRL, value=66): (False, True),
            self.make_event(NOTE): (False, False),
            self.make_event(PROGRAM): (False, False),
        })

        self.check_filter(CtrlValueFilter(23, 42), {
            self.make_event(CTRL, value=32): (True, False),
            self.make_event(CTRL, value=66): (False, True),
        })

    @data_offsets
    def test_ProgramFilter(self, off):
        self.check_filter(ProgramFilter(off(1)), {
            self.make_event(PROGRAM, program=off(1)): (True, False),
            self.make_event(PROGRAM, program=off(2)): (False, True),
            self.make_event(NOTE): (False, False),
            self.make_event(CTRL): (False, False),
        })

        self.check_filter(ProgramFilter(off(4), off(8), off(15), off(16)), {
            self.make_event(PROGRAM, program=off(8)): (True, False),
            self.make_event(PROGRAM, program=off(13)): (False, True),
        })

        self.check_filter(ProgramFilter(programs=[off(4), off(8), off(15), off(16)]), {
            self.make_event(PROGRAM, program=off(8)): (True, False),
            self.make_event(PROGRAM, program=off(13)): (False, True),
        })

        with self.assertRaises(TypeError):
            ProgramFilter()
        with self.assertRaises(TypeError):
            ProgramFilter(123.456)
        with self.assertRaises(TypeError):
            ProgramFilter('blah')
        with self.assertRaises(ValueError):
            ProgramFilter(off(-1))
        with self.assertRaises(ValueError):
            ProgramFilter(off(128))

    @data_offsets
    def test_SysExFilter(self, off):
        self.check_filter(SysExFilter([0xf0, 4, 8, 15, 16, 23, 42, 0xf7]), {
            SysExEvent(off(0), [0xf0, 4, 8, 15, 16, 23, 42, 0xf7]): (True, False),
            SysExEvent(off(0), [0xf0, 4, 8, 15, 16, 23, 43, 0xf7]): (False, True),
            self.make_event(NOTE): (False, False),
            self.make_event(CTRL): (False, False),
        })

        self.check_filter(SysExFilter('\xf0\x04\x08'), {
            SysExEvent(off(0), [0xf0, 4, 8, 15, 16, 23, 42, 0xf7]): (True, False),
            SysExEvent(off(0), [0xf0, 4, 9, 15, 16, 23, 42, 0xf7]): (False, True),
        })

        self.check_filter(SysExFilter(manufacturer=0x42), {
            SysExEvent(off(0), [0xf0, 0x42, 8, 15, 16, 23, 42, 0xf7]): (True, False),
            SysExEvent(off(0), [0xf0, 0x43, 8, 15, 16, 23, 42, 0xf7]): (False, True),
        })

        self.check_filter(SysExFilter(manufacturer='\x00\x23\x42'), {
            SysExEvent(off(0), [0xf0, 0x00, 0x23, 0x42, 16, 23, 42, 0xf7]): (True, False),
            SysExEvent(off(0), [0xf0, 4, 8, 15, 16, 23, 42, 0xf7]): (False, True),
        })
