# -*- coding: utf-8 -*-
#
# midipatch
#
# Copyright (C) 2007  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import _midipatch
import misc as _misc


class _Unit:
    def __rshift__(self, other):
        return _Chain(self, other)

    def __rrshift__(self, other):
        return _Chain(other, self)


class _Chain(_Unit):
    def __init__(self, first, second):
        self.items = first, second


class Fork(list, _Unit):
    def __init__(self, *args):
        if len(args) == 1:
            list.__init__(self, args[0])
        elif len(args) == 2:
            l = [ (TypeFilter(args[0]) >> x) for x in args[1] ] + \
                [ ~TypeFilter(args[0]) ]
            list.__init__(self, l)
        else:
            raise ArgumentError()

def NoteFork(x):
    return Fork(Types.NOTE, x)

def ControllerFork(x):
    return Fork(Types.CONTROLLER, x)

def PitchBendFork(x):
    return Fork(Types.PITCHBEND, x)

def ProgramChangeFork(x):
    return Fork(Types.PROGRAMCHANGE, x)


# base class for all filters, supporting operator ~
class _Filter(_Unit):
    def __invert__(self):
        return _InvertedFilter(self)

class _Modifier(_Unit):
    pass


class _InvertedFilter(_midipatch.InvertedFilter, _Unit):
    pass


class Pass(_midipatch.Pass, _Unit):
    def __init__(self, p=True):
        _midipatch.Pass.__init__(self, p)

def Discard():
    return Pass(False)


class Types:
    NOTEON        = 1 << 0
    NOTEOFF       = 1 << 1
    NOTE          = NOTEON | NOTEOFF
    CONTROLLER    = 1 << 2
    PITCHBEND     = 1 << 3
    PROGRAMCHANGE = 1 << 4


### filters ###

class TypeFilter(_midipatch.TypeFilter, _Filter):
    def __init__(self, type_):
        _midipatch.TypeFilter.__init__(self, type_)

def NoteGate():
    return TypeFilter(Types.NOTE)

def ControllerGate():
    return TypeFilter(Types.CONTROLLER)

def PitchBendGate():
    return TypeFilter(Types.PITCHBEND)

def ProgramChangeGate():
    return TypeFilter(Types.PROGRAMCHANGE)


class PortFilter(_midipatch.PortFilter, _Filter):
    def __init__(self, *args):
        vec = _midipatch.int_vector()
#        for port in [ p for p in _misc.flatten(args) ]:
        for port in _misc.flatten(args):
            vec.push_back(_misc.offset_port(port))
        _midipatch.PortFilter.__init__(self, vec)


class ChannelFilter(_midipatch.ChannelFilter, _Filter):
    def __init__(self, *args):
        vec = _midipatch.int_vector()
        for channel in [ _misc.offset_channel(c) for c in _misc.flatten(args) ]:
            vec.push_back(channel)
        _midipatch.ChannelFilter.__init__(self, vec)


class KeyFilter(_midipatch.KeyFilter, _Filter):
    def __init__(self, *args):
        if len(args) == 1: args = args[0]
        r = _misc.noterange2numbers(args)
        _midipatch.KeyFilter.__init__(self, r[0], r[1])


class VelocityFilter(_midipatch.VelocityFilter, _Filter):
    def __init__(self, *args):
        if len(args) == 1: args = args[0]
        _midipatch.VelocityFilter.__init__(self, args[0], args[1])


class ControllerFilter(_midipatch.ControllerFilter, _Filter):
    def __init__(self, controller):
        _midipatch.ControllerFilter.__init__(self, controller)


### splits ###

def PortSplit(d):
    return Fork([ (PortFilter(p) >> w) for p, w in d.items() ])

def ChannelSplit(d):
    return Fork([ (ChannelFilter(c) >> w) for c, w in d.items() ])


def KeySplit(*args):
    if len(args) == 1:
        return NoteFork([ (KeyFilter(k) >> w) for k, w in args[0].items() ])
    elif len(args) == 3:
        filt = KeyFilter(0, args[0])
        return NoteFork([ filt >> args[1], ~filt >> args[2] ])
    else:
        raise ArgumentError()


def VelocitySplit(*args):
    if len(args) == 1:
        return NoteFork([ (VelocityFilter(v) >> w) for v, w in args[0].items() ])
    elif len(args) == 3:
        filt = VelocityFilter(0, args[0])
        return NoteFork([ filt >> args[1], ~filt >> args[2] ])
    else:
        raise ArgumentError()


### modifiers ###

class Port(_midipatch.Port, _Modifier):
    def __init__(self, port):
        _midipatch.Port.__init__(self, _misc.offset_port(port))


class Channel(_midipatch.Channel, _Modifier):
    def __init__(self, channel):
        _midipatch.Channel.__init__(self, _misc.offset_channel(channel))


class Transpose(_midipatch.Transpose, _Modifier):
    pass


class Velocity(_midipatch.Velocity, _Modifier):
    OFFSET = 1
    MULTIPLY = 2
    FIXED = 3
    def __init__(self, value, mode=OFFSET):
        _midipatch.Velocity.__init__(self, value, mode)

def VelocityOffset(value):
    return Velocity(value, Velocity.OFFSET)

def VelocityMultiply(value):
    return Velocity(value, Velocity.MULTIPLY)

def VelocityFixed(value):
    return Velocity(value, Velocity.FIXED)


class VelocityGradient(_midipatch.VelocityGradient, _Modifier):
    def __init__(self, note_first, note_last, value_first, value_last, mode=Velocity.OFFSET):
        _midipatch.VelocityGradient.__init__(self,
            _misc.note2number(note_first), _misc.note2number(note_last),
            value_first, value_last, mode)

def VelocityGradientOffset(value):
    return VelocityGradient(value, Velocity.OFFSET)

def VelocityGradientMultiply(value):
    return VelocityGradient(value, Velocity.MULTIPLY)

def VelocityGradientFixed(value):
    return VelocityGradient(value, Velocity.FIXED)


class ControllerRange(_midipatch.ControllerRange, _Modifier):
    def __init__(self, controller, in_min, in_max, out_min, out_max):
        _midipatch.ControllerRange.__init__(self, controller, in_min, in_max, out_min, out_max)


### midi events ###

class TriggerEvent(_midipatch.TriggerEvent, _Unit):
    def __init__(self, type_, port, channel, data1, data2):
        _midipatch.TriggerEvent.__init__(self, type_,
                _misc.offset_port(port) if port >= 0 else port,
                _misc.offset_channel(channel) if channel >= 0 else channel,
                data1, data2)

def ControlChange(port, channel, controller, value):
    return TriggerEvent(Types.CONTROLLER, port, channel, controller, value)

def ProgramChange(port, channel, program):
    return TriggerEvent(Types.PROGRAMCHANGE, port, channel, 0, _misc.offset_program(program))


PORT      = -1
CHANNEL   = -2
DATA1     = -3
DATA2     = -4

NOTE      = -3
VELOCITY  = -4

PROGRAM   = -4

class SwitchPatch(_midipatch.SwitchPatch, _Unit):
    def __init__(self, num=PROGRAM):
        _midipatch.SwitchPatch.__init__(self, num)


class Print(_midipatch.Print, _Unit):
    def __init__(self, name=''):
        _midipatch.Print.__init__(self, name)
