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

import _mididings

from mididings.units.base import _Unit, _unit_repr

import mididings.util as _util


@_unit_repr
def Port(port):
    return _Unit(_mididings.Port(_util.port_number(port)))


@_unit_repr
def Channel(channel):
    return _Unit(_mididings.Channel(_util.channel_number(channel)))


@_unit_repr
def Transpose(offset):
    return _Unit(_mididings.Transpose(offset))


@_unit_repr
def Velocity(offset=None, multiply=None, fixed=None):
    if sum(x != None for x in (offset, multiply, fixed)) != 1:
        raise ValueError("arguments offset, multiply and fixed are mutually exclusive")

    if offset != None:
        return _Unit(_mididings.Velocity(offset, 1))
    elif multiply != None:
        return _Unit(_mididings.Velocity(multiply, 2))
    elif fixed != None:
        return _Unit(_mididings.Velocity(fixed, 3))


# for backward compatibility, deprecated
def VelocityOffset(value):
    return Velocity(offset=value)

def VelocityMultiply(value):
    return Velocity(multiply=value)

def VelocityFixed(value):
    return Velocity(fixed=value)


@_unit_repr
def VelocityCurve(gamma):
    return _Unit(_mididings.VelocityCurve(gamma))


@_unit_repr
def VelocityGradient(notes, offset=None, multiply=None, fixed=None):
    if offset != None and multiply != None and fixed != None:
        # for backward compatibility
        notes = (notes, offset)
        offset = (multiply, fixed)
        multiply = fixed = None

    try:
        note_lower, note_upper = _util.note_range(notes)
    except Exception:
        raise ValueError("invalid note range")
    if not note_lower < note_upper:
        raise ValueError("note numbers must be in ascending order")

    if sum(x != None for x in (offset, multiply, fixed)) != 1:
        raise ValueError("arguments offset, multiply and fixed are mutually exclusive")

    if offset != None:
        return _Unit(_mididings.VelocityGradient(note_lower, note_upper, offset[0], offset[1], 1))
    elif multiply != None:
        return _Unit(_mididings.VelocityGradient(note_lower, note_upper, multiply[0], multiply[1], 2))
    elif fixed != None:
        return _Unit(_mididings.VelocityGradient(note_lower, note_upper, fixed[0], fixed[1], 3))


def VelocityGradientOffset(note_lower, note_upper, value_lower, value_upper):
    return VelocityGradient((note_lower, note_upper), offset=(value_lower, value_upper))

def VelocityGradientMultiply(note_lower, note_upper, value_lower, value_upper):
    return VelocityGradient((note_lower, note_upper), multiply=(value_lower, value_upper))

def VelocityGradientFixed(note_lower, note_upper, value_lower, value_upper):
    return VelocityGradient((note_lower, note_upper), fixed=(value_lower, value_upper))


@_unit_repr
def CtrlMap(ctrl_in, ctrl_out):
    return _Unit(_mididings.CtrlMap(
        _util.ctrl_number(ctrl_in),
        _util.ctrl_number(ctrl_out)
    ))


@_unit_repr
def CtrlRange(ctrl, out_min, out_max, in_min=0, in_max=127):
    if not in_min < in_max:
        raise ValueError("in_min must be less than in_max")
    return _Unit(_mididings.CtrlRange(
        _util.ctrl_number(ctrl),
        out_min, out_max, in_min, in_max
    ))
