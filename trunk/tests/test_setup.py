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

    def test_config_backend(self):
        config(backend='alsa')
        config(backend='jack')
        config(backend='jack-rt')
        with self.assertRaises(ValueError):
            config(backend='unknown')
        with self.assertRaises(ValueError):
            config(backend=666)

    def test_config_client_name(self):
        config(client_name='foo')
        with self.assertRaises(TypeError):
            config(client_name=666)

    def test_config_in_ports(self):
        config(in_ports=23)
        config(in_ports=['foo', 'bar'])
        with self.assertRaises(TypeError):
            config(in_ports=[23, 42])
        with self.assertRaises(ValueError):
            config(in_ports=-1)

    def test_config_out_ports(self):
        config(out_ports=23)
        config(out_ports=['foo', 'bar'])
        with self.assertRaises(TypeError):
            config(out_ports=[23, 42])
        with self.assertRaises(ValueError):
            config(out_ports=-1)

    def test_config_data_offset(self):
        config(data_offset=0)
        config(data_offset=1)
        with self.assertRaises(ValueError):
            config(data_offset=-1)
        with self.assertRaises(ValueError):
            config(data_offset=2)

    def test_config_octave_offset(self):
        for x in range(-3, 5):
            config(octave_offset=x)
        with self.assertRaises(TypeError):
            config(octave_offset=1.5)

    def test_config_initial_scene(self):
        config(initial_scene=4)
        config(initial_scene=(8,))
        config(initial_scene=(15,16))

    def test_config_start_delay(self):
        config(start_delay=None)
        config(start_delay=0)
        config(start_delay=1.23)


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
