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


def _default_portname(n, out):
    prefix = 'out_' if out else 'in_'
    return prefix + str(n + get_config('data_offset'))

def _parse_portnames(ports, out):
    if not _misc.issequence(ports):
        return [_default_portname(n, out) for n in range(ports)]

    portnames = []
    for n, port in enumerate(ports):
        if _misc.issequence(port):
            if port[0] is None:
                portnames.append(_default_portname(n, out))
            else:
                portnames.append(port[0])
        else:
            portnames.append(port)
    return portnames


def _parse_port_connections(ports, out):
    if not _misc.issequence(ports):
        return {}

    connections = {}
    for n, port in enumerate(ports):
        if not _misc.issequence(port) or len(port) <= 1 or port[1] is None:
            continue
        portname = port[0]
        if port[0] is None:
            portname = _default_portname(n, out)
        connections[portname] = port[1:]
    return connections


def reset():
    global _config, _config_overridden, _hooks
    _config = _DEFAULT_CONFIG.copy()
    _config_overridden = []
    _hooks = []
    _config_updated()



@_arguments.accept(kwargs = {
    'backend':          tuple(_VALID_BACKENDS),
    'client_name':      str,
    'in_ports':         _arguments.either(
                            _arguments.each(int, _arguments.condition(lambda x: x > 0)),
                            _arguments.sequenceof(_arguments.either(str, [str])),
                        ),
    'out_ports':        _arguments.either(
                            _arguments.each(int, _arguments.condition(lambda x: x > 0)),
                            _arguments.sequenceof(_arguments.either(str, [str])),
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


def _config_impl(override=False, **kwargs):
    for k, v in kwargs.items():
        # everything seems ok, go ahead and change the config
        if override or k not in _config_overridden:
            _config[k] = v
        if override:
            _config_overridden.append(k)
    _config_updated()


def _config_updated():
    global _in_portnames, _out_portnames
    global _in_port_connections, _out_port_connections
    _in_portnames = _parse_portnames(get_config('in_ports'), False)
    _out_portnames = _parse_portnames(get_config('out_ports'), True)
    _in_port_connections = _parse_port_connections(get_config('in_ports'), False)
    _out_port_connections = _parse_port_connections(get_config('out_ports'), True)


def get_config(var):
    return _config[var]


def hook(*args):
    _hooks.extend(args)

def get_hooks():
    return _hooks


reset()
