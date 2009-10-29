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

import mididings.event as _event

import thread as _thread
import subprocess as _subprocess


class _CallBase(_Unit):
    def __init__(self, fun, async, cont):
        self.fun = fun
        _Unit.__init__(self, _mididings.Call(self.do_call, async, cont))
    def do_call(self, ev):
        # add additional properties that don't exist on the C++ side
        ev.__class__ = _event.MidiEvent
        return self.fun(ev)


class _CallThread(_CallBase):
    def __init__(self, fun):
        self.fun_thread = fun
        _CallBase.__init__(self, self.do_thread, True, True)
    def do_thread(self, ev):
        # need to make a copy of the event.
        # the underlying C++ object will become invalid when this function returns
        ev_copy = _event.MidiEvent(ev.type_, ev.port_, ev.channel_, ev.data1, ev.data2)
        _thread.start_new_thread(self.fun_thread, (ev_copy,))


@_unit_repr
def Call(fun):
    return _CallBase(fun, False, False)


@_unit_repr
def CallAsync(fun):
    return _CallBase(fun, True, True)


@_unit_repr
def CallThread(fun):
    return _CallThread(fun)


class _System(_CallBase):
    def __init__(self, cmd):
        self.cmd = cmd
        CallBase.__init__(self, self.do_system, True, True)
    def do_system(self, ev):
        cmd = self.cmd(ev) if callable(self.cmd) else self.cmd
        _subprocess.Popen(cmd, shell=True)


@_unit_repr
def System(cmd):
    return _System(cmd)
