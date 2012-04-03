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

import _mididings

from mididings.misc import NamedFlag as _NamedFlag
from mididings.misc import NamedBitMask as _NamedBitMask


class _EventType(_NamedBitMask):
    pass


class _EventAttribute(_NamedFlag):
    pass


_EVENT_TYPES = {}

for _name, _value in _mididings.MidiEventType.names.items():
    _type_object = _EventType(int(_value), _name)
    # add event type object to this module's global namespace
    globals()[_name] = _type_object
    # only masks matching a single event type (exactly one bit set) are added
    # to the event types dict
    if len([x for x in range(32) if _value & (1 << x)]) == 1:
        _EVENT_TYPES[int(_value)] = _type_object


EVENT_PORT      = _EventAttribute(-1, 'EVENT_PORT')
EVENT_CHANNEL   = _EventAttribute(-2, 'EVENT_CHANNEL')
# generic
EVENT_DATA1     = _EventAttribute(-3, 'EVENT_DATA1')
EVENT_DATA2     = _EventAttribute(-4, 'EVENT_DATA2')
# note
EVENT_NOTE      = _EventAttribute(-3, 'EVENT_NOTE')
EVENT_VELOCITY  = _EventAttribute(-4, 'EVENT_VELOCITY')
# controller
EVENT_CTRL      = _EventAttribute(-3, 'EVENT_CTRL')
# for backward compatibility
EVENT_PARAM     = _EventAttribute(-3, 'EVENT_CTRL')
EVENT_PARAM._deprecated = True
EVENT_VALUE     = _EventAttribute(-4, 'EVENT_VALUE')
# program change
EVENT_PROGRAM   = _EventAttribute(-4, 'EVENT_PROGRAM')
