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

from mididings import run_scenes


def run_scenes_memorize(memo_file, scenes, control=None, pre=None, post=None):
    try:
        f = open(memo_file)
        first_scene = int(f.read())
    except:
        first_scene = -1

    current_scene = [-1]

    # need to track scene changes in a callback, the engine object
    # will be gone by the time run_scenees() returns
    def callback(n):
        current_scene[0] = n

    run_scenes(scenes, control, pre, post,
               first_scene = first_scene,
               scene_switch_callback = callback)

    f = open(memo_file, 'w')
    f.write(str(current_scene[0]))
