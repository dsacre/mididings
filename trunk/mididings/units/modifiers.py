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

from mididings.units.base import _Unit

from mididings import util as _util


class Port(_Unit):
    def __init__(self, port):
        _Unit.__init__(self, _mididings.Port(_util.port_number(port)))


class Channel(_Unit):
    def __init__(self, channel):
        _Unit.__init__(self, _mididings.Channel(_util.channel_number(channel)))


class Transpose(_Unit):
    def __init__(self, offset):
        _Unit.__init__(self, _mididings.Transpose(offset))


class Velocity(_Unit):
    OFFSET = 1
    MULTIPLY = 2
    FIXED = 3
    def __init__(self, value, mode=OFFSET):
        _Unit.__init__(self, _mididings.Velocity(value, mode))

def VelocityOffset(value):
    return Velocity(value, Velocity.OFFSET)

def VelocityMultiply(value):
    return Velocity(value, Velocity.MULTIPLY)

def VelocityFixed(value):
    return Velocity(value, Velocity.FIXED)


class VelocityCurve(_Unit):
    def __init__(self, gamma):
        _Unit.__init__(self, _mididings.VelocityCurve(gamma))


class VelocityGradient(_Unit):
    def __init__(self, note_lower, note_upper, value_lower, value_upper, mode=Velocity.OFFSET):
        note_lower = _util.note_number(note_lower)
        note_upper = _util.note_number(note_upper)
        if not note_lower < note_upper:
            raise ValueError("note_lower must be less than note_upper")
        _Unit.__init__(self, _mididings.VelocityGradient(note_lower, note_upper, value_lower, value_upper, mode))

def VelocityGradientOffset(note_lower, note_upper, value_lower, value_upper):
    return VelocityGradient(note_lower, note_upper, value_lower, value_upper, Velocity.OFFSET)

def VelocityGradientMultiply(note_lower, note_upper, value_lower, value_upper):
    return VelocityGradient(note_lower, note_upper, value_lower, value_upper, Velocity.MULTIPLY)

def VelocityGradientFixed(note_lower, note_upper, value_lower, value_upper):
    return VelocityGradient(note_lower, note_upper, value_lower, value_upper, Velocity.FIXED)


class CtrlMap(_Unit):
    def __init__(self, ctrl_in, ctrl_out):
        _Unit.__init__(self, _mididings.CtrlMap(
            _util.ctrl_number(ctrl_in),
            _util.ctrl_number(ctrl_out)
        ))


class CtrlRange(_Unit):
    def __init__(self, ctrl, out_min, out_max, in_min=0, in_max=127):
        if not in_min < in_max:
            raise ValueError("in_min must be less than in_max")
        _Unit.__init__(self, _mididings.CtrlRange(
            _util.ctrl_number(ctrl),
            out_min, out_max,
            in_min, in_max
        ))
