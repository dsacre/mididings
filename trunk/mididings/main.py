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


class _Config(dict):
    def __init__(self, d):
        dict.__init__(self, d)

    def __call__(self, **kwargs):
        for k in kwargs:
            if k not in self:
                raise ValueError('unknown config variable: %s' % k)
            self[k] = kwargs[k]


config = _Config({
    'backend':          'alsa',
    'client_name':      'mididings',
    'in_ports':         1,
    'out_ports':        1,
    'data_offset':      1,
    'octave_offset':    2,
    'initial_scene':    None,
    'verbose':          True,
    'start_delay':      None,
})


_hooks = []

def hook(*args):
    _hooks.extend(args)


def run(patch):
    run_scenes({ config['data_offset']: patch }, None, None, None)


def run_scenes(scenes, control=None, pre=None, post=None):
    e = _engine.Engine(scenes, control, pre, post)
    try:
        e.run()
    except KeyboardInterrupt:
        return


_misc.deprecated('run_scenes')
def run_patches(patches, control=None, pre=None, post=None):
    run_scenes(patches, control, pre, post)


def process_file(infile, outfile, patch):
    config(
        backend = 'smf',
        in_ports = [infile],
        out_ports = [outfile],
    )
    e = _engine.Engine({ 0: patch }, None, None, None)
    e.process_file()


def test_run(patch, events):
    return test_run_scenes({ config['data_offset']: patch }, events)


def test_run_scenes(scenes, events):
    config(backend = 'dummy')
    e = _engine.Engine(scenes, None, None, None)
    r = []
    if not _misc.issequence(events):
        events = [events]
    for ev in events:
        r += e.process(ev)[:]
    return r


def switch_scene(n):
    TheEngine.switch_scene(n - config['data_offset'])


def current_scene():
    return TheEngine.current_scene() + config['data_offset']


def quit():
    TheEngine.quit()



__all__ = [
    'config',
    'hook',
    'run',
    'run_scenes',
    'run_patches',
    'process_file',
    'switch_scene',
    'current_scene',
    'quit',
]
