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


_config = {
    'backend':              'alsa',
    'client_name':          'mididings',
    'in_ports':             1,
    'out_ports':            1,
    'data_offset':          1,
    'octave_offset':        2,
    'verbose':              True,
    'start_delay':          None,
    'remove_duplicates':    True,
    'osc_port':             None,
    'osc_notify_port':      None,
}


def config(**kwargs):
    for k in kwargs:
        if k not in _config:
            raise TypeError('unknown config variable: %s' % k)
        _config[k] = kwargs[k]


def run(patch):
    run_scenes({ _config['data_offset']: patch }, None, None, None)


def run_scenes(scenes, control=None, pre=None, post=None, first_scene=-1, scene_switch_callback=None):
    if first_scene == -1:
        first_scene = _config['data_offset']
    e = _engine.Engine(scenes, control, pre, post)
    try:
        e.run(first_scene, scene_switch_callback)
    except KeyboardInterrupt:
        return


# for backward compatibility, deprecated
def run_patches(patches, control=None, pre=None, post=None, first_patch=-1, patch_switch_callback=None):
    run_scenes(patches, control, pre, post, first_patch, patch_switch_callback)


def process_file(infile, outfile, patch):
    config(
        backend = 'smf',
        in_ports = [infile],
        out_ports = [outfile],
    )
    e = _engine.Engine({ 0: patch }, None, None, None)
    e.process_file()


def test_run(patch, events):
    return test_run_scenes({ _config['data_offset']: patch }, events)


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
    TheEngine.switch_scene(n - _config['data_offset'])


def current_scene():
    return TheEngine.current_scene() + _config['data_offset']



__all__ = ['config', 'run', 'run_scenes', 'run_patches', 'process_file', 'switch_scene', 'current_scene']
