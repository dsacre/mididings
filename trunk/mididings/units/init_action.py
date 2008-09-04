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

from base import *
from base import _Unit
from generators import *
from modifiers import *


class InitAction(_Unit):
    def __init__(self, action):
        self.action = action


def Output(port, channel, program=None):
    if program != None:
        return Fork([
            InitAction(ProgChange(port, channel, program)),
            Port(port) >> Channel(channel),
        ])
    else:
        return Port(port) >> Channel(channel)

