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
from mididings.util import *


class UtilTestCase(MididingsTestCase):

    def test_note_number(self):
        config(octave_offset=1)
        self.assertEqual(note_number(42), 42)
        self.assertEqual(note_number('c4'), 60)
        self.assertEqual(note_number('c#4'), 61)
        self.assertEqual(note_number('db4'), 61)
        self.assertEqual(note_number('a0'), 21)

        with self.assertRaises(ValueError):
            note_number(-23)
        with self.assertRaises(TypeError):
            note_number(123.456)
        with self.assertRaises(ValueError):
            note_number('a23')
        with self.assertRaises(ValueError):
            note_number('h3')

        config(octave_offset=2)
        self.assertEqual(note_number(42), 42)
        self.assertEqual(note_number('c3'), 60)
        self.assertEqual(note_number('c#3'), 61)
        self.assertEqual(note_number('db3'), 61)
        self.assertEqual(note_number('a-1'), 21)

    def test_note_range(self):
        self.assertEqual(note_range(23), (23, 24))
        self.assertEqual(note_range((23, 42)), (23, 42))
#        self.assertEqual(note_range('c3:c5'), (48, 72))
#        self.assertEqual(note_range(':c4'), (0, 60))
#        self.assertEqual(note_range('c2:'), (36, 0))
        self.assertEqual(note_range('c3:c5'), (60, 84))
        self.assertEqual(note_range(':c4'), (0, 72))
        self.assertEqual(note_range('c2:'), (48, 0))

        with self.assertRaises(ValueError):
            note_range('blah')
        with self.assertRaises(ValueError):
            note_range('x3:y5')
        with self.assertRaises(ValueError):
            note_range((23,))
        with self.assertRaises(ValueError):
            note_range(('c4',))

    def test_note_name(self):
        config(octave_offset=1)
        self.assertEqual(note_name(60), 'c4')
        self.assertEqual(note_name(61), 'c#4')
        self.assertEqual(note_name(0), 'c-1')
        self.assertEqual(note_name(-23), 'c#-3')
        self.assertEqual(note_name(127), 'g9')

        with self.assertRaises(TypeError):
            note_name(123.456)

    def test_event_type(self):
        self.assertEqual(event_type(NOTEON), NOTEON)
        self.assertEqual(event_type(PROGRAM), PROGRAM)

        with self.assertRaises(ValueError):
            event_type(NOTE)
        with self.assertRaises(ValueError):
            event_type(123)

    @data_offsets
    def test_port_number(self, off):
        config(
            in_ports=['foo', 'bar'],
            out_ports=['foo', 'blah', 'bar']
        )

        self.assertEqual(port_number(1), 1)
        self.assertEqual(port_number('foo'), off(0))
        self.assertEqual(port_number('blah'), off(1))

        with self.assertRaises(ValueError):
            port_number('bar')
        with self.assertRaises(TypeError):
            port_number(123.456)

    def test_sysex_data(self):
        self.assertEqual(sysex_data('\xf0\x04\x08\x15\x16\x23\x42\xf7'), self.native_sysex('\xf0\x04\x08\x15\x16\x23\x42\xf7'))
        self.assertEqual(sysex_data([0xf0, 0x04, 0x08, 0x15, 0x16, 0x23, 0x42, 0xf7]), self.native_sysex('\xf0\x04\x08\x15\x16\x23\x42\xf7'))
        self.assertEqual(sysex_data('\xf0\x23\x42\x66', allow_partial=True), self.native_sysex('\xf0\x23\x42\x66'))

        with self.assertRaises(ValueError):
            sysex_data('\xf0')
        with self.assertRaises(ValueError):
            sysex_data('\xfa\x23\x42\xf7')
        with self.assertRaises(ValueError):
            sysex_data('\xf0\x23\x42\xfa')
        with self.assertRaises(ValueError):
            sysex_data('\xf0\xff\xff\xfa')

    def test_sysex_manufacturer(self):
        self.assertEqual(sysex_manufacturer('\x42'), self.native_sysex('\x42'))
        self.assertEqual(sysex_manufacturer(0x42), self.native_sysex('\x42'))
        self.assertEqual(sysex_manufacturer('\x00\x42\x23'), self.native_sysex('\x00\x42\x23'))
        self.assertEqual(sysex_manufacturer([0x00, 0x42, 0x23]), self.native_sysex('\x00\x42\x23'))

        with self.assertRaises(ValueError):
            sysex_manufacturer('\x42\x23')
        with self.assertRaises(ValueError):
            sysex_manufacturer('\x42\x00\x23')
        with self.assertRaises(ValueError):
            sysex_manufacturer('\x00\x23\xff')
