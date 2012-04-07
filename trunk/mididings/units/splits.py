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

from mididings.units.base import Chain, Fork, _UNIT_TYPES
from mididings.units.filters import PortFilter, ChannelFilter, KeyFilter, VelocityFilter
from mididings.units.filters import CtrlFilter, CtrlValueFilter, ProgramFilter, SysExFilter

import mididings.overload as _overload
import mididings.arguments as _arguments
import mididings.util as _util


def _make_split(t, d, unpack=False):
    if unpack:
        # if dictionary key is a tuple, unpack and pass as individual parameters to ctor
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



@_arguments.accept({_arguments.nullable(_arguments.flatten(_util.port_number, tuple)): _UNIT_TYPES})
def PortSplit(d):
    return _make_split(PortFilter, d)


@_arguments.accept({_arguments.nullable(_arguments.flatten(_util.channel_number, tuple)): _UNIT_TYPES})
def ChannelSplit(d):
    return _make_split(ChannelFilter, d)


@_overload.mark
@_arguments.accept({_arguments.nullable(_util.note_range): _UNIT_TYPES})
def KeySplit(d):
    return _make_split(KeyFilter, d)

@_overload.mark
@_arguments.accept(_util.note_limit, _UNIT_TYPES, _UNIT_TYPES)
def KeySplit(note, patch_lower, patch_upper):
    return _make_threshold(KeyFilter(0, note), patch_lower, patch_upper)


@_overload.mark
@_arguments.accept({_arguments.nullable(_util.velocity_range): _UNIT_TYPES})
def VelocitySplit(d):
    return _make_split(VelocityFilter, d, unpack=True)

@_overload.mark
@_arguments.accept(_util.velocity_limit, _UNIT_TYPES, _UNIT_TYPES)
def VelocitySplit(threshold, patch_lower, patch_upper):
    return _make_threshold(VelocityFilter(0, threshold), patch_lower, patch_upper)


@_arguments.accept({_arguments.nullable(_arguments.flatten(_util.ctrl_number, tuple)): _UNIT_TYPES})
def CtrlSplit(d):
    return _make_split(CtrlFilter, d)


@_overload.mark
@_arguments.accept({_arguments.nullable(_util.ctrl_range): _UNIT_TYPES})
def CtrlValueSplit(d):
    return _make_split(CtrlValueFilter, d, unpack=True)

@_overload.mark
@_arguments.accept(_util.ctrl_limit, _UNIT_TYPES, _UNIT_TYPES)
def CtrlValueSplit(threshold, patch_lower, patch_upper):
    return _make_threshold(CtrlValueFilter(0, threshold), patch_lower, patch_upper)


@_arguments.accept({_arguments.nullable(_arguments.flatten(_util.program_number, tuple)): _UNIT_TYPES})
def ProgramSplit(d):
    return _make_split(ProgramFilter, d)


@_overload.mark
@_arguments.accept(dict)
def SysExSplit(d):
    return _make_split(SysExFilter, d)

@_overload.mark
@_arguments.accept(dict)
def SysExSplit(manufacturers):
    return _make_split(lambda m: SysExFilter(manufacturer=m), manufacturers)
