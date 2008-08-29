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

from mididings import *


# suppress program change if the program is the same as the one previously selected on this port/channel

class _Suppressor:
    def __init__(self):
        self.current = { }
    def __call__(self, ev):
        k = (ev.port, ev.channel)
        if k in self.current and self.current[k] == ev.program:
            return False
        else:
            self.current[k] = ev.program
            return True


def SuppressPC():
    return Split({ PROGRAM: Call(_Suppressor()), ~PROGRAM: Pass() })
