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

import time as _time


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
}


def config(**kwargs):
    for k in kwargs:
        if k not in _config:
            raise TypeError('unknown config variable: %s' % k)
        _config[k] = kwargs[k]


def run(patch):
    run_patches({ _config['data_offset']: patch }, None, None, None)


def run_patches(patches, control=None, pre=None, post=None, first_patch=-1, patch_switch_callback=None):
    if first_patch == -1:
        first_patch = _config['data_offset']
    e = _engine.Engine(patches, control, pre, post)
    try:
        e.start(first_patch, patch_switch_callback)
        while True:
            _time.sleep(3600)
    except KeyboardInterrupt:
        return


def process_file(infile, outfile, patch):
    config(
        backend = 'smf',
        in_ports = [infile],
        out_ports = [outfile],
    )
    e = _engine.Engine({ 0: patch }, None, None, None)
    e.start(0, None)


def test_run(patch, events):
    return test_run_patches({ _config['data_offset']: patch }, events)


def test_run_patches(patches, events):
    config(backend = 'dummy')
    e = _engine.Engine(patches, None, None, None)
    r = []
    if not _misc.issequence(events):
        events = [events]
    for ev in events:
        r += e.process(ev)[:]
    return r


def switch_patch(n):
    TheEngine.switch_patch(n - _config['data_offset'])


def current_patch():
    return TheEngine.current_patch() + _config['data_offset']



__all__ = ['config', 'run', 'run_patches', 'process_file', 'switch_patch', 'current_patch']
