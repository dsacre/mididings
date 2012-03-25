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
from mididings import engine


class EngineTestCase(MididingsTestCase):

    def test_in_ports(self):
        ports = ['foo', 'bar', 'baz']
        config(in_ports = ports)
        self.assertEqual(engine.in_ports(), ports)

        config(in_ports = 3)
        self.assertEqual(engine.in_ports(), ['in_0', 'in_1', 'in_2'])

    def test_out_ports(self):
        ports = ['foo', 'bar', 'baz']
        config(out_ports = ports)
        self.assertEqual(engine.out_ports(), ports)

        config(out_ports = 3)
        self.assertEqual(engine.out_ports(), ['out_0', 'out_1', 'out_2'])

    def test_active(self):
        self.assertFalse(engine.active())

        def foo(ev):
            self.assertTrue(engine.active())

        self.run_patch(Process(foo), self.make_event())
