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

import _mididings

import mididings.misc as _misc

_VALID_BACKENDS = _mididings.available_backends()

_DEFAULT_CONFIG = {
    'backend':          'alsa' if 'alsa' in _VALID_BACKENDS else 'jack',
    'client_name':      'mididings',
    'in_ports':         1,
    'out_ports':        1,
    'data_offset':      1,
    'octave_offset':    2,
    'initial_scene':    None,
    'start_delay':      None,
    'silent':           False,
}

_config = _DEFAULT_CONFIG.copy()
_config_override = []
_hooks = []


def config(_override=False, _check=True, **kwargs):
    for k, v in kwargs.items():
        # check if the name of the config variable is known
        if k not in _config:
            raise ValueError("unknown config variable '%s'" % k)

        # check if the value and/or type is valid for the given config variable
        if _check:
            if k == 'backend' and v not in _VALID_BACKENDS:
                raise ValueError("backend must be one of %s" % ', '.join("'%s'" % x for x in _VALID_BACKENDS))

            if k == 'client_name' and not isinstance(v, str):
                raise TypeError("client_name must be a string")

            if k in ('in_ports', 'out_ports'):
                if isinstance(v, int):
                    if v < 1:
                        raise ValueError("%s can't be less than one" % k)
                elif _misc.issequence(v):
                    if not _misc.issequenceof(v, str):
                        raise TypeError("all values in %s must be strings" % k)
                else:
                    raise TypeError("%s must be an integer or a sequence" % k)

            if k == 'data_offset' and v not in (0, 1):
                raise ValueError("data_offset must be 0 or 1")

            if k == 'octave_offset' and not isinstance(v, int):
                raise TypeError("octave_offset must be an integer")

            if k == 'initial_scene':
                if not isinstance(v, int) and not _misc.issequenceof(v, int):
                    raise TypeError("initial_scene must be an integer or a tuple of two integers")

            if k == 'start_delay':
                if not isinstance(v, (int, float, type(None))):
                    raise TypeError("start_delay must be a number or None")
                if v != None and v < 0:
                    raise ValueError("start_delay must be a positive number")

            if k == 'silent' and not isinstance(v, bool):
                raise TypeError("silent must be a boolean")

        # everything seems ok, go ahead and change the config
        if _override or k not in _config_override:
            _config[k] = v
        if _override:
            _config_override.append(k)

def get_config(var):
    return _config[var]


def hook(*args):
    _hooks.extend(args)

def get_hooks():
    return _hooks


def reset():
    global _config, _config_override, _hooks
    _config = _DEFAULT_CONFIG.copy()
    _config_override = []
    _hooks = []
