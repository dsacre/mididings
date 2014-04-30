# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2014  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

from mididings.units.base import _Unit, Fork, Chain, _UNIT_TYPES
from mididings.units.generators import Program, Ctrl
from mididings.units.modifiers import Port, Channel

import mididings.unitrepr as _unitrepr

import functools as _functools
import copy as _copy


class _InitExit(_Unit):
    def __init__(self, init_patch=[], exit_patch=[]):
        self.init_patch = init_patch
        self.exit_patch = exit_patch


@_unitrepr.accept(_UNIT_TYPES)
def Init(patch):
    return _InitExit(init_patch=patch)


@_unitrepr.accept(_UNIT_TYPES)
def Exit(patch):
    return _InitExit(exit_patch=patch)


def Output(port, channel, program=None, volume=None, pan=None, expression=None, ctrls={}):
    if isinstance(program, tuple):
        bank, program = program
    else:
        bank = None

    init = []

    if bank is not None:
        init.append(Ctrl(port, channel, 0, bank // 128))
        init.append(Ctrl(port, channel, 32, bank % 128))

    if program is not None:
        init.append(Program(port, channel, program))

    if volume is not None:
        init.append(Ctrl(port, channel, 7, volume))
    if pan is not None:
        init.append(Ctrl(port, channel, 10, pan))
    if expression is not None:
        init.append(Ctrl(port, channel, 11, expression))

    for k, v in ctrls.items():
        init.append(Ctrl(port, channel, k, v))

    return Fork([
        Init(init),
        Port(port) >> Channel(channel)
    ])


class OutputTemplate(object):
    def __init__(self, *args, **kwargs):
        self.partial = _functools.partial(Output, *args, **kwargs)
        self.before = []
        self.after = []

    def __call__(self, *args, **kwargs):
        return Chain(self.before) >> self.partial(*args, **kwargs) >> Chain(self.after)

    def __rshift__(self, other):
        if not isinstance(other, _UNIT_TYPES):
            return NotImplemented
        r = _copy.copy(self)
        r.after = self.after + [other]
        return r

    def __rrshift__(self, other):
        if not isinstance(other, _UNIT_TYPES):
            return NotImplemented
        r = _copy.copy(self)
        r.before = [other] + self.before
        return r
