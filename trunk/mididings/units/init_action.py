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
    def __init__(self, init, proc=Discard()):
        self.init = init
        self.proc = proc


class Output(InitAction):
    def __init__(self, port, channel, program=None):
        InitAction.__init__(self,
            ProgChange(port, channel, program) if program != None else None,
            Port(port) >> Channel(channel),
        )
