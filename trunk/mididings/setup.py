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

_config = {
    'backend':          'alsa',
    'client_name':      'mididings',
    'in_ports':         1,
    'out_ports':        1,
    'data_offset':      1,
    'octave_offset':    2,
    'initial_scene':    None,
    'start_delay':      None,
    'silent':           False,
}

_config_override = []

_hooks = []


def config(override=False, **kwargs):
    for k in kwargs:
        if k not in _config:
            raise TypeError('unknown config variable: %s' % k)
        if override or k not in _config_override:
            _config[k] = kwargs[k]
        if override:
            _config_override.append(k)

def get_config(var):
    return _config[var]


def hook(*args):
    _hooks.extend(args)

def get_hooks():
    return _hooks
