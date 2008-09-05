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

from .base import _Filter

from .. import util as _util
from .. import misc as _misc


class PortFilter(_mididings.PortFilter, _Filter):
    def __init__(self, *args):
        v = _misc.make_int_vector((_util.port_number(p) for p in _misc.flatten(args)))
        _mididings.PortFilter.__init__(self, v)


class ChannelFilter(_mididings.ChannelFilter, _Filter):
    def __init__(self, *args):
        v = _misc.make_int_vector((_util.channel_number(c) for c in _misc.flatten(args)))
        _mididings.ChannelFilter.__init__(self, v)


class KeyFilter(_mididings.KeyFilter, _Filter):
    def __init__(self, *args):
        if len(args) == 1:
            args = args[0]
        r = _util.note_range(args)
        _mididings.KeyFilter.__init__(self, r[0], r[1])


class VelocityFilter(_mididings.VelocityFilter, _Filter):
    def __init__(self, *args):
        if len(args) == 1:
            args = args[0]
        _mididings.VelocityFilter.__init__(self, args[0], args[1])


class CtrlFilter(_mididings.CtrlFilter, _Filter):
    def __init__(self, *args):
        v = _misc.make_int_vector(_misc.flatten(args))
        _mididings.CtrlFilter.__init__(self, v)


class CtrlValueFilter(_mididings.CtrlValueFilter, _Filter):
    def __init__(self, lower, upper=0):
        _mididings.CtrlValueFilter.__init__(self, lower, upper)


class ProgFilter(_mididings.ProgFilter, _Filter):
    def __init__(self, *args):
        v = _misc.make_int_vector((_util.program_number(p) for p in _misc.flatten(args)))
        _mididings.ProgFilter.__init__(self, v)
