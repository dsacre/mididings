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

# populate this module with midi event type constants
for _name, _value in _mididings.MidiEventType.names.items():
    _type_object = _EventType(int(_value), _name)

    # add event type object to this module's global namespace
    globals()[_name] = _type_object

    # only masks matching a single event type (exactly one bit set) are added
    # to the event types dict
    if len([_x for _x in range(32) if _value & (1 << _x)]) == 1:
        _EVENT_TYPES[int(_value)] = _type_object


# populate this module with midi event attribute constants
for _name, _value in _mididings.EventAttribute.names.items():
    _attribute_object = _EventAttribute(int(_value), "EVENT_" + _name)

    # add event attribute object to this module's global namespace
    globals()["EVENT_" + _name] = _attribute_object
