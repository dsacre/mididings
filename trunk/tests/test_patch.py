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


class PatchTestCase(MididingsTestCase):

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
