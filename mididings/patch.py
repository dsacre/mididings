# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import _mididings
import main
import units
import misc


class Patch(_mididings.Patch):
    def __init__(self, p):
        _mididings.Patch.__init__(self, self.build(p))

    def build(self, p):
        if isinstance(p, units._Chain):
            v = Patch.ModuleVector()
            for i in p.units:
                v.push_back(self.build(i))
            return Patch.Chain(v)

        elif isinstance(p, list):
            v = Patch.ModuleVector()
            for i in p:
                v.push_back(self.build(i))

            if hasattr(p, 'remove_duplicates') and p.remove_duplicates != None:
                r = p.remove_duplicates
            else:
                r = main._config['remove_duplicates']

            return Patch.Fork(v, r)

        elif isinstance(p, dict):
            return self.build([
                units.Filter(t) >> w for t, w in p.items()
            ])

        elif isinstance(p, units.InitAction):
            return self.build(p.proc)

        elif isinstance(p, units._Unit):
            return Patch.Single(p)

        raise TypeError("type '%s' not allowed in patch" % type(p).__name__)



def get_init_actions(patch):
    if isinstance(patch, units._Chain):
        r = [get_init_actions(p) for p in patch.units]

    elif isinstance(patch, list):
        r = [get_init_actions(p) for p in patch]

    elif isinstance(patch, dict):
        r = [get_init_actions(p) for p in patch.values()]

    elif isinstance(patch, units.InitAction):
        r = [patch.init]

    else:
        r = []

    return misc.flatten(r)
