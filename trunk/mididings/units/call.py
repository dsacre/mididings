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

from mididings.units.base import _Unit

import mididings.event as _event
import mididings.overload as _overload
import mididings.unitrepr as _unitrepr
import mididings.misc as _misc
from mididings.setup import get_config as _get_config

import sys as _sys
if _sys.version_info >= (3,):
    import _thread
else:
    import thread as _thread
import subprocess as _subprocess
import types as _types
import copy as _copy
import collections as _collections

if _sys.version_info >= (2, 6):
    _callable_constraint = _collections.Callable
else:
    import mididings.arguments as _arguments
    _callable_constraint = _arguments.condition(lambda c: callable(c))


class _CallBase(_Unit):
    def __init__(self, function, async, cont):
        def do_call(ev):
            # add additional properties that don't exist on the C++ side
            ev.__class__ = _event.MidiEvent

            # call the function
            ret = function(ev)

            if ret is None or async:
                return None
            elif isinstance(ret, _types.GeneratorType):
                # function is a generator, build list
                ret = list(ret)
            elif not _misc.issequence(ret):
                ret = [ret]

            for ev in ret:
                ev._finalize()
            return ret

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


@_unitrepr.accept(_callable_constraint)
def Process(function):
    if _get_config('backend') == 'jack-rt' and not _get_config('silent'):
        print("WARNING: using Process() with the 'jack-rt' backend is probably a bad idea")
    return _CallBase(function, False, False)


@_overload.mark
@_unitrepr.accept(_callable_constraint)
def Call(function):
    return _CallBase(function, True, True)

@_overload.mark
@_unitrepr.accept(_callable_constraint)
def Call(thread):
    return _CallThread(thread)


@_unitrepr.accept((str, _callable_constraint))
def System(command):
    return _System(command)
