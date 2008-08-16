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

import _mididings

from base import *
from filters import *

from .. import event as _event


def PortSplit(d):
    return Fork([ (PortFilter(p) >> w) for p, w in d.items() ])

def ChannelSplit(d):
    return Fork([ (ChannelFilter(c) >> w) for c, w in d.items() ])


def KeySplit(*args):
    if len(args) == 1:
        # KeySplit(d)
#        return Fork([
#            (Fork([ KeyFilter(k), ~Filter(_event.NOTE) ]) >> w) for k, w in args[0].items()
#        ])
        return Fork([
            (KeyFilter(k) >> w) for k, w in args[0].items()
        ])
    elif len(args) == 3:
        # KeySplit(key, unit_lower, unit_upper)
        key, unit_lower, unit_upper = args
        filt = KeyFilter(0, key)
#        return Fork([
#            Fork([  filt, ~Filter(_event.NOTE) ]) >> unit_lower,
#            Fork([ ~filt, ~Filter(_event.NOTE) ]) >> unit_upper
#        ])
        return Fork([
            filt  >> unit_lower,
            ~filt >> unit_upper
        ])
    else:
        raise ArgumentError()


def VelocitySplit(*args):
    if len(args) == 1:
        # VelocitySplit(d)
        return Fork([
            (VelocityFilter(v) >> w) for v, w in args[0].items()
        ])
    elif len(args) == 3:
        # VelocitySplit(thresh, unit_lower, unit_upper)
        thresh, unit_lower, unit_upper = args
        filt = VelocityFilter(0, thresh)
        return Fork([
            filt  >> unit_lower,
            ~filt >> unit_upper
        ])
    else:
        raise ArgumentError()
