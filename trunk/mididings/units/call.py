# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2012  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import _mididings

from mididings.units.base import _Unit, _unit_repr

import mididings.event as _event
import mididings.overload as _overload
from mididings.setup import get_config as _get_config

import sys as _sys
if _sys.version_info >= (3,):
    import _thread
else:
    import thread as _thread
import subprocess as _subprocess
import functools as _functools
import types as _types
import copy as _copy


class _CallBase(_Unit):
    def __init__(self, function, async, cont):
        def do_call(ev):
            # add additional properties that don't exist on the C++ side
            ev.__class__ = _event.MidiEvent
            # call the function
            r = function(ev)
            # if the function returned a generator, it needs to be made into a list
            # before returning to C++
            if isinstance(r, _types.GeneratorType):
                return list(r)
            else:
                return r

        _Unit.__init__(self, _mididings.Call(do_call, async, cont))


class _CallThread(_CallBase):
    def __init__(self, function):
        def do_thread(ev):
            # need to make a copy of the event.
            # the underlying C++ object will become invalid when this function returns
            ev_copy = _copy.copy(ev)
            _thread.start_new_thread(function, (ev_copy,))

        _CallBase.__init__(self, do_thread, True, True)


class _System(_CallBase):
    def __init__(self, command):
        def do_system(ev):
            args = command(ev) if hasattr(command, '__call__') else command
            _subprocess.Popen(args, shell=True)

        _CallBase.__init__(self, do_system, True, True)


@_unit_repr
def Process(function):
    if _get_config('backend') == 'jack-rt' and not _get_config('silent'):
        print("WARNING: using Process() with the 'jack-rt' backend is probably a bad idea")
    return _CallBase(function, False, False)


@_unit_repr
@_overload.mark
def Call(function):
    def wrapper(function, ev):
        if function(ev) != None:
            print("return value from Call() ignored. please use Process() instead")
    return _CallBase(_functools.partial(wrapper, function), True, True)

@_unit_repr
@_overload.mark
def Call(thread):
    return _CallThread(thread)


@_unit_repr
def System(command):
    return _System(command)
