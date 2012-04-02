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

import _mididings

import mididings.units as _units


class Patch(_mididings.Patch):
    def __init__(self, p):
        _mididings.Patch.__init__(self, self.build(p))

    def build(self, p):
        if isinstance(p, _units.base._Chain):
            return Patch.Chain(self.build(i) for i in p)

        elif isinstance(p, list):
            gen = (self.build(i) for i in p)

            remove_duplicates = True
            if hasattr(p, 'remove_duplicates'):
                remove_duplicates = (p.remove_duplicates != False)

            return Patch.Fork(gen, remove_duplicates)

        elif isinstance(p, dict):
            return self.build(
                _units.splits._make_split(_units.base.Filter, p, unpack=True)
            )

        elif isinstance(p, _units.init._Init):
            return Patch.Single(_mididings.Pass(False))

        elif isinstance(p, _units.base._Unit):
            if isinstance(p.unit, _mididings.Unit):
                return Patch.Single(p.unit)
            elif isinstance(p.unit, _mididings.UnitEx):
                return Patch.Extended(p.unit)

        message = "type '%s' not allowed in patch. offending object is: %r" % (type(p).__name__, p)
        raise TypeError(message)


def get_init_patches(patch):
    if isinstance(patch, _units.base._Chain):
        return flatten([get_init_patches(p) for p in patch])

    elif isinstance(patch, list):
        return flatten([get_init_patches(p) for p in patch])

    elif isinstance(patch, dict):
        return flatten([get_init_patches(p) for p in patch.values()])

    elif isinstance(patch, _units.init._Init):
        return [patch.init_patch]

    else:
        return []


def flatten(patch):
    r = []
    for i in patch:
        if isinstance(i, list) and not isinstance(i, _units.base._Chain):
            r.extend(i)
        else:
            r.append(i)
    return r
