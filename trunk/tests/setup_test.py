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


class SetupTestCase(tests.helpers.MididingsTestCase):

    def test_DataOffset(self):
        config(data_offset = 1)
        p = Channel(6)
        ev = MidiEvent(PROGRAM, 1, 1, 0, 41)
        self.assertEqual(ev.channel_, 0)
        self.assertEqual(ev.data2, 41)
        def foo(ev):
            self.assertEqual(ev.channel, 1)
            self.assertEqual(ev.channel_, 0)
            self.assertEqual(ev.program, 42)
            self.assertEqual(ev.data2, 41)
            ev.channel = 6
        r = self.run_patch(p, ev)
        self.assertEqual(r[0].channel_, 5)

    def test_NamedPorts(self):
        config(out_ports = ['foo', 'bar', 'baz'])
        ev = self.make_event(port=0)

        self.check_patch(Port('bar'), {
            ev : [self.modify_event(ev, port=1)],
        })
