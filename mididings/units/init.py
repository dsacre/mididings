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

from mididings.units.base import _Unit, Fork, Chain, _UNIT_TYPES
from mididings.units.generators import Program, Ctrl
from mididings.units.modifiers import Port, Channel

import mididings.unitrepr as _unitrepr
import mididings.util as _util

import functools as _functools
import copy as _copy


class _InitExit(_Unit):
    def __init__(self, init_patch=[], exit_patch=[]):
        self.init_patch = init_patch
        self.exit_patch = exit_patch


@_unitrepr.accept(_UNIT_TYPES)
def Init(patch):
    """
    Init(patch)

    Add *patch* to the init patch of the scene containing this unit, so that
    it will be executed when switching to this scene.
    The patch is added in parallel to whatever is already in the init patch.

    This unit does no event processing in the patch it is inserted in, and
    discards all events.
    """
    return _InitExit(init_patch=patch)


@_unitrepr.accept(_UNIT_TYPES)
def Exit(patch):
    """
    Exit(patch)

    Add *patch* to the exit patch of the scene containing this unit, so that
    it will be executed when leaving this scene, switching to a different one.
    The patch is added in parallel to whatever is already in the exit patch.

    This unit does no event processing in the patch it is inserted in, and
    discards all events.
    """
    return _InitExit(exit_patch=patch)


def Output(port=None, channel=None, program=None,
           volume=None, pan=None, expression=None, ctrls={}):
    """
    Output(port=None, channel=None, program=None, volume=None, pan=None, expression=None, ctrls={})

    Route incoming events to the specified *port* and *channel*.
    When switching to the scene containing this unit, a program change and/or
    arbitrary control changes can be sent.

    To send a bank select (CC #0 and CC #32) before the program change,
    *program* can be a tuple with two elements, where the first element is the
    bank number, and the second is the program number.

    Values for the commonly used controllers *volume* (#7), *pan* (#10) and
    *expression* (#11) can be specified directly. For all other controllers,
    the *ctrls* argument can contain a mapping from controller numbers to
    their respective values.

    If *port* or *channel* are ``None``, events will be routed to the first
    port/channel.
    """
    if port is None:
        port = _util.offset(0)
    if channel is None:
        channel = _util.offset(0)

    if isinstance(program, tuple):
        bank, program = program
    else:
        bank = None

    init = []

    if bank is not None:
        init.append(Ctrl(port, channel, 0, bank // 128))
        init.append(Ctrl(port, channel, 32, bank % 128))

    if program is not None:
        init.append(Program(port, channel, program))

    if volume is not None:
        init.append(Ctrl(port, channel, 7, volume))
    if pan is not None:
        init.append(Ctrl(port, channel, 10, pan))
    if expression is not None:
        init.append(Ctrl(port, channel, 11, expression))

    for k, v in ctrls.items():
        init.append(Ctrl(port, channel, k, v))

    return Fork([
        Init(init),
        Port(port) >> Channel(channel)
    ])


class OutputTemplate(object):
    """
    OutputTemplate(*args, **kwargs)

    Create an object that when called will behave like :func:`~.Output()`,
    with *args* and *kwargs* replacing some of its arguments.
    That is, :class:`~.OutputTemplate()` is not a unit by itself, but returns
    one when called.

    This works just like ``functools.partial(Output, *args, **kwargs)``, but
    with the added benefit that an :class:`~.OutputTemplate()` object also
    supports operator ``>>`` like any unit.
    """
    def __init__(self, *args, **kwargs):
        self.partial = _functools.partial(Output, *args, **kwargs)
        self.before = []
        self.after = []

    def __call__(self, *args, **kwargs):
        return (Chain(self.before)
                >> self.partial(*args, **kwargs)
                >> Chain(self.after))

    def __rshift__(self, other):
        if not isinstance(other, _UNIT_TYPES):
            return NotImplemented
        r = _copy.copy(self)
        r.after = self.after + [other]
        return r

    def __rrshift__(self, other):
        if not isinstance(other, _UNIT_TYPES):
            return NotImplemented
        r = _copy.copy(self)
        r.before = [other] + self.before
        return r
