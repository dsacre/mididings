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

    def test_data_offset(self):
        ev = self.make_event(PROGRAM, 0, 6, 0, 41)

        config(data_offset = 1)

        def foo(ev):
            self.assertEqual(ev.port, 1)
            self.assertEqual(ev.port_, 0)
            self.assertEqual(ev.channel, 7)
            self.assertEqual(ev.channel_, 6)
            self.assertEqual(ev.program, 42)
            self.assertEqual(ev.data2, 41)
            ev.port = 3
            ev.channel = 5
            ev.program = 66
            return ev

        r = self.run_patch(Process(foo), ev)

        self.assertEqual(r[0].port_, 2)
        self.assertEqual(r[0].channel_, 4)
        self.assertEqual(r[0].data2, 65)

    def test_named_ports(self):
        config(out_ports = ['foo', 'bar', 'baz'])
        ev = self.make_event(port=0)

        self.check_patch(Port('bar'), {
            ev : [self.modify_event(ev, port=1)],
        })
