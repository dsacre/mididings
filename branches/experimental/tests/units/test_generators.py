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


class GeneratorsTestCase(tests.helpers.MididingsTestCase):

    def test_Ctrl(self):
        ev = self.make_event(NOTEON)

        p = Ctrl(23, 42)
        self.check_patch(p, {
            ev: [self.make_event(CTRL, ev.port, ev.channel, 23, 42)],
        })
        p = Ctrl(23, EVENT_NOTE)
        self.check_patch(p, {
            ev: [self.make_event(CTRL, ev.port, ev.channel, 23, ev.note)],
        })
