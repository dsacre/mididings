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

from mididings.units.base import _Unit, _unit_repr

import mididings.event as _event
import mididings.misc as _misc
from mididings.setup import get_config as _get_config

import thread as _thread
import subprocess as _subprocess
import functools as _functools
import inspect as _inspect


class _CallBase(_Unit):
    def __init__(self, function, async, cont):
        self.fun = function
        _Unit.__init__(self, _mididings.Call(self.do_call, async, cont))
    def do_call(self, ev):
        # add additional properties that don't exist on the C++ side
        ev.__class__ = _event.MidiEvent
        # call the function
        r = self.fun(ev)
        # if the function returned a generator, it needs to be made into a list before returning to C++
        if _inspect.isgenerator(r):
            return list(r)
        else:
            return r


class _CallThread(_CallBase):
    def __init__(self, function):
        self.fun_thread = function
        _CallBase.__init__(self, self.do_thread, True, True)
    def do_thread(self, ev):
        # need to make a copy of the event.
        # the underlying C++ object will become invalid when this function returns
        ev_copy = _event.MidiEvent(ev.type, ev.port_, ev.channel_, ev.data1, ev.data2)
        _thread.start_new_thread(self.fun_thread, (ev_copy,))


class _System(_CallBase):
    def __init__(self, cmd):
        self.cmd = cmd
        _CallBase.__init__(self, self.do_system, True, True)
    def do_system(self, ev):
        cmd = self.cmd(ev) if callable(self.cmd) else self.cmd
        _subprocess.Popen(cmd, shell=True)


@_unit_repr
def Process(function):
    if _get_config('verbose') and _get_config('backend') == 'jack-rt':
        print "WARNING: using Process() with the 'jack-rt' backend is probably a bad idea"
    return _CallBase(function, False, False)


@_unit_repr
@_misc.overload
def Call(function):
    def wrapper(function, ev):
        if function(ev) != None:
            print "return value from Call() ignored. please use Process() instead"
    return _CallBase(_functools.partial(wrapper, function), True, True)

@_unit_repr
@_misc.overload
def Call(thread):
    return _CallThread(thread)


@_misc.deprecated('Call')
def CallAsync(function):
    return Call(function)

@_misc.deprecated('Call')
def CallThread(function):
    return Call(thread=function)


@_unit_repr
def System(cmd):
    return _System(cmd)
