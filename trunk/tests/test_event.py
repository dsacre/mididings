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
from mididings.event import *


class EventTestCase(tests.helpers.MididingsTestCase):

    def test_SysExEvent(self):
        sysex = '\xf0\x04\x08\x15\x16\x23\x42\xf7'
        ev = SysExEvent(0, sysex)

        def foo(ev):
            self.assertEqual(ev.type, SYSEX)
            self.assertEqual(ev.port, 0)
            self.assertEqual(ev.sysex, self.native_sysex(sysex))
            return ev

        self.check_patch(Process(foo), {ev: [ev]})

    def test_operator_equals(self):
        a = self.make_event(channel=0)
        b = self.make_event(channel=1)
        c = self.make_event(type=a.type, port=a.port, channel=a.channel, data1=a.data1, data2=a.data2)

        self.assertFalse(a == b)
        self.assertTrue(a != b)

        self.assertTrue(a == c)
        self.assertFalse(a != c)
