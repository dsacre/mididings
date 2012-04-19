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


class SetupTestCase(MididingsTestCase):

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
        config(in_ports=['foo', ['bar', 'blah']])
        config(in_ports=['foo', ('bar', 'blah', 'blubb')])
        with self.assertRaises(TypeError):
            config(in_ports='foo')
        with self.assertRaises(TypeError):
            config(in_ports=[23, 42])
#        with self.assertRaises(ValueError):
        with self.assertRaises(TypeError):
            config(in_ports=-1)

    def test_config_out_ports(self):
        config(out_ports=23)
        config(out_ports=['foo', 'bar'])
        config(out_ports=['foo', ['bar', 'blah']])
        config(out_ports=['foo', ('bar', 'blah', 'blubb')])
        with self.assertRaises(TypeError):
            config(out_ports='foo')
        with self.assertRaises(TypeError):
            config(out_ports=[23, 42])
#        with self.assertRaises(ValueError):
        with self.assertRaises(TypeError):
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

    @data_offsets
    def test_named_ports(self, off):
        config(out_ports = ['foo', 'bar', 'baz'])
        ev = self.make_event(port=off(0))

        self.check_patch(Port('bar'), {
            ev : [self.modify_event(ev, port=off(1))],
        })
