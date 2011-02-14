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

import tests.helpers

from mididings import *


class FiltersTestCase(tests.helpers.MididingsTestCase):

    def test_PortFilter(self):
        self.check_filter(PortFilter(0), {
            self.make_event(port=0): (True, False),
        })
        self.check_filter(PortFilter(1), {
            self.make_event(port=0): (False, True),
        })

        with self.assertRaises(ValueError):
            PortFilter('nonexist')

        with self.assertRaises(ValueError):
            PortFilter(-1)

    def test_ChannelFilter(self):
        self.check_filter(ChannelFilter(2), {
            self.make_event(channel=2): (True, False),
        })
        self.check_filter(ChannelFilter(3), {
            self.make_event(channel=2): (False, True),
        })

        with self.assertRaises(ValueError):
            ChannelFilter(-1)
        with self.assertRaises(ValueError):
            ChannelFilter(16)

    def test_KeyFilter(self):
        self.check_filter(KeyFilter('e3:a4'), {
            self.make_event(NOTEON, note=23): (False, True),
            self.make_event(NOTEON, note=60): (True, False),
            self.make_event(NOTEOFF, note=23): (False, True),
            self.make_event(NOTEOFF, note=60): (True, False),
            self.make_event(PROGRAM): (True, True),
        })

    def test_VelocityFilter(self):
        self.check_filter(VelocityFilter(64, 128), {
            self.make_event(NOTEON, velocity=23): (False, True),
            self.make_event(NOTEON, velocity=127): (True, False),
            self.make_event(NOTEOFF, velocity=23): (True, True),
            self.make_event(NOTEOFF, velocity=127): (True, True),
            self.make_event(PROGRAM): (True, True),
        })

    def test_CtrlFilter(self):
        self.check_filter(CtrlFilter(23), {
            self.make_event(CTRL, ctrl=23): (True, False),
            self.make_event(CTRL, ctrl=42): (False, True),
            self.make_event(NOTEON): (True, True),
            self.make_event(PROGRAM): (True, True),
        })

    def test_CtrlValueFilter(self):
        self.check_filter(CtrlValueFilter(23, 42), {
            self.make_event(CTRL, value=32): (True, False),
            self.make_event(CTRL, value=66): (False, True),
            self.make_event(PROGRAM): (True, True),
        })

    def test_ProgramFilter(self):
        self.check_filter(ProgramFilter(4, 8, 15, 16), {
            self.make_event(PROGRAM, value=8): (True, False),
            self.make_event(PROGRAM, value=13): (False, True),
            self.make_event(CTRL): (True, True),
        })
