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

from mididings import *
from mididings.extra import PerChannel


class _SuppressPC(object):
    def __init__(self):
        self.current = None
    def __call__(self, ev):
        if ev.program == self.current:
            return None
        else:
            self.current = ev.program
            return ev


def SuppressPC():
    return Filter(PROGRAM) % Process(PerChannel(_SuppressPC))
