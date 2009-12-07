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

import engine as _engine
import misc as _misc
import setup as _setup


def config(override=False, **kwargs):
    _setup.config(override, **kwargs)

def hook(*args):
    _setup.hook(*args)


def run(*args, **kwargs):
    def run_patch(patch):
        e = _engine.Engine({ 0: patch }, None, None, None)
        e.run()
    def run_scenes(scenes, control=None, pre=None, post=None):
        e = _engine.Engine(scenes, control, pre, post)
        e.run()

    _misc.call_overload('run', args, kwargs, [
        run_patch,
        run_scenes
    ])

_misc.deprecated('run')
def run_scenes(scenes, control=None, pre=None, post=None):
    run(scenes, control, pre, post)

_misc.deprecated('run')
def run_patches(patches, control=None, pre=None, post=None):
    run(patches, control, pre, post)


def process_file(infile, outfile, patch):
    _setup.config(False,
        backend = 'smf',
        in_ports = [infile],
        out_ports = [outfile],
    )
    e = _engine.Engine({ 0: patch }, None, None, None)
    e.process_file()


def switch_scene(n):
    TheEngine.switch_scene(n)

def current_scene():
    return TheEngine.current_scene()

def get_scenes():
    return TheEngine.get_scenes()


def quit():
    TheEngine.quit()
