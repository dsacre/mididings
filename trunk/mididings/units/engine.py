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

from mididings.units.base import _Unit, _unit_repr

import mididings.constants as _constants
import mididings.util as _util
import mididings.overload as _overload


@_unit_repr
def Sanitize():
    return _Unit(_mididings.Sanitize())


@_unit_repr
@_overload.mark
def SceneSwitch(number=_constants.EVENT_PROGRAM):
    return _Unit(_mididings.SceneSwitch(_util.scene_number(number) if number >= 0 else number, 0))

@_unit_repr
@_overload.mark
def SceneSwitch(offset):
    return _Unit(_mididings.SceneSwitch(0, offset))

@_unit_repr
@_overload.mark
def SubSceneSwitch(number=_constants.EVENT_PROGRAM):
    return _Unit(_mididings.SubSceneSwitch(_util.scene_number(number) if number >= 0 else number, 0, False))

@_unit_repr
@_overload.mark
def SubSceneSwitch(offset, wrap=True):
    return _Unit(_mididings.SubSceneSwitch(0, offset, wrap))
