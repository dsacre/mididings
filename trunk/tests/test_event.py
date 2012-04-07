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
from mididings.event import *
import mididings.constants

import copy
import pickle


class EventTestCase(MididingsTestCase):

    @data_offsets
    def test_NoteOnEvent(self, off):
        ev = NoteOnEvent(off(1), off(7), 60, 127)

        def foo(ev):
            self.assertEqual(ev.type, NOTEON)
            self.assertEqual(ev.port, off(1))
            self.assertEqual(ev.port_, 1)
            self.assertEqual(ev.channel, off(7))
            self.assertEqual(ev.channel_, 7)
            self.assertEqual(ev.note, 60)
            self.assertEqual(ev.data1, 60)
            self.assertEqual(ev.velocity, 127)
            self.assertEqual(ev.data2, 127)
            ev.port = off(3)
            ev.channel = off(5)
            ev.note = 69
            ev.velocity = 42
            return ev

        (r,) = self.run_patch(Process(foo), ev)

        self.assertEqual(r.type, NOTEON)
        self.assertEqual(r.port, off(3))
        self.assertEqual(r.port_, 3)
        self.assertEqual(r.channel, off(5))
        self.assertEqual(r.channel_, 5)
        self.assertEqual(r.note, 69)
        self.assertEqual(r.data1, 69)
        self.assertEqual(r.velocity, 42)
        self.assertEqual(r.data2, 42)
        with self.assertRaises(AttributeError): r.ctrl
        with self.assertRaises(AttributeError): r.value
        with self.assertRaises(AttributeError): r.program
        with self.assertRaises(AttributeError): r.sysex

    @data_offsets
    def test_NoteOffEvent(self, off):
        ev = NoteOffEvent(off(1), off(7), 60, 127)

        def foo(ev):
            self.assertEqual(ev.type, NOTEOFF)
            self.assertEqual(ev.port, off(1))
            self.assertEqual(ev.port_, 1)
            self.assertEqual(ev.channel, off(7))
            self.assertEqual(ev.channel_, 7)
            self.assertEqual(ev.note, 60)
            self.assertEqual(ev.data1, 60)
            self.assertEqual(ev.velocity, 127)
            self.assertEqual(ev.data2, 127)
            ev.port = off(3)
            ev.channel = off(5)
            ev.note = 69
            ev.velocity = 42
            return ev

        (r,) = self.run_patch(Process(foo), ev)

        self.assertEqual(r.type, NOTEOFF)
        self.assertEqual(r.port, off(3))
        self.assertEqual(r.port_, 3)
        self.assertEqual(r.channel, off(5))
        self.assertEqual(r.channel_, 5)
        self.assertEqual(r.note, 69)
        self.assertEqual(r.data1, 69)
        self.assertEqual(r.velocity, 42)
        self.assertEqual(r.data2, 42)
        with self.assertRaises(AttributeError): r.ctrl
        with self.assertRaises(AttributeError): r.value
        with self.assertRaises(AttributeError): r.program
        with self.assertRaises(AttributeError): r.sysex

    @data_offsets
    def test_CtrlEvent(self, off):
        ev = CtrlEvent(off(1), off(7), 60, 127)

        def foo(ev):
            self.assertEqual(ev.type, CTRL)
            self.assertEqual(ev.port, off(1))
            self.assertEqual(ev.port_, 1)
            self.assertEqual(ev.channel, off(7))
            self.assertEqual(ev.channel_, 7)
            self.assertEqual(ev.ctrl, 60)
            self.assertEqual(ev.data1, 60)
            self.assertEqual(ev.value, 127)
            self.assertEqual(ev.data2, 127)
            ev.port = off(3)
            ev.channel = off(5)
            ev.ctrl = 69
            ev.value = 42
            return ev

        (r,) = self.run_patch(Process(foo), ev)

        self.assertEqual(r.type, CTRL)
        self.assertEqual(r.port, off(3))
        self.assertEqual(r.port_, 3)
        self.assertEqual(r.channel, off(5))
        self.assertEqual(r.channel_, 5)
        self.assertEqual(r.ctrl, 69)
        self.assertEqual(r.data1, 69)
        self.assertEqual(r.value, 42)
        self.assertEqual(r.data2, 42)
        with self.assertRaises(AttributeError): r.note
        with self.assertRaises(AttributeError): r.velocity
        with self.assertRaises(AttributeError): r.program
        with self.assertRaises(AttributeError): r.sysex

    @data_offsets
    def test_ProgramEvent(self, off):
        ev = ProgramEvent(off(1), off(7), off(42))

        def foo(ev):
            self.assertEqual(ev.type, PROGRAM)
            self.assertEqual(ev.port, off(1))
            self.assertEqual(ev.port_, 1)
            self.assertEqual(ev.channel, off(7))
            self.assertEqual(ev.channel_, 7)
            self.assertEqual(ev.program, off(42))
            self.assertEqual(ev.data2, 42)
            ev.port = off(3)
            ev.channel = off(5)
            ev.program = off(66)
            return ev

        (r,) = self.run_patch(Process(foo), ev)

        self.assertEqual(r.type, PROGRAM)
        self.assertEqual(r.port, off(3))
        self.assertEqual(r.port_, 3)
        self.assertEqual(r.channel, off(5))
        self.assertEqual(r.channel_, 5)
        self.assertEqual(r.program, off(66))
        self.assertEqual(r.data2, 66)
        with self.assertRaises(AttributeError): r.note
        with self.assertRaises(AttributeError): r.velocity
        with self.assertRaises(AttributeError): r.ctrl
        with self.assertRaises(AttributeError): r.value
        with self.assertRaises(AttributeError): r.sysex

    @data_offsets
    def test_SysExEvent(self, off):
        sysex1 = '\xf0\x04\x08\x15\x16\x23\x42\xf7'
        sysex2 = '\xf0\x09\x11\x02\x74\x5b\x41\x56\x63\x56\xf7'
        ev = SysExEvent(off(1), sysex1)

        def foo(ev):
            self.assertEqual(ev.type, SYSEX)
            self.assertEqual(ev.port, off(1))
            self.assertEqual(ev.sysex, self.native_sysex(sysex1))
            ev.port = off(3)
            ev.sysex = sysex2
            return ev

        (r,) = self.run_patch(Process(foo), ev)

        self.assertEqual(r.type, SYSEX)
        self.assertEqual(r.port, off(3))
        self.assertEqual(r.port_, 3)
        self.assertEqual(r.sysex, self.native_sysex(sysex2))
        with self.assertRaises(AttributeError): ev.note
        with self.assertRaises(AttributeError): ev.velocity
        with self.assertRaises(AttributeError): ev.ctrl
        with self.assertRaises(AttributeError): ev.value
        with self.assertRaises(AttributeError): ev.program

    @data_offsets
    def test_SysExEvent_modify(self, off):
        sysex1 = '\xf0\x04\x08\x15\x16\x23\x42\xf7'
        sysex2 = '\xf0\x05\x08\x15\x16\x23\x42\xf7'
        ev = SysExEvent(off(1), sysex1)

        def foo(ev):
            ev.sysex[1] = 0x05
            return ev

        (r,) = self.run_patch(Process(foo), ev)

        self.assertEqual(r.sysex, self.native_sysex(sysex2))

    @data_offsets
    def test_operator_equals(self, off):
        for t in constants._EVENT_TYPES.values():
            a = self.make_event(type=t, port=off(0))
            b = self.make_event(type=t, port=off(1))
            c = self.make_event(type=a.type, port=a.port, channel=a.channel, data1=a.data1, data2=a.data2, sysex=a.sysex_)

            self.assertNotEqual(a, b)
            self.assertFalse(a == b)
            self.assertTrue(a != b)

            self.assertEqual(a, c)
            self.assertTrue(a == c)
            self.assertFalse(a != c)

    @data_offsets
    def test_to_string(self, off):
        for t in constants._EVENT_TYPES.values():
            ev = self.make_event(t)
            self.assertTrue(isinstance(ev.to_string(), str))
            self.assertTrue(isinstance(ev.to_string(['foo', 'bar'], 3, 80), str))

    @data_offsets
    def test_rebuild_repr(self, off):
        for t in constants._EVENT_TYPES.values():
            ev = self.make_event(t)
            rebuilt = eval(repr(ev), self.mididings_dict)
            self.assertEqual(rebuilt, ev)
            self.assertEqual(repr(ev), repr(rebuilt))

    @data_offsets
    def test_copy(self, off):
        a = self.make_event()
        b = copy.copy(a)

        self.assertEqual(b, a)

        c = SysExEvent(off(23), '\xf0\x04\x08\x15\x16\x23\x42\xf7')
        d = copy.copy(c)

        self.assertEqual(d, c)

    @data_offsets
    def test_pickle(self, off):
        a = self.make_event()
        b = pickle.loads(pickle.dumps(a))

        self.assertEqual(b, a)

        c = SysExEvent(off(23), '\xf0\x04\x08\x15\x16\x23\x42\xf7')
        d = pickle.loads(pickle.dumps(c))

        self.assertEqual(d, c)
