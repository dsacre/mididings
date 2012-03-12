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

class Scene(object):
    def __init__(self, name, patch, init_patch=None):
        self.name = name
        self.patch = patch
        self.init_patch = init_patch


class SceneGroup(object):
    def __init__(self, name, scenes):
        self.name = name
        self.scenes = scenes
