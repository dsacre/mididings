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

import _mididings

from mididings.units.base import _Unit, _unit_repr, Filter, Split, Pass
from mididings.units.splits import VelocitySplit
from mididings.units.generators import NoteOn, NoteOff

import mididings.util as _util
import mididings.misc as _misc
import mididings.constants as _constants


@_unit_repr
def Port(port):
    return _Unit(_mididings.Port(_util.port_number(port)))


@_unit_repr
def Channel(channel):
    return _Unit(_mididings.Channel(_util.channel_number(channel)))


@_unit_repr
def Transpose(offset):
    return _Unit(_mididings.Transpose(offset))


def Key(note):
    return Filter(_constants.NOTE) % Split({
        _constants.NOTEON:  NoteOn(note, _constants.EVENT_VELOCITY),
        _constants.NOTEOFF: NoteOff(note, _constants.EVENT_VELOCITY),
    })


@_unit_repr
def Velocity(*args, **kwargs):
    param, mode = _misc.call_overload(args, kwargs, [
        lambda offset: (offset, 1),
        lambda multiply: (multiply, 2),
        lambda fixed: (fixed, 3),
        lambda gamma: (gamma, 4),
        lambda curve: (curve, 5),
        lambda multiply, offset: ((multiply, offset), 6),
    ])
    if mode == 6:
        return Velocity(multiply=param[0]) >> Velocity(offset=param[1])
    else:
        return _Unit(_mididings.Velocity(param, mode))


@_misc.deprecated('Velocity')
def VelocityMultiply(value):
    return Velocity(multiply=value)

@_misc.deprecated('Velocity')
def VelocityFixed(value):
    return Velocity(fixed=value)

@_misc.deprecated('Velocity')
def VelocityCurve(gamma):
    return Velocity(gamma=gamma)


@_unit_repr
def VelocitySlope(*args, **kwargs):
    notes, params, mode = _misc.call_overload(args, kwargs, [
        lambda notes, offset: (notes, offset, 1),
        lambda notes, multiply: (notes, multiply, 2),
        lambda notes, fixed: (notes, fixed, 3),
        lambda notes, gamma: (notes, gamma, 4),
        lambda notes, curve: (notes, curve, 5),
        lambda notes, multiply, offset: (notes, (multiply, offset), 6),
    ])
    note_numbers = [_util.note_number(n) for n in notes]

    if len(notes) != len(params) and mode != 6:
        raise ValueError("notes and velocity values must be sequences of the same length")
    if len(notes) < 2:
        raise ValueError("need at least two notes")
    if sorted(note_numbers) != note_numbers:
        raise ValueError("notes must be in ascending order")

    if mode == 6:
        return VelocitySlope(notes, multiply=params[0]) >> VelocitySlope(notes, offset=params[1])
    else:
        return _Unit(_mididings.VelocitySlope(
            _misc.make_int_vector(note_numbers),
            _misc.make_float_vector(params), mode
        ))


@_misc.deprecated('VelocitySlope')
def VelocityGradient(note_lower, note_upper, value_lower, value_upper):
    return VelocitySlope((note_lower, note_upper), offset=(value_lower, value_upper))

@_misc.deprecated('VelocitySlope')
def VelocityGradientMultiply(note_lower, note_upper, value_lower, value_upper):
    return VelocitySlope((note_lower, note_upper), multiply=(value_lower, value_upper))

@_misc.deprecated('VelocitySlope')
def VelocityGradientFixed(note_lower, note_upper, value_lower, value_upper):
    return VelocitySlope((note_lower, note_upper), fixed=(value_lower, value_upper))


def VelocityLimit(*args, **kwargs):
    min, max = _misc.call_overload(args, kwargs, [
        lambda min, max: (min, max),
        lambda max: (0, max),
        lambda min: (min, 0),
    ])

    d = { (min, max): Pass() }
    if min:
        d[(0, min)] = Velocity(fixed=min)
    if max:
        d[(max, 0)] = Velocity(fixed=max)

    return Filter(_constants.NOTE) % VelocitySplit(d)


@_unit_repr
def CtrlMap(ctrl_in, ctrl_out):
    return _Unit(_mididings.CtrlMap(
        _util.ctrl_number(ctrl_in),
        _util.ctrl_number(ctrl_out)
    ))


@_unit_repr
def CtrlRange(ctrl, min, max, in_min=0, in_max=127):
    if in_min > in_max:
        # swap ranges so that in_min is less than in_max
        in_min, in_max = in_max, in_min
        min, max = max, min
    return _Unit(_mididings.CtrlRange(
        _util.ctrl_number(ctrl),
        min, max, in_min, in_max
    ))


@_unit_repr
def CtrlCurve(*args, **kwargs):
    ctrl, param, mode = _misc.call_overload(args, kwargs, [
        lambda ctrl, gamma: (ctrl, gamma, 4),
        lambda ctrl, curve: (ctrl, curve, 5),
        lambda ctrl, offset: (ctrl, offset, 1),
        lambda ctrl, multiply: (ctrl, multiply, 2),
        lambda ctrl, multiply, offset: (ctrl, (multiply, offset), 6),
    ])
    if mode == 6:
        return CtrlCurve(ctrl, multiply=param[0]) >> CtrlCurve(ctrl, offset=param[1])
    else:
        return _Unit(_mididings.CtrlCurve(ctrl, param, mode))


@_unit_repr
@_misc.overload
def PitchbendRange(min, max, in_min=-8192, in_max=8191):
    return _Unit(_mididings.PitchbendRange(min, max, in_min, in_max))

@_misc.overload
def PitchbendRange(down, up, range):
    return PitchbendRange(int(float(down)/range*8192), int(float(up)/range*8191))
