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
from mididings.event import *


class FiltersTestCase(MididingsTestCase):

    @data_offsets
    def test_PortFilter(self, off):
        self.check_filter(PortFilter(off(0)), {
            self.make_event(port=off(0)): (True, False),
        })
        self.check_filter(PortFilter(off(1)), {
            self.make_event(port=off(0)): (False, True),
        })

        with self.assertRaises(ValueError):
            PortFilter('nonexist')

        with self.assertRaises(ValueError):
            PortFilter(-1)

    @data_offsets
    def test_ChannelFilter(self, off):
        self.check_filter(ChannelFilter(off(2)), {
            self.make_event(channel=off(2)): (True, False),
        })
        self.check_filter(ChannelFilter(off(3)), {
            self.make_event(channel=off(2)): (False, True),
        })

        with self.assertRaises(ValueError):
            ChannelFilter(-1)
        with self.assertRaises(ValueError):
            ChannelFilter(off(16))

    @data_offsets
    def test_KeyFilter(self, off):
#        self.check_filter(KeyFilter('e3:a4'), {
        self.check_filter(KeyFilter('e2:a3'), {
            self.make_event(NOTEON, note=23): (False, True),
            self.make_event(NOTEON, note=60): (True, False),
            self.make_event(NOTEOFF, note=23): (False, True),
            self.make_event(NOTEOFF, note=60): (True, False),
            self.make_event(PROGRAM): (True, True),
        })

    @data_offsets
    def test_VelocityFilter(self, off):
        self.check_filter(VelocityFilter(64, 128), {
            self.make_event(NOTEON, velocity=23): (False, True),
            self.make_event(NOTEON, velocity=127): (True, False),
            self.make_event(NOTEOFF, velocity=23): (True, True),
            self.make_event(NOTEOFF, velocity=127): (True, True),
            self.make_event(PROGRAM): (True, True),
        })

    @data_offsets
    def test_CtrlFilter(self, off):
        self.check_filter(CtrlFilter(23), {
            self.make_event(CTRL, ctrl=23): (True, False),
            self.make_event(CTRL, ctrl=42): (False, True),
#            self.make_event(NOTEON): (True, True),
#            self.make_event(PROGRAM): (True, True),
            self.make_event(NOTEON): (False, False),
            self.make_event(PROGRAM): (False, False),
        })

    @data_offsets
    def test_CtrlValueFilter(self, off):
        self.check_filter(CtrlValueFilter(23, 42), {
            self.make_event(CTRL, value=32): (True, False),
            self.make_event(CTRL, value=66): (False, True),
#            self.make_event(PROGRAM): (True, True),
            self.make_event(PROGRAM): (False, False),
        })

    @data_offsets
    def test_ProgramFilter(self, off):
        self.check_filter(ProgramFilter(off(4), off(8), off(15), off(16)), {
            self.make_event(PROGRAM, program=off(8)): (True, False),
            self.make_event(PROGRAM, program=off(13)): (False, True),
#            self.make_event(CTRL): (True, True),
            self.make_event(CTRL): (False, False),
        })

    @data_offsets
    def test_SysExFilter(self, off):
        self.check_filter(SysExFilter([0xf0, 4, 8, 15, 16, 23, 42, 0xf7]), {
            SysExEvent(off(0), [0xf0, 4, 8, 15, 16, 23, 42, 0xf7]): (True, False),
            SysExEvent(off(0), [0xf0, 4, 8, 15, 16, 23, 43, 0xf7]): (False, True),
            self.make_event(NOTEON): (False, False),
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
