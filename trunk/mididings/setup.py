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

import mididings.arguments as _arguments

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


@_arguments.accept(kwargs = {
    'backend':          tuple(_VALID_BACKENDS),
    'client_name':      str,
    'in_ports':         _arguments.either(
                            _arguments.each(int, _arguments.condition(lambda x: x > 0)),
                            _arguments.sequenceof(_arguments.either(
                                str,
                                [str, str],
                                [str, [str]],
                            )),
                        ),
    'out_ports':        _arguments.either(
                            _arguments.each(int, _arguments.condition(lambda x: x > 0)),
                            _arguments.sequenceof(_arguments.either(
                                str,
                                [str, str],
                                [str, [str]],
                            )),
                        ),
    'data_offset':      (0, 1),
    'octave_offset':    int,
    'initial_scene':    _arguments.either(
                            int,
                            _arguments.each(tuple, [int]),
                            _arguments.each(tuple, [int, int])
                        ),
    'start_delay':      (int, float, type(None)),
    'silent':           bool,
})
def config(**kwargs):
    _config_impl(**kwargs)


def _config_impl(_override=False, **kwargs):
    for k, v in kwargs.items():
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
