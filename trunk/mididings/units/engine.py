# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2010  Dominic Sacré  <dominic.sacre@gmx.de>
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
import mididings.misc as _misc


@_unit_repr
def Sanitize():
    return _Unit(_mididings.Sanitize())


@_unit_repr
def SceneSwitch(number=_constants.EVENT_PROGRAM):
    return _Unit(_mididings.SceneSwitch(_util.scene_number(number) if number >= 0 else number))

@_misc.deprecated('SceneSwitch')
def PatchSwitch(number=_constants.EVENT_PROGRAM):
    return SceneSwitch(number)

