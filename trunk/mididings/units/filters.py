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

import _mididings

from mididings.units.base import _Filter

from mididings import util as _util
from mididings import misc as _misc


class PortFilter(_Filter):
    def __init__(self, *args):
        v = _misc.make_int_vector((_util.port_number(p) for p in _misc.flatten(args)))
        _Filter.__init__(self, _mididings.PortFilter(v))


class ChannelFilter(_Filter):
    def __init__(self, *args):
        v = _misc.make_int_vector((_util.channel_number(c) for c in _misc.flatten(args)))
        _Filter.__init__(self, _mididings.ChannelFilter(v))


class KeyFilter(_Filter):
    def __init__(self, *args):
        if len(args) == 1:
            args = args[0]
        r = _util.note_range(args)
        _Filter.__init__(self, _mididings.KeyFilter(r[0], r[1]))


class VelocityFilter(_Filter):
    def __init__(self, *args):
        if len(args) == 1:
            args = args[0]
        _Filter.__init__(self, _mididings.VelocityFilter(args[0], args[1]))


class CtrlFilter(_Filter):
    def __init__(self, *args):
        v = _misc.make_int_vector(_util.ctrl_number(c) for c in _misc.flatten(args))
        _Filter.__init__(self, _mididings.CtrlFilter(v))


class CtrlValueFilter(_Filter):
    def __init__(self, lower, upper=0):
        _Filter.__init__(self, _mididings.CtrlValueFilter(_util.ctrl_value(lower), _util.ctrl_value(upper)))


class ProgFilter(_Filter):
    def __init__(self, *args):
        v = _misc.make_int_vector(_util.program_number(p) for p in _misc.flatten(args))
        _Filter.__init__(self, _mididings.ProgFilter(v))
