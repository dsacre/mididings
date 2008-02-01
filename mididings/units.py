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
from event import _MidiEventEx


class _Unit:
    def __rshift__(self, other):
        return _Chain(self, other)

    def __rrshift__(self, other):
        return _Chain(other, self)


class _Chain(_Unit):
    def __init__(self, first, second):
        self.items = first, second


class Fork(list, _Unit):
    def __init__(self, l):
        list.__init__(self, l)


class TypeFork(Fork):
    def __init__(self, t, l):
        a = [ (TypeFilter(t) >> x) for x in l ] + \
            [ ~TypeFilter(t) ]
        list.__init__(self, a)

def NoteFork(x):
    return TypeFork(TYPE_NOTE, x)

def ControllerFork(x):
    return TypeFork(TYPE_CONTROLLER, x)

def PitchBendFork(x):
    return TypeFork(TYPE_PITCHBEND, x)

def ProgramChangeFork(x):
    return TypeFork(TYPE_PGMCHANGE, x)


# base class for all filters, supporting operator ~
class _Filter(_Unit):
    def __invert__(self):
        return _InvertedFilter(self)

class _Modifier(_Unit):
    pass


class _InvertedFilter(_mididings.InvertedFilter, _Unit):
    pass


class Pass(_mididings.Pass, _Unit):
    def __init__(self, p=True):
        _mididings.Pass.__init__(self, p)

def Discard():
    return Pass(False)


### filters ###

class TypeFilter(_mididings.TypeFilter, _Filter):
    def __init__(self, type_):
        _mididings.TypeFilter.__init__(self, type_)

def NoteGate():
    return TypeFilter(TYPE_NOTE)

def ControllerGate():
    return TypeFilter(TYPE_CONTROLLER)

def PitchBendGate():
    return TypeFilter(TYPE_PITCHBEND)

def ProgramChangeGate():
    return TypeFilter(TYPE_PGMCHANGE)


class PortFilter(_mididings.PortFilter, _Filter):
    def __init__(self, *args):
        vec = _mididings.int_vector()
        for port in _util.flatten(args):
            vec.push_back(port - _main.PORT_OFFSET)
        _mididings.PortFilter.__init__(self, vec)


class ChannelFilter(_mididings.ChannelFilter, _Filter):
    def __init__(self, *args):
        vec = _mididings.int_vector()
        for c in _util.flatten(args):
            vec.push_back(c - _main.CHANNEL_OFFSET)
        _mididings.ChannelFilter.__init__(self, vec)


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


class ControllerFilter(_mididings.ControllerFilter, _Filter):
    def __init__(self, controller):
        _mididings.ControllerFilter.__init__(self, controller)


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
        # KeySplit(key, units_lower, units_upper)
        key, units_lower, units_upper = args
        filt = KeyFilter(0, key)
        return NoteFork([ filt >> units_lower, ~filt >> units_upper ])
    else:
        raise ArgumentError()


def VelocitySplit(*args):
    if len(args) == 1:
        # VelocitySplit(d)
        return NoteFork([ (VelocityFilter(v) >> w) for v, w in args[0].items() ])
    elif len(args) == 3:
        # VelocitySplit(thresh, units_lower, units_upper)
        thresh, units_lower, units_upper = args
        filt = VelocityFilter(0, thresh)
        return NoteFork([ filt >> units_lower, ~filt >> units_upper ])
    else:
        raise ArgumentError()


### modifiers ###

class Port(_mididings.Port, _Modifier):
    def __init__(self, port):
        _mididings.Port.__init__(self, port - _main.PORT_OFFSET)


class Channel(_mididings.Channel, _Modifier):
    def __init__(self, channel):
        _mididings.Channel.__init__(self, channel - _main.CHANNEL_OFFSET)


class Transpose(_mididings.Transpose, _Modifier):
    def __init__(self, offset):
        _mididings.Transpose.__init__(self, offset)


class Velocity(_mididings.Velocity, _Modifier):
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


class VelocityGradient(_mididings.VelocityGradient, _Modifier):
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


class ControllerRange(_mididings.ControllerRange, _Modifier):
    def __init__(self, controller, in_min, in_max, out_min, out_max):
        _mididings.ControllerRange.__init__(self, controller, in_min, in_max, out_min, out_max)


### misc ###

class GenerateEvent(_mididings.GenerateEvent, _Unit):
    def __init__(self, type_, port, channel, data1, data2):
        _mididings.GenerateEvent.__init__(self, type_,
                port - _main.PORT_OFFSET if port >= 0 else port,
                channel - _main.CHANNEL_OFFSET if channel >= 0 else channel,
                data1, data2)

def ControlChange(port, channel, controller, value):
    return GenerateEvent(TYPE_CONTROLLER, port, channel, controller, value)

def ProgramChange(port, channel, program):
    return GenerateEvent(TYPE_PGMCHANGE, port, channel, 0, program - _main.PROGRAM_OFFSET)


class PatchSwitcher(_mididings.PatchSwitcher, _Unit):
    def __init__(self, num=PROGRAM):
        _mididings.PatchSwitcher.__init__(self, num)


class Call(_mididings.Call, _Unit):
    def __init__(self, fun):
        self.fun = fun
        _mididings.Call.__init__(self, self.do_call)
    def do_call(self, ev):
        # foist a few more properties
        ev.__class__ = _MidiEventEx
        return self.fun(ev)

#class CallAsync(_mididings.Call, _Unit):
#    def __init__(self, fun):
#        self.fun = fun
#        _mididings.Call.__init__(self, self.do_call_async)
#    def do_call_async(self, ev):
#        ev.__class__ = _MidiEventEx
#        Q.put((self.fun, ev))
#        return False


class Print(Call):
    def __init__(self, name=None):
        self.name = name
        Call.__init__(self, self.do_print)

    def do_print(self, ev):
        if self.name:
            print self.name + ":",

        if ev.type == TYPE_NOTEON:
            t = "note on"
            d1 = "note " + str(ev.note) + " (" + _util.notenumber2name(ev.note) + ")"
            d2 = "velocity " + str(ev.velocity)
        elif ev.type == TYPE_NOTEOFF:
            t = "note off"
            d1 = "note " + str(ev.note) + " (" + _util.notenumber2name(ev.note) + ")"
            d2 = "velocity " + str(ev.velocity)
        elif ev.type == TYPE_CONTROLLER:
            t = "control change"
            d1 = "param " + str(ev.param)
            d2 = "value " + str(ev.value)
        elif ev.type == TYPE_PITCHBEND:
            t = "pitch bend"
            d1 = None
            d2 = "value " + str(ev.value)
        elif ev.type == TYPE_PGMCHANGE:
            t = "program change"
            d1 = None
            d2 = "value " + str(ev.program)

        print "%s: port %d, channel %d," % (t, ev.port, ev.channel),
        if d1: print "%s," % (d1,),
        print "%s" % (d2,)
