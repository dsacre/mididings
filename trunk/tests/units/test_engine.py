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


class EngineTestCase(MididingsTestCase):

    @data_offsets
    def testSanitize(self, off):
        def foo(ev):
            ev.port = off(42)
        def bar(ev):
            self.fail()
        p = Process(foo) >> Sanitize() >> Process(bar)
        self.run_patch(p, self.make_event(port=off(42)))

        p = Velocity(+666) >> Sanitize()
        r = self.run_patch(p, self.make_event(NOTEON, velocity=42))
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].data2, 127)

    @data_offsets
    def testSceneSwitch(self, off):
        config(silent=True)
        p = {
            off(0): Split({
                        PROGRAM:  SceneSwitch(),
                        ~PROGRAM: Channel(off(7)),
                    }),
            off(1): Channel(off(13)),
        }
        events = (
            self.make_event(NOTEON, off(0), off(0), 69, 123),
            self.make_event(PROGRAM, off(0), off(0), 0, 1),   # no data offset!
            self.make_event(NOTEON, off(0), off(0), 23, 42),
            self.make_event(NOTEOFF, off(0), off(0), 69, 0),
        )
        results = [
            self.make_event(NOTEON, off(0), off(7), 69, 123),
            self.make_event(NOTEON, off(0), off(13), 23, 42),
            self.make_event(NOTEOFF, off(0), off(7), 69, 0),
        ]
        self.check_scenes(p, {
            events: results,
        })
