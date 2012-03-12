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
from mididings.event import *


class EngineTestCase(tests.helpers.MididingsTestCase):

    def testSanitize(self):
        def foo(ev):
            ev.port = 42
        def bar(ev):
            self.fail()
        p = Process(foo) >> Sanitize() >> Process(bar)
        self.run_patch(p, self.make_event(port=42))

        p = Velocity(+666) >> Sanitize()
        r = self.run_patch(p, self.make_event(NOTEON, velocity=42))
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].data2, 127)

    def testSceneSwitch(self):
        config(silent=True)
        p = {
            0:  Split({
                    PROGRAM:  SceneSwitch(),
                    ~PROGRAM: Channel(7),
                }),
            1: Channel(13),
        }
        events = (
            self.make_event(NOTEON, 0, 0, 69, 123),
            self.make_event(PROGRAM, 0, 0, 0, 1),
            self.make_event(NOTEON, 0, 0, 23, 42),
            self.make_event(NOTEOFF, 0, 0, 69, 0),
        )
        results = [
            self.make_event(NOTEON, 0, 7, 69, 123),
            self.make_event(NOTEON, 0, 13, 23, 42),
            self.make_event(NOTEOFF, 0, 7, 69, 0),
        ]
        self.check_scenes(p, {
            events: results,
        })
