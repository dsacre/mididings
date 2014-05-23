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

import mididings as _m
from mididings.extra.per_channel import PerChannel as _PerChannel


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
    """
    Filter out program changes if the same program has already
    been selected on the same port/channel.
    """
    return (_m.Filter(_m.PROGRAM) %
        _m.Process(_PerChannel(_SuppressPC)))
