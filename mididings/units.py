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
import misc as _misc
from event import *

import thread as _thread


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


# split events by type
class Split(dict, _Unit):
    def __init__(self, d):
        dict.__init__(self, d)


# base class for all filters, supporting operator ~
class _Filter(_Unit):
    def __invert__(self):
        return _InvertedFilter(self, not isinstance(self, Filter))


class _InvertedFilter(_mididings.InvertedFilter, _Unit):
    pass


class Pass(_mididings.Pass, _Unit):
    def __init__(self, p=True):
        _mididings.Pass.__init__(self, p)

def Discard():
    return Pass(False)


### filters ###

class Filter(_mididings.Filter, _Filter):
    def __init__(self, *args):
        if len(args) > 1:
            types = reduce(lambda x,y: x|y, args)
        else:
            types = args[0]
        _mididings.Filter.__init__(self, types)


class PortFilter(_mididings.PortFilter, _Filter):
    def __init__(self, *args):
        v = _misc.make_int_vector((_misc.port_number(p) for p in _misc.flatten(args)))
        _mididings.PortFilter.__init__(self, v)


class ChannelFilter(_mididings.ChannelFilter, _Filter):
    def __init__(self, *args):
        v = _misc.make_int_vector((_misc.channel_number(c) for c in _misc.flatten(args)))
        _mididings.ChannelFilter.__init__(self, v)


class KeyFilter(_mididings.KeyFilter, _Filter):
    def __init__(self, *args):
        if len(args) == 1:
            args = args[0]
        r = _misc.noterange2numbers(args)
        _mididings.KeyFilter.__init__(self, r[0], r[1])


class VelocityFilter(_mididings.VelocityFilter, _Filter):
    def __init__(self, *args):
        if len(args) == 1:
            args = args[0]
        _mididings.VelocityFilter.__init__(self, args[0], args[1])


class CtrlFilter(_mididings.CtrlFilter, _Filter):
    def __init__(self, *args):
        v = _misc.make_int_vector(_misc.flatten(args))
        _mididings.CtrlFilter.__init__(self, v)


class CtrlValueFilter(_mididings.CtrlValueFilter, _Filter):
    def __init__(self, lower, upper=0):
        _mididings.CtrlValueFilter.__init__(self, lower, upper)


class ProgFilter(_mididings.ProgFilter, _Filter):
    def __init__(self, *args):
        v = _misc.make_int_vector((_misc.program_number(p) for p in _misc.flatten(args)))
        _mididings.ProgFilter.__init__(self, v)


### splits ###

def PortSplit(d):
    return Fork([ (PortFilter(p) >> w) for p, w in d.items() ])

def ChannelSplit(d):
    return Fork([ (ChannelFilter(c) >> w) for c, w in d.items() ])


def KeySplit(*args):
    if len(args) == 1:
        # KeySplit(d)
        return Fork([
            (Fork([ KeyFilter(k), ~Filter(NOTE) ]) >> w) for k, w in args[0].items()
        ])
    elif len(args) == 3:
        # KeySplit(key, unit_lower, unit_upper)
        key, unit_lower, unit_upper = args
        filt = KeyFilter(0, key)
        return Fork([
            Fork([  filt, ~Filter(NOTE) ]) >> unit_lower,
            Fork([ ~filt, ~Filter(NOTE) ]) >> unit_upper
        ])
    else:
        raise ArgumentError()


def VelocitySplit(*args):
    if len(args) == 1:
        # VelocitySplit(d)
        return Fork([
            (Fork([ VelocityFilter(v), ~Filter(NOTE) ]) >> w) for v, w in args[0].items()
        ])
    elif len(args) == 3:
        # VelocitySplit(thresh, unit_lower, unit_upper)
        thresh, unit_lower, unit_upper = args
        filt = VelocityFilter(0, thresh)
        return Fork([
            Fork([  filt, ~Filter(NOTE) ]) >> unit_lower,
            Fork([ ~filt, ~Filter(NOTE) ]) >> unit_upper
        ])
    else:
        raise ArgumentError()


### modifiers ###

class Port(_mididings.Port, _Unit):
    def __init__(self, port):
        _mididings.Port.__init__(self, _misc.port_number(port))


class Channel(_mididings.Channel, _Unit):
    def __init__(self, channel):
        _mididings.Channel.__init__(self, _misc.channel_number(channel))


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
            _misc.note2number(note_lower), _misc.note2number(note_upper),
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


### misc ###

class GenerateEvent(_mididings.GenerateEvent, _Unit):
    def __init__(self, type_, port, channel, data1, data2):
        _mididings.GenerateEvent.__init__(self, type_,
                _misc.port_number(port) if isinstance(port, str) or port >= 0 else port,
                _misc.channel_number(channel) if channel >= 0 else channel,
                data1, data2)


def CtrlChange(*args):
    if len(args) == 2:
        # CrtlChange(ctrl, value)
        ctrl, value = args
        return GenerateEvent(CTRL, EVENT_PORT, EVENT_CHANNEL, ctrl, value)
    elif len(args) == 4:
        # CrtlChange(port, channel, ctrl, value)
        port, channel, ctrl, value = args
        return GenerateEvent(CTRL, port, channel, ctrl, value)
    else:
        raise ArgumentError()


def ProgChange(*args):
    if len(args) == 1:
        # ProgChange(program)
        return GenerateEvent(PROGRAM, EVENT_PORT, EVENT_CHANNEL, 0, _misc.program_number(args[0]))
    elif len(args) == 3:
        # ProgChange(port, channel, program)
        port, channel, program = args
        return GenerateEvent(PROGRAM, port, channel, 0, _misc.program_number(program))
    else:
        raise ArgumentError()


class Sanitize(_mididings.Sanitize, _Unit):
    def __init__(self):
        _mididings.Sanitize.__init__(self)


class PatchSwitch(_mididings.PatchSwitch, _Unit):
    def __init__(self, num=EVENT_PROGRAM):
        _mididings.PatchSwitch.__init__(self, num)


class _CallBase(_mididings.Call, _Unit):
    def __init__(self, fun, async, cont):
        self.fun = fun
        _mididings.Call.__init__(self, self.do_call, async, cont)
    def do_call(self, ev):
        # add additional properties
        ev.__class__ = MidiEvent
        return self.fun(ev)

class Call(_CallBase):
    def __init__(self, fun):
        _CallBase.__init__(self, fun, False, False)

class CallAsync(_CallBase):
    def __init__(self, fun, cont=False):
        _CallBase.__init__(self, fun, True, cont)

class CallThread(_CallBase):
    def __init__(self, fun, cont=False):
        self.fun_thread = fun
        _CallBase.__init__(self, self.do_thread, True, cont)
    def do_thread(self, ev):
        # need to make a copy of the event. the underlying C++ object will become invalid when this function returns
        ev_copy = MidiEvent(ev.type_, ev.port_, ev.channel_, ev.data1, ev.data2)
        _thread.start_new_thread(self.fun_thread, (ev_copy,))


class Print(_CallBase):
    PORTNAMES_NONE = 0
    PORTNAMES_IN   = 1
    PORTNAMES_OUT  = 2

    def __init__(self, name=None, types=ANY, portnames=PORTNAMES_NONE):
        self.name = name
        self.types = types
        self.ports = portnames
        _CallBase.__init__(self, self.do_print, True, True)

    def do_print(self, ev):
        # delayed 'til first use, because _main.TheSetup doesn't yet exist during __init__
        if not hasattr(self, 'portnames'):
            if self.ports == Print.PORTNAMES_NONE:
                self.portnames = []
            elif self.ports == Print.PORTNAMES_IN:
                self.portnames = _main.TheSetup.in_ports
            elif self.ports == Print.PORTNAMES_OUT:
                self.portnames = _main.TheSetup.out_ports
            self.portname_length = max((len(p) for p in self.portnames))

        if ev.type_ & self.types:
            if self.name:
                print self.name + ":",
            print ev.to_string(self.portnames, self.portname_length)
