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

from mididings.units.base import _UNIT_TYPES

import mididings.arguments as _arguments


class Scene(object):
    @_arguments.accept(None, str, _UNIT_TYPES, _UNIT_TYPES + (type(None),))
    def __init__(self, name, patch, init_patch=None):
        self.name = name
        self.patch = patch
        self.init_patch = init_patch


class SceneGroup(object):
    @_arguments.accept(None, str, [(Scene,) + _UNIT_TYPES])
    def __init__(self, name, subscenes):
        self.name = name
        self.subscenes = subscenes
