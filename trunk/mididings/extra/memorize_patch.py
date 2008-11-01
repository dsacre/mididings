# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

from mididings import run_patches


def run_patches_memorize(memo_file, patches, control=None, pre=None, post=None):
    try:
        f = open(memo_file)
        first_patch = int(f.read())
    except:
        first_patch = -1

    current_patch = [-1]

    # need to track patch changes in a callback, the engine object
    # will be gone by the time run_patches() returns
    def callback(n):
        current_patch[0] = n

    run_patches(patches, control, pre, post,
                first_patch = first_patch,
                patch_switch_callback = callback)

    f = open(memo_file, 'w')
    f.write(str(current_patch[0]))
