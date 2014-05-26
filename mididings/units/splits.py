# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2014  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

from mididings.units.base import Chain, Fork, _UNIT_TYPES
from mididings.units.filters import (
        PortFilter, ChannelFilter, KeyFilter, VelocityFilter,
        CtrlFilter, CtrlValueFilter, ProgramFilter, SysExFilter)

import mididings.overload as _overload
import mididings.arguments as _arguments
import mididings.util as _util


def _make_split(t, d, unpack=False):
    if unpack:
        # if dictionary key is a tuple, unpack and pass as individual
        # parameters to ctor
        t = lambda p, t=t: t(*(p if isinstance(p, tuple) else (p,)))

    # build dict with all items from d, except d[None]
    dd = dict((k, v) for k, v in d.items() if k is not None)

    # build fork from all normal items
    r = Fork((t(k) >> w) for k, w in dd.items())

    # add else-rule, if any
    if None in d:
        f = Chain(~t(k) for k in dd.keys())
        r.append(f >> d[None])

    return r


def _make_threshold(f, patch_lower, patch_upper):
    return Fork([
        f >> patch_lower,
        ~f >> patch_upper,
    ])



@_arguments.accept({
    _arguments.nullable(_arguments.flatten(_util.port_number, tuple)):
        _UNIT_TYPES
})
def PortSplit(mapping):
    """
    PortSplit(mapping)

    Split events by input port, with *mapping* being a dictionary of the form
    ``{ports: patch, ...}``.
    """
    return _make_split(PortFilter, mapping)


@_arguments.accept({
    _arguments.nullable(_arguments.flatten(_util.channel_number, tuple)):
        _UNIT_TYPES
})
def ChannelSplit(mapping):
    """
    ChannelSplit(mapping)

    Split events by input channel, with *mapping* being a dictionary of
    the form ``{channels: patch, ...}``.
    """
    return _make_split(ChannelFilter, mapping)


@_overload.mark(
    """
    KeySplit(threshold, patch_lower, patch_upper)
    KeySplit(mapping)

    Split events by key. Non-note events are sent to all patches.

    The first version splits at a single threshold. The second version allows
    an arbitrary number of (possibly overlapping) note ranges, with *mapping*
    being a dictionary of the form ``{note_range: patch, ...}``.
    """
)
@_arguments.accept(_util.note_limit, _UNIT_TYPES, _UNIT_TYPES)
def KeySplit(threshold, patch_lower, patch_upper):
    return _make_threshold(KeyFilter(0, threshold),
                           patch_lower, patch_upper)

@_overload.mark
@_arguments.accept({_arguments.nullable(_util.note_range): _UNIT_TYPES})
def KeySplit(mapping):
    return _make_split(KeyFilter, mapping)


@_overload.mark(
    """
    VelocitySplit(threshold, patch_lower, patch_upper)
    VelocitySplit(mapping)

    Split events by note-on velocity. Non-note events are sent to all patches.

    The first version splits at a single threshold. The second version allows
    an arbitrary number of (possibly overlapping) value ranges, with
    *mapping* being a dictionary of the form ``{(lower, upper): patch, ...}``.
    """
)
@_arguments.accept(_util.velocity_limit, _UNIT_TYPES, _UNIT_TYPES)
def VelocitySplit(threshold, patch_lower, patch_upper):
    return _make_threshold(VelocityFilter(0, threshold),
                           patch_lower, patch_upper)

@_overload.mark
@_arguments.accept({_arguments.nullable(_util.velocity_range): _UNIT_TYPES})
def VelocitySplit(mapping):
    return _make_split(VelocityFilter, mapping, unpack=True)


@_arguments.accept({
    _arguments.nullable(_arguments.flatten(_util.ctrl_number, tuple)):
        _UNIT_TYPES
})
def CtrlSplit(mapping):
    """
    CtrlSplit(mapping)

    Split events by controller number, with *mapping* being a dictionary of
    the form ``{ctrls: patch, ...}``.
    Non-control-change events are discarded.
    """
    return _make_split(CtrlFilter, mapping)


@_overload.mark(
    """
    CtrlValueSplit(threshold, patch_lower, patch_upper)
    CtrlValueSplit(mapping)

    Split events by controller value.

    The first version splits at a single threshold. The second version allows
    an arbitrary number of (possibly overlapping) value ranges, with *mapping*
    being a dictionary of the form ``{value: patch, ...}`` or
    ``{(lower, upper): patch, ...}``.

    Non-control-change events are discarded.

    """
)
@_arguments.accept(_util.ctrl_limit, _UNIT_TYPES, _UNIT_TYPES)
def CtrlValueSplit(threshold, patch_lower, patch_upper):
    return _make_threshold(CtrlValueFilter(0, threshold),
                           patch_lower, patch_upper)

@_overload.mark
@_arguments.accept({_arguments.nullable(_util.ctrl_range): _UNIT_TYPES})
def CtrlValueSplit(mapping):
    return _make_split(CtrlValueFilter, mapping, unpack=True)


@_arguments.accept({
    _arguments.nullable(_arguments.flatten(_util.program_number, tuple)):
        _UNIT_TYPES
})
def ProgramSplit(mapping):
    """
    ProgramSplit(mapping)

    Split events by program number, with *mapping* being a dictionary of the
    form ``{programs: patch, ...}``.
    Non-program-change events are discarded.
    """
    return _make_split(ProgramFilter, mapping)


@_overload.mark(
    """
    SysExSplit(mapping)
    SysExSplit(manufacturers=...)

    Split events by sysex data or manufacturer id, with *mapping* being a
    dictionary of the form ``{sysex: patch, ...}``, and *manufacturers* being
    a dictionary of the form ``{manufacturer: patch, ...}``
    (cf. :func:`SysExFilter()`).

    Non-sysex events are discarded.
    """
)
@_arguments.accept(dict)
def SysExSplit(mapping):
    return _make_split(SysExFilter, mapping)

@_overload.mark
@_arguments.accept(dict)
def SysExSplit(manufacturers):
    return _make_split(lambda m: SysExFilter(manufacturer=m), manufacturers)
