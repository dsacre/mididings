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


class CallTestCase(tests.helpers.MididingsTestCase):

    def test_Process(self):
        def foo(ev):
            self.assertEqual(ev.type, NOTEON)
            self.assertEqual(ev.port, 0)
            self.assertEqual(ev.channel, 0)
            self.assertEqual(ev.note, 66)
            self.assertEqual(ev.velocity, 23)
            ev.type = CTRL
            ev.port = 4
            ev.channel = 5
            ev.ctrl = 23
            ev.value = 42
            return ev

        self.check_patch(Process(foo), {
            self.make_event(NOTEON, 0, 0, 66, 23): [self.make_event(CTRL, 4, 5, 23, 42)],
        })

        ev = self.make_event()

        self.check_patch(Process(lambda ev: ev), {
            ev: [ev]
        })

        self.check_patch(Process(lambda ev: None), {
            ev: []
        })

        self.check_patch(Process(lambda ev: []), {
            ev: []
        })

        self.check_patch(Process(lambda ev: [ev, ev, ev]), {
            ev: [ev, ev, ev]
        })
