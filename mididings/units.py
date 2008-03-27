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
import main as _main
import util as _util
from event import *


# bass class for all units
class _Unit:
    def __rshift__(self, other):
        return _Chain(self, other)

    def __rrshift__(self, other):
        return _Chain(other, self)


# units connected in series
class _Chain(_Unit):
    def __init__(self, first, second):
        self.items = first, second


# units connected in parallel
class Fork(list, _Unit):
    def __init__(self, l):
        list.__init__(self, l)


# base class for all filters, supporting operator ~
class _Filter(_Unit):
    def __invert__(self):
        return _InvertedFilter(self)


class _InvertedFilter(_mididings.InvertedFilter, _Unit):
    pass


class Pass(_mididings.Pass, _Unit):
    def __init__(self, p=True):
        _mididings.Pass.__init__(self, p)

def Discard():
    return Pass(False)


###

class _TypeFork(Fork):
    def __init__(self, t, l):
#        a = [ (_TypeFilter(t) >> x) for x in l ] + [ ~_TypeFilter(t) ]
#        Fork.__init__(self, a)
        match = _TypeFilter(t) >> [ x for x in l ]
        other = ~_TypeFilter(t)
        Fork.__init__(self, [ match, other ])

def NoteFork(x):
    return _TypeFork(TYPE_NOTE, x)

def CtrlFork(x):
    return _TypeFork(TYPE_CTRL, x)

def PitchbendFork(x):
    return _TypeFork(TYPE_PITCHBEND, x)

def ProgFork(x):
    return _TypeFork(TYPE_PROGRAM, x)


def _Divide(t, match, other=Pass()):
    return Fork([ _TypeFilter(t) >> match, ~_TypeFilter(t) >> other ])

def NoteDivide(match, other=Pass()):
    return _Divide(TYPE_NOTE, match, other)

def CtrlDivide(match, other=Pass()):
    return _Divide(TYPE_CTRL, match, other)

def PitchbendDivide(match, other=Pass()):
    return _Divide(TYPE_PITCHBEND, match, other)

def ProgDivide(match, other=Pass()):
    return _Divide(TYPE_PROGRAM, match, other)


### filters ###

class _TypeFilter(_mididings.TypeFilter, _Filter):
    def __init__(self, type_):
        _mididings.TypeFilter.__init__(self, type_)

def NoteGate():
    return _TypeFilter(TYPE_NOTE)

def CtrlGate():
    return _TypeFilter(TYPE_CTRL)

def PitchbendGate():
    return _TypeFilter(TYPE_PITCHBEND)

def ProgGate():
    return _TypeFilter(TYPE_PROGRAM)


class PortFilter(_mididings.PortFilter, _Filter):
    def __init__(self, *args):
        v = _mididings.int_vector()
        for p in _util.flatten(args):
            v.push_back(p - _main.DATA_OFFSET)
        _mididings.PortFilter.__init__(self, v)


class ChannelFilter(_mididings.ChannelFilter, _Filter):
    def __init__(self, *args):
        v = _mididings.int_vector()
        for c in _util.flatten(args):
            v.push_back(c - _main.DATA_OFFSET)
        _mididings.ChannelFilter.__init__(self, v)


class KeyFilter(_mididings.KeyFilter, _Filter):
    def __init__(self, *args):
        if len(args) == 1:
            args = args[0]
        r = _util.noterange2numbers(args)
        _mididings.KeyFilter.__init__(self, r[0], r[1])


class VelocityFilter(_mididings.VelocityFilter, _Filter):
    def __init__(self, *args):
        if len(args) == 1:
            args = args[0]
        _mididings.VelocityFilter.__init__(self, args[0], args[1])


class CtrlFilter(_mididings.CtrlFilter, _Filter):
    def __init__(self, *args):
        v = _mididings.int_vector()
        for c in _util.flatten(args):
            v.push_back(c)
        _mididings.CtrlFilter.__init__(self, v)


class CtrlValueFilter(_mididings.CtrlValueFilter, _Filter):
    def __init__(self, lower, upper=0):
        _mididings.CtrlValueFilter.__init__(self, lower, upper)


class ProgFilter(_mididings.ProgFilter, _Filter):
    def __init__(self, *args):
        v = _mididings.int_vector()
        for p in _util.flatten(args):
            v.push_back(p - _main.DATA_OFFSET)
        _mididings.ProgFilter.__init__(self, v)


### splits ###

def PortSplit(d):
    return Fork([ (PortFilter(p) >> w) for p, w in d.items() ])

def ChannelSplit(d):
    return Fork([ (ChannelFilter(c) >> w) for c, w in d.items() ])


def KeySplit(*args):
    if len(args) == 1:
        # KeySplit(d)
        return NoteFork([ (KeyFilter(k) >> w) for k, w in args[0].items() ])
    elif len(args) == 3:
        # KeySplit(key, unit_lower, unit_upper)
        key, unit_lower, unit_upper = args
        filt = KeyFilter(0, key)
        return NoteFork([ filt >> unit_lower, ~filt >> unit_upper ])
    else:
        raise ArgumentError()


def VelocitySplit(*args):
    if len(args) == 1:
        # VelocitySplit(d)
        return NoteFork([ (VelocityFilter(v) >> w) for v, w in args[0].items() ])
    elif len(args) == 3:
        # VelocitySplit(thresh, unit_lower, unit_upper)
        thresh, unit_lower, unit_upper = args
        filt = VelocityFilter(0, thresh)
        return NoteFork([ filt >> unit_lower, ~filt >> unit_upper ])
    else:
        raise ArgumentError()


### modifiers ###

class Port(_mididings.Port, _Unit):
    def __init__(self, port):
        _mididings.Port.__init__(self, port - _main.DATA_OFFSET)


class Channel(_mididings.Channel, _Unit):
    def __init__(self, channel):
        _mididings.Channel.__init__(self, channel - _main.DATA_OFFSET)


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
            _util.note2number(note_lower), _util.note2number(note_upper),
            value_lower, value_upper, mode)

def VelocityGradientOffset(note_lower, note_upper, value_lower, value_upper):
    return VelocityGradient(note_lower, note_upper, value_lower, value_upper, Velocity.OFFSET)

def VelocityGradientMultiply(note_lower, note_upper, value_lower, value_upper):
    return VelocityGradient(note_lower, note_upper, value_lower, value_upper, Velocity.MULTIPLY)

def VelocityGradientFixed(note_lower, note_upper, value_lower, value_upper):
    return VelocityGradient(note_lower, note_upper, value_lower, value_upper, Velocity.FIXED)


class CtrlRange(_mididings.CtrlRange, _Unit):
    def __init__(self, ctrl, in_min, in_max, out_min, out_max):
        _mididings.CtrlRange.__init__(self, ctrl, in_min, in_max, out_min, out_max)


### misc ###

class GenerateEvent(_mididings.GenerateEvent, _Unit):
    def __init__(self, type_, port, channel, data1, data2):
        _mididings.GenerateEvent.__init__(self, type_,
                port - _main.DATA_OFFSET if port >= 0 else port,
                channel - _main.DATA_OFFSET if channel >= 0 else channel,
                data1, data2)


def CtrlChange(*args):
    if len(args) == 2:
        # ControlChange(ctrl, value)
        ctrl, value = args
        return GenerateEvent(TYPE_CTRL, _main.DATA_OFFSET,
                             _main.DATA_OFFSET, ctrl, value)
    elif len(args) == 4:
        # ControlChange(port, channel, ctrl, value)
        port, channel, ctrl, value = args
        return GenerateEvent(TYPE_CTRL, port, channel, ctrl, value)
    else:
        raise ArgumentError()


def ProgChange(*args):
    if len(args) == 1:
        # ProgramChange(program)
        return GenerateEvent(TYPE_PROGRAM, _main.DATA_OFFSET,
                             _main.DATA_OFFSET, 0, args[0] - _main.DATA_OFFSET)
    elif len(args) == 3:
        # ProgramChange(port, channel, program)
        port, channel, program = args
        return GenerateEvent(TYPE_PROGRAM, port, channel, 0, program - _main.DATA_OFFSET)
    else:
        raise ArgumentError()


class PatchSwitch(_mididings.PatchSwitch, _Unit):
    def __init__(self, num=PROGRAM):
        _mididings.PatchSwitch.__init__(self, num)


class Call(_mididings.Call, _Unit):
    def __init__(self, fun):
        self.fun = fun
        _mididings.Call.__init__(self, self.do_call)
    def do_call(self, ev):
        # foist a few more properties
        ev.__class__ = MidiEvent
        return self.fun(ev)


class Print(Call):
    def __init__(self, name=None):
        self.name = name
        Call.__init__(self, self.do_print)

    def do_print(self, ev):
        if self.name:
            print self.name + ":",

        if ev.type_ == TYPE_NOTEON:
            t = "note on"
            d1 = "note " + str(ev.note) + " (" + _util.notenumber2name(ev.note) + ")"
            d2 = "velocity " + str(ev.velocity)
        elif ev.type_ == TYPE_NOTEOFF:
            t = "note off"
            d1 = "note " + str(ev.note) + " (" + _util.notenumber2name(ev.note) + ")"
            d2 = "velocity " + str(ev.velocity)
        elif ev.type_ == TYPE_CTRL:
            t = "control change"
            d1 = "param " + str(ev.param)
            d2 = "value " + str(ev.value)
        elif ev.type_ == TYPE_PITCHBEND:
            t = "pitch bend"
            d1 = None
            d2 = "value " + str(ev.value)
        elif ev.type_ == TYPE_PROGRAM:
            t = "program change"
            d1 = None
            d2 = "program " + str(ev.program)
        else:
            t = "none"
            d1 = None
            d2 = "-"

        print "%s: port %d, channel %d," % (t, ev.port, ev.channel),
        if d1 != None:
            print "%s," % (d1,),
        print "%s" % (d2,)
