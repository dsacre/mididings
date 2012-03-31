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


class CallTestCase(MididingsTestCase):

    @data_offsets
    def test_Process(self, off):
        def foo(ev):
            self.assertEqual(ev.type, NOTEON)
            self.assertEqual(ev.port, off(0))
            self.assertEqual(ev.channel, off(0))
            self.assertEqual(ev.note, 66)
            self.assertEqual(ev.velocity, 23)
            ev.type = CTRL
            ev.port = off(4)
            ev.channel = off(5)
            ev.ctrl = 23
            ev.value = 42
            return ev

        self.check_patch(Process(foo), {
            self.make_event(NOTEON, off(0), off(0), 66, 23): [self.make_event(CTRL, off(4), off(5), 23, 42)],
        })

    def test_Process_return(self):
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

        self.check_patch(Process(lambda ev: (ev for ev in [ev, ev])), {
            ev: [ev, ev]
        })
