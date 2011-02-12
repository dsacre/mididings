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


class SplitsTestCase(tests.helpers.MididingsTestCase):

    def test_ChannelSplit(self):
        p = ChannelSplit({ 0: Discard(), (1, 2): Pass() })
        self.check_patch(p, {
            self.make_event(channel=0): False,
            self.make_event(channel=1): True,
        })
        p = ChannelSplit({ 0: Discard(), (2, 3): Discard(), None: Pass() })
        self.check_patch(p, {
            self.make_event(channel=0): False,
            self.make_event(channel=1): True,
        })

    def test_KeySplit(self):
        ev1 = self.make_event(NOTEON, note=66)
        ev2 = self.make_event(NOTEON, note=42)
        ev3 = self.make_event(PROGRAM)

        p = KeySplit(55, Channel(3), Channel(7))
        self.check_patch(p, {
            ev1: [self.modify_event(ev1, channel=7)],
            ev2: [self.modify_event(ev2, channel=3)],
            ev3: [self.modify_event(ev3, channel=3), self.modify_event(ev3, channel=7)],
        })
