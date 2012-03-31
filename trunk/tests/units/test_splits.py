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


class SplitsTestCase(MididingsTestCase):

    @data_offsets
    def test_PortSplit(self, off):
        p = PortSplit({
            off(0): Discard(),
            (off(1), off(2)): Pass()
        })
        self.check_patch(p, {
            self.make_event(port=off(0)): False,
            self.make_event(port=off(1)): True,
        })

        p = PortSplit({
            off(0): Discard(),
            (off(2), off(3)): Discard(),
            None: Pass()
        })
        self.check_patch(p, {
            self.make_event(port=off(0)): False,
            self.make_event(port=off(1)): True,
        })

    @data_offsets
    def test_ChannelSplit(self, off):
        p = ChannelSplit({
            off(0): Discard(),
            (off(1), off(2)): Pass()
        })
        self.check_patch(p, {
            self.make_event(channel=off(0)): False,
            self.make_event(channel=off(1)): True,
        })

        p = ChannelSplit({
            off(0): Discard(),
            (off(2), off(3)): Discard(),
            None: Pass()
        })
        self.check_patch(p, {
            self.make_event(channel=off(0)): False,
            self.make_event(channel=off(1)): True,
        })

    @data_offsets
    def test_KeySplit(self, off):
        ev1 = self.make_event(NOTEON, note=66)
        ev2 = self.make_event(NOTEON, note=42)
        ev3 = self.make_event(PROGRAM)

        p = KeySplit(55, Channel(off(3)), Channel(off(7)))
        self.check_patch(p, {
            ev1: [self.modify_event(ev1, channel=off(7))],
            ev2: [self.modify_event(ev2, channel=off(3))],
            ev3: [self.modify_event(ev3, channel=off(3)), self.modify_event(ev3, channel=off(7))],
        })

        p = KeySplit({
            (23, 52): Pass(),
            (52, 69): Discard(),
            (69, 88): Pass(),
        })
        self.check_patch(p, {
            ev1: False,
            ev2: True,
            ev3: True,
        })
