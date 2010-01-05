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

from mididings.units.base import _Unit, Fork, _unit_repr
from mididings.units.generators import ProgChange, CtrlChange
from mididings.units.modifiers import Port, Channel


class _InitAction(_Unit):
    def __init__(self, action):
        self.action = action


@_unit_repr
def InitAction(action):
    return _InitAction(action)


def Output(port, channel, program=None, volume=None):
    if isinstance(program, tuple):
        bank, program = program
    else:
        bank = None

    init = []

    if bank != None:
        init.append(CtrlChange(port, channel, 0, bank // 128))
        init.append(CtrlChange(port, channel, 32, bank % 128))

    if program != None:
        init.append(ProgChange(port, channel, program))

    if volume != None:
        init.append(CtrlChange(port, channel, 7, volume))

    return Fork([
        InitAction(init),
        Port(port) >> Channel(channel)
    ])
