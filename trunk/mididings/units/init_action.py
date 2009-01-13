# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2009  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

from .base import _Unit, Fork
from .generators import ProgChange, CtrlChange
from .modifiers import Port, Channel


class InitAction(_Unit):
    def __init__(self, action):
        self.action = action


def Output(port, channel, program=None, bank=None):
    if bank != None:
        return Fork([
            InitAction([
                CtrlChange(port, channel, 0, bank // 128),
                CtrlChange(port, channel, 32, bank % 128),
                ProgChange(port, channel, program),
            ]),
            Port(port) >> Channel(channel),
        ])
    elif program != None:
        return Fork([
            InitAction(ProgChange(port, channel, program)),
            Port(port) >> Channel(channel),
        ])
    else:
        return Port(port) >> Channel(channel)
