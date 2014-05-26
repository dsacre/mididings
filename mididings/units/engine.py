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

import _mididings

from mididings.units.base import _Unit

import mididings.constants as _constants
import mididings.util as _util
import mididings.overload as _overload
import mididings.unitrepr as _unitrepr


@_unitrepr.store
def Sanitize():
    """
    Sanitize()

    Make sure the event is a valid MIDI message.
    Events with invalid port (output), channel, controller, program or note
    number are discarded. Note velocity and controller values are confined to
    the range 0-127.
    """
    return _Unit(_mididings.Sanitize())


@_overload.mark(
    """
    SceneSwitch(number=EVENT_PROGRAM)
    SceneSwitch(offset=...)

    Switch to another scene.

    *number* can be a fixed scene number, or one of the
    :ref:`Event Attribute <event-attributes>` constants to use a value from
    the incoming event's data.
    With no arguments, the program number of the incoming event (which should
    be a program change) will be used.

    *offset* can be a positive or negative value that will be added to the
    current scene number, allowing you to go forward or backward in the list
    of scenes.
    """
)
@_unitrepr.accept(_util.scene_number_ref)
def SceneSwitch(number=_constants.EVENT_PROGRAM):
    return _Unit(_mididings.SceneSwitch(_util.actual_ref(number), 0))

@_overload.mark
@_unitrepr.accept(int)
def SceneSwitch(offset):
    return _Unit(_mididings.SceneSwitch(0, offset))


@_overload.mark(
    """
    SubSceneSwitch(number=EVENT_PROGRAM)
    SubSceneSwitch(offset=..., wrap=True)

    Switches between subscenes within a scene group.

    *number* can be a fixed subscene number, or one of the
    :ref:`Event Attribute <event-attributes>` constants to use a value from
    the incoming event's data.
    With no arguments, the program number of the incoming event (which should
    be a program change) will be used.

    *offset* can be a positive or negative value that will be added to the
    current subscene number, allowing you to go forward or backward in the
    list of subscenes. If *wrap* is ``True`` you can loop through subscenes.
    """
)
@_unitrepr.accept(_util.subscene_number_ref)
def SubSceneSwitch(number=_constants.EVENT_PROGRAM):
    return _Unit(_mididings.SubSceneSwitch(_util.actual_ref(number), 0, False))

@_overload.mark
@_unitrepr.accept(int, bool)
def SubSceneSwitch(offset, wrap=True):
    return _Unit(_mididings.SubSceneSwitch(0, offset, wrap))
