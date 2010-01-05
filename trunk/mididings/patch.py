# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2010  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import _mididings
import mididings.units as _units


class Patch(_mididings.Patch):
    def __init__(self, p):
        _mididings.Patch.__init__(self, self.build(p))

    def build(self, p):
        if isinstance(p, _units.base.Chain):
            v = Patch.ModuleVector()
            for i in p:
                v.push_back(self.build(i))
            return Patch.Chain(v)

        elif isinstance(p, list):
            v = Patch.ModuleVector()
            for i in p:
                v.push_back(self.build(i))

            if hasattr(p, 'remove_duplicates'):
                return Patch.Fork(v, p.remove_duplicates != False)
            else:
                return Patch.Fork(v, True)

        elif isinstance(p, dict):
            return self.build([
                _units.base.Filter(t) >> w for t, w in p.items()
            ])

        elif isinstance(p, _units.init_action._InitAction):
            return Patch.Single(_mididings.Pass(False))

        elif isinstance(p, _units.base._Unit):
            if isinstance(p.unit, _mididings.Unit):
                return Patch.Single(p.unit)
            elif isinstance(p.unit, _mididings.UnitEx):
                return Patch.Extended(p.unit)

        raise TypeError("type '%s' not allowed in patch:\n"
                        "offending object is: %s" % (type(p).__name__, repr(p)))


def get_init_actions(patch):
    if isinstance(patch, _units.base.Chain):
        return flatten([get_init_actions(p) for p in patch])

    elif isinstance(patch, list):
        return flatten([get_init_actions(p) for p in patch])

    elif isinstance(patch, dict):
        return flatten([get_init_actions(p) for p in patch.values()])

    elif isinstance(patch, _units.init_action._InitAction):
        return [patch.action]

    else:
        return []


def flatten(patch):
    r = []
    for i in patch:
        if isinstance(i, list) and not isinstance(i, _units.base.Chain):
            r.extend(i)
        else:
            r.append(i)
    return r
