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

import tests.helpers

from mididings import *


class BaseTestCase(tests.helpers.MididingsTestCase):

    def test_Pass(self):
        self.check_patch(Pass(), {
            self.make_event(): True,
        })
        self.check_patch(Discard(), {
            self.make_event(): False,
        })

    def test_Fork(self):
        ev = self.make_event(channel=2)

        p = Fork([Pass(), Pass()])
        self.check_patch(p, {ev: True})

        p = Pass() // Pass()
        self.check_patch(p, {ev: True})

        p = +Channel(3)
        self.check_patch(p, {ev: [ev, self.modify_event(ev, channel=3)]})

        p = Fork([Pass(), Discard(), Pass()])
        self.check_patch(p, {ev: [ev]})

        p = Fork([Pass(), Pass()], remove_duplicates=False)
        self.check_patch(p, {ev: [ev, ev]})

        p = Fork([Pass(), Discard(), Pass()], remove_duplicates=False)
        self.check_patch(p, {ev: [ev, ev]})

    def test_Filter(self):
        self.check_filter(Filter(PROGRAM), {
            self.make_event(NOTEON): (False, True),
            self.make_event(NOTEOFF): (False, True),
            self.make_event(CTRL): (False, True),
            self.make_event(PROGRAM): (True, False),
        })

        self.check_filter(Filter(NOTE), {
            self.make_event(NOTEON): (True, False),
            self.make_event(NOTEOFF): (True, False),
            self.make_event(CTRL): (False, True),
            self.make_event(PROGRAM): (False, True),
        })

        self.check_filter(Filter(NOTE, CTRL, AFTERTOUCH), {
            self.make_event(NOTEON): (True, False),
            self.make_event(NOTEOFF): (True, False),
            self.make_event(CTRL): (True, False),
            self.make_event(PROGRAM): (False, True),
        })

    def test_Split(self):
        ev1 = self.make_event(NOTEON, channel=1)
        ev2 = self.make_event(PROGRAM, channel=2)
        ev3 = self.make_event(CTRL)

        p = Split({ NOTE: Channel(4), PROGRAM: Channel(8) })
        self.check_patch(p, {
            ev1: [self.modify_event(ev1, channel=4)],
            ev2: [self.modify_event(ev2, channel=8)],
            ev3: [],
        })

    def test_Selector(self):
        p = CtrlFilter(23) % CtrlValueFilter(123)
        self.check_patch(p, {
            self.make_event(NOTEON): True,
            self.make_event(CTRL, ctrl=23, value=42): False,
            self.make_event(CTRL, ctrl=42, value=123): True,
        })

        p = CtrlFilter(42) % CtrlValueFilter(123)
        self.check_patch(p, {
            self.make_event(NOTEON): True,
            self.make_event(CTRL, ctrl=23, value=42): True,
            self.make_event(CTRL, ctrl=42, value=123): True,
        })

        p = (Filter(CTRL) & CtrlFilter(42) & CtrlValueFilter(123)) % Discard()
        self.check_patch(p, {
            self.make_event(NOTEON): True,
            self.make_event(CTRL, ctrl=23, value=42): True,
            self.make_event(CTRL, ctrl=42, value=123): False,
        })

        p = (CtrlFilter(42) | CtrlValueFilter(123)) % Discard()
        self.check_patch(p, {
#            self.make_event(NOTEON): False,
            self.make_event(NOTEON): True,
            self.make_event(CTRL, ctrl=23, value=42): True,
            self.make_event(CTRL, ctrl=42, value=123): False,
        })

        p = (Filter(NOTE) | (CtrlFilter(42) & CtrlValueFilter(123))) % Discard()
        self.check_patch(p, {
            self.make_event(NOTEON): False,
            self.make_event(CTRL, ctrl=23, value=42): True,
            self.make_event(CTRL, ctrl=42, value=123): False,
        })

        p = CtrlFilter(42) % (CtrlValueFilter(123) % Discard())
        self.check_patch(p, {
#            self.make_event(NOTEON): False,
            self.make_event(NOTEON): True,
            self.make_event(CTRL, ctrl=23, value=42): True,
            self.make_event(CTRL, ctrl=42, value=123): False,
        })

    def test_unit_order(self):
        def me_impl(ev, n):
            order.append(n)
            return ev

        def me(n):
            return Process(lambda ev: me_impl(ev, n))

        order = []
        p = ([ me(1), me(2) ] >> me(3) >>
             [ me(4), me(5) >> [ me(6), me(7) ] >> me(8) ] >> me(9))
        self.run_patch(p, self.make_event())
        self.assertEqual(order, [1, 2, 3, 4, 5, 6, 7, 8, 9])

        order = []
        p = (Fork([ me(1), me(2) ], False) >> me(3) >>
             Fork([ me(4), me(5) >> Fork([ me(6), me(7) ], False) >> me(8) ], False) >> me(9))

        self.run_patch(p, self.make_event())
        self.assertEqual(order, [1, 2, 3, 3, 4, 5, 6, 7, 8, 8, 4, 5, 6, 7, 8, 8, 9, 9, 9, 9, 9, 9])
