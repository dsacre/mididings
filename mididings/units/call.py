# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2014  Dominic Sacré  <dominic.sacre@gmx.de>
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
import inspect as _inspect


class _CallBase(_Unit):
    def __init__(self, function, is_async, cont):
        def do_call(ev):
            # add additional properties that don't exist on the C++ side
            ev.__class__ = _event.MidiEvent

            # call the function
            ret = function(ev)

            if ret is None or is_async:
                return None
            elif isinstance(ret, _types.GeneratorType):
                # function is a generator, build list
                ret = list(ret)
            elif not _misc.issequence(ret):
                ret = [ret]

            for ev in ret:
                ev._finalize()
            return ret

        _Unit.__init__(self, _mididings.Call(do_call, is_async, cont))


class _CallThread(_CallBase):
    def __init__(self, function):
        def do_thread(ev):
            # need to make a copy of the event. the underlying C++ object will
            # become invalid once this function returns
            ev_copy = _copy.copy(ev)
            _thread.start_new_thread(function, (ev_copy,))

        _CallBase.__init__(self, do_thread, True, False)


class _System(_CallBase):
    def __init__(self, command):
        def do_system(ev):
            args = command(ev) if hasattr(command, '__call__') else command
            _subprocess.Popen(args, shell=True)

        _CallBase.__init__(self, do_system, True, False)


def _call_partial(function, args, kwargs, require_event=False):
    """
    Add args and kwargs when calling function (similar to functools.partial).
    Also, allow omission of the first argument (event) if require_event
    is False.
    """
    try:
        argspec = _inspect.getargspec(function)
        ismethod = _inspect.ismethod(function)
    except TypeError:
        # support callable objects
        argspec = _inspect.getargspec(function.__call__)
        ismethod = _inspect.ismethod(function.__call__)

    if (not require_event and argspec[1] == None
                and len(argspec[0]) - int(ismethod) == 0):
        # omit event argument when function has no positional arguments
        if len(kwargs):
            return lambda ev: function(**kwargs)
        else:
            return lambda ev: function()
    if len(args) or len(kwargs):
        # return a function with args and kwargs applied
        return lambda ev: function(ev, *args, **kwargs)
    else:
        # no additional arguments, no wrapper needed
        return function


@_unitrepr.accept(_collections.abc.Callable, None, kwargs={ None: None })
def Process(function, *args, **kwargs):
    """
    Process(function, *args, **kwargs)

    Process the incoming MIDI event using a Python function, then continue
    executing the mididings patch with the events returned from that
    function.

    :param function:
        a function, or any other callable object, that will be called with
        a :class:`~.MidiEvent` object as its first argument.

        The function's return value can be:
          - a single :class:`~.MidiEvent` object.
          - a list of :class:`~.MidiEvent` objects.
          - ``None`` (or an empty list).

        Instead of ``return``\ ing :class:`~.MidiEvent` objects, *function*
        may also be a generator that ``yield``\ s :class:`~.MidiEvent`
        objects.

    :param \*args:
        optional positional arguments that will be passed to *function*.

    :param \*\*kwargs:
        optional keyword arguments that will be passed to *function*.


    Any other MIDI processing will be stalled until *function* returns,
    so this should only be used with functions that don't block.
    Use :func:`Call()` for tasks that may take longer and/or don't require
    returning any MIDI events.
    """
    if _get_config('backend') == 'jack-rt' and not _get_config('silent'):
        print("WARNING: using Process() with the 'jack-rt' backend"
              " is probably a bad idea")
    return _CallBase(_call_partial(function, args, kwargs, True), False, False)


@_overload.mark(
    """
    Call(function, *args, **kwargs)
    Call(thread=..., **kwargs)

    Schedule a Python function for execution.
    The incoming event is discarded.

    :param function:
        a function, or any other callable object.
        If the function accepts arguments, its first argument will be a copy
        of the :class:`~.MidiEvent` that triggered the function call.

        The function's return value is ignored.

    :param thread:
        like *function*, but causes the function to be run in its own thread.

    :param \*args:
        optional positional arguments that will be passed to *function*.

    :param \*\*kwargs:
        optional keyword arguments that will be passed to *function*.
    """
)
@_unitrepr.accept(_collections.abc.Callable, None, kwargs={ None: None })
def Call(function, *args, **kwargs):
    return _CallBase(_call_partial(function, args, kwargs), True, False)

@_overload.mark
@_unitrepr.accept(_collections.abc.Callable, kwargs={ None: None })
def Call(thread, **kwargs):
    return _CallThread(_call_partial(thread, (), kwargs))


@_unitrepr.accept((str, _collections.abc.Callable))
def System(command):
    """
    Run an arbitrary shell command.
    The incoming event is discarded.

    :param command:
        a string which will be passed verbatim to the shell.

        Alternatively it may also be a Python function that accepts a
        :class:`~.MidiEvent` argument and returns the command string to
        be executed.
    """
    return _System(command)
