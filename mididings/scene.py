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

from mididings.units.base import _UNIT_TYPES

import mididings.patch as _patch
import mididings.arguments as _arguments


class Scene(object):
    """
    Scene(name, patch, init_patch=None, exit_patch=None)

    Construct a Scene object to be used with the :func:`run()` function.

    :param name: a string describing the scene.
    :param patch: the patch defining the MIDI processing to take place for
        incoming events.
    :param init_patch: an optional patch that will be triggered when
        switching to this scene.
    :param exit_patch: an optional patch that will be triggered when
        switching away from this scene.
    """
    @_arguments.accept(None, _arguments.nullable(str), _UNIT_TYPES,
                       _arguments.nullable(_UNIT_TYPES),
                       _arguments.nullable(_UNIT_TYPES))
    def __init__(self, name, patch, init_patch=None, exit_patch=None):
        self.name = name if name else ''
        self.patch = patch
        self.init_patch = [init_patch] if init_patch else []
        self.exit_patch = [exit_patch] if exit_patch else []


class SceneGroup(object):
    """
    SceneGroup(name, subscenes)

    Construct a SceneGroup object. This can be used to group multiple scenes
    under a common name and program number.

    :param name: a string describing the subscene.
    :param subscenes: a list of :class:`Scene` objects or patches.
    """
    @_arguments.accept(None, str, [(Scene,) + _UNIT_TYPES])
    def __init__(self, name, subscenes):
        self.name = name
        self.subscenes = subscenes



def _parse_scene(scene):
    if isinstance(scene, Scene):
        pass
    elif isinstance(scene, tuple):
        scene = Scene(None, *scene)
    else:
        scene = Scene(None, scene, None)

    # add any initializations defined in the processing patch
    # (via Init() etc.) to the init patch
    scene.init_patch += _patch.get_init_patches(scene.patch)
    scene.exit_patch += _patch.get_exit_patches(scene.patch)

    return scene


# the types that are (convertible to) valid scenes
_SCENE_TYPES = (Scene, SceneGroup) + _UNIT_TYPES
