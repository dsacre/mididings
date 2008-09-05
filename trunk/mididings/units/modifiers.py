# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import _mididings

from .base import _Unit

from .. import util as _util


class Port(_mididings.Port, _Unit):
    def __init__(self, port):
        _mididings.Port.__init__(self, _util.port_number(port))


class Channel(_mididings.Channel, _Unit):
    def __init__(self, channel):
        _mididings.Channel.__init__(self, _util.channel_number(channel))


class Transpose(_mididings.Transpose, _Unit):
    def __init__(self, offset):
        _mididings.Transpose.__init__(self, offset)


class Velocity(_mididings.Velocity, _Unit):
    OFFSET = 1
    MULTIPLY = 2
    FIXED = 3
    def __init__(self, value, mode=OFFSET):
        _mididings.Velocity.__init__(self, value, mode)

def VelocityOffset(value):
    return Velocity(value, Velocity.OFFSET)

def VelocityMultiply(value):
    return Velocity(value, Velocity.MULTIPLY)

def VelocityFixed(value):
    return Velocity(value, Velocity.FIXED)


class VelocityCurve(_mididings.VelocityCurve, _Unit):
    def __init__(self, gamma):
        _mididings.VelocityCurve.__init__(self, gamma)


class VelocityGradient(_mididings.VelocityGradient, _Unit):
    def __init__(self, note_lower, note_upper, value_lower, value_upper, mode=Velocity.OFFSET):
        _mididings.VelocityGradient.__init__(self,
            _util.note_number(note_lower), _util.note_number(note_upper),
            value_lower, value_upper, mode)

def VelocityGradientOffset(note_lower, note_upper, value_lower, value_upper):
    return VelocityGradient(note_lower, note_upper, value_lower, value_upper, Velocity.OFFSET)

def VelocityGradientMultiply(note_lower, note_upper, value_lower, value_upper):
    return VelocityGradient(note_lower, note_upper, value_lower, value_upper, Velocity.MULTIPLY)

def VelocityGradientFixed(note_lower, note_upper, value_lower, value_upper):
    return VelocityGradient(note_lower, note_upper, value_lower, value_upper, Velocity.FIXED)


class CtrlMap(_mididings.CtrlMap, _Unit):
    def __init__(self, ctrl_in, ctrl_out):
        _mididings.CtrlMap.__init__(self, ctrl_in, ctrl_out)


class CtrlRange(_mididings.CtrlRange, _Unit):
    def __init__(self, ctrl, out_min, out_max, in_min=0, in_max=127):
        _mididings.CtrlRange.__init__(self, ctrl, out_min, out_max, in_min, in_max)
