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

from mididings.units.base import _Unit, Filter, Split, Pass
from mididings.units.splits import VelocitySplit
from mididings.units.generators import NoteOn, NoteOff, PolyAftertouch

import mididings.util as _util
import mididings.misc as _misc
import mididings.overload as _overload
import mididings.constants as _constants
import mididings.arguments as _arguments
import mididings.unitrepr as _unitrepr


@_unitrepr.accept(_util.port_number)
def Port(port):
    """
    Port(port)

    Change the event's port number.
    """
    return _Unit(_mididings.Port(_util.actual(port)))


@_unitrepr.accept(_util.channel_number)
def Channel(channel):
    """
    Channel(channel)

    Change the event's channel number.
    """
    return _Unit(_mididings.Channel(_util.actual(channel)))


@_overload.mark(
    """
    Transpose(offset)
    Transpose(octaves=...)

    Transpose note events by the given number of semitones or octaves.
    """
)
@_unitrepr.accept(int)
def Transpose(offset):
    return _Unit(_mididings.Transpose(offset))

@_overload.mark
@_arguments.accept(int)
def Transpose(octaves):
    return Transpose(octaves * 12)


@_unitrepr.accept(_util.note_number)
def Key(note):
    """
    Key(note)

    Change note events to a fixed note number.
    """
    return _Unit(_mididings.Key(note))


@_overload.mark(
    """
    Velocity(offset)
    Velocity(multiply=...)
    Velocity(fixed=...)
    Velocity(curve=...)
    Velocity(gamma=...)
    Velocity(multiply, offset)

    Change the velocity of note-on events:

    - *offset*: add the given value to the event's velocity.
    - *multiply*: multiply the event's velocity with the given value.
    - *fixed*: set the event's velocity to a fixed value.
    - *curve*: apply an exponential function
      ``f(x) = 127 * (exp(p*x/127)-1) / (exp(p)-1)``.
      Positive values increase velocity, while negative values decrease it.
    - *gamma*: apply a simple power function
      ``f(x) = 127 * (x/127)**(1/p)``.
      Values greater than 1 increase velocity, while values between 0 and 1
      decrease it.
    """
)
@_unitrepr.accept(int)
def Velocity(offset):
    return _Unit(_mididings.Velocity(
                    offset, _mididings.TransformMode.OFFSET))

@_overload.mark
@_unitrepr.accept((float, int))
def Velocity(multiply):
    return _Unit(_mididings.Velocity(
                    multiply, _mididings.TransformMode.MULTIPLY))

@_overload.mark
@_unitrepr.accept(_util.velocity_value)
def Velocity(fixed):
    return _Unit(_mididings.Velocity(
                    fixed, _mididings.TransformMode.FIXED))

@_overload.mark
@_unitrepr.accept((float, int))
def Velocity(gamma):
    return _Unit(_mididings.Velocity(
                    gamma, _mididings.TransformMode.GAMMA))

@_overload.mark
@_unitrepr.accept((float, int))
def Velocity(curve):
    return _Unit(_mididings.Velocity(
                    curve, _mididings.TransformMode.CURVE))

@_overload.mark
@_unitrepr.accept((float, int), int)
def Velocity(multiply, offset):
    return Velocity(multiply=multiply) >> Velocity(offset=offset)


@_overload.mark(
    """
    VelocitySlope(notes, offset)
    VelocitySlope(notes, multiply=...)
    VelocitySlope(notes, fixed=...)
    VelocitySlope(notes, curve=...)
    VelocitySlope(notes, gamma=...)
    VelocitySlope(notes, multiply, offset)

    Change the velocity of note-on events, applying a linear slope between
    different notes. This can be thought of as a :func:`~.Velocity()` unit
    with different parameters for different note ranges, and is useful for
    example to fade-in a sound over a region of the keyboard.

    Both parameters must be sequences of the same length, with notes in
    ascending order, and one velocity parameter corresponding to each note.
    """
)
@_unitrepr.accept([_util.note_limit], [int])
def VelocitySlope(notes, offset):
    _check_velocity_slope(notes, offset)
    return _Unit(_mididings.VelocitySlope(
                    notes, offset, _mididings.TransformMode.OFFSET))

@_overload.mark
@_unitrepr.accept([_util.note_limit], [(float, int)])
def VelocitySlope(notes, multiply):
    _check_velocity_slope(notes, multiply)
    return _Unit(_mididings.VelocitySlope(
                    notes, multiply, _mididings.TransformMode.MULTIPLY))

@_overload.mark
@_unitrepr.accept([_util.note_limit], [_util.velocity_value])
def VelocitySlope(notes, fixed):
    _check_velocity_slope(notes, fixed)
    return _Unit(_mididings.VelocitySlope(
                    notes, fixed, _mididings.TransformMode.FIXED))

@_overload.mark
@_unitrepr.accept([_util.note_limit], [(float, int)])
def VelocitySlope(notes, gamma):
    _check_velocity_slope(notes, gamma)
    return _Unit(_mididings.VelocitySlope(
                    notes, gamma, _mididings.TransformMode.GAMMA))

@_overload.mark
@_unitrepr.accept([_util.note_limit], [(float, int)])
def VelocitySlope(notes, curve):
    _check_velocity_slope(notes, curve)
    return _Unit(_mididings.VelocitySlope(
                    notes, curve, _mididings.TransformMode.CURVE))

@_overload.mark
@_unitrepr.accept([_util.note_limit], [(float, int)], [int])
def VelocitySlope(notes, multiply, offset):
    return (VelocitySlope(notes, multiply=multiply)
            >> VelocitySlope(notes, offset=offset))


def _check_velocity_slope(notes, params):
    message = None
    if len(notes) != len(params):
        message = ("invalid parameters to VelocitySlope(): notes and velocity"
                   "values must be sequences of the same length")
    elif len(notes) < 2:
        message = ("invalid parameters to VelocitySlope(): need at least"
                   "two notes")
    elif sorted(notes) != list(notes):
        message = ("invalid parameters to VelocitySlope(): notes must be in"
                   "ascending order")

    if message is not None:
        raise ValueError(message)


@_overload.mark(
    """
    VelocityLimit(min, max)
    VelocityLimit(min)
    VelocityLimit(max=...)

    Limit velocities of note-on events to the given range.
    """
)
@_arguments.accept(_util.velocity_limit, _util.velocity_limit)
def VelocityLimit(min, max):
    return Filter(_constants.NOTE) % VelocitySplit({
        (0, min):   Velocity(fixed=min),
        (min, max): Pass(),
        (max, 0):   Velocity(fixed=max),
    })

@_overload.mark
@_arguments.accept(_util.velocity_limit)
def VelocityLimit(max):
    return Filter(_constants.NOTE) % VelocitySplit({
        (0, max):   Pass(),
        (max, 0):   Velocity(fixed=max),
    })

@_overload.mark
@_arguments.accept(_util.velocity_limit)
def VelocityLimit(min):
    return Filter(_constants.NOTE) % VelocitySplit({
        (0, min):   Velocity(fixed=min),
        (min, 0):   Pass(),
    })


@_unitrepr.accept(_util.ctrl_number, _util.ctrl_number)
def CtrlMap(ctrl_in, ctrl_out):
    """
    CtrlMap(ctrl_in, ctrl_out)

    Convert controller *ctrl_in* to *ctrl_out*, i.e. change the event's
    control change number.
    """
    return _Unit(_mididings.CtrlMap(ctrl_in, ctrl_out))


@_unitrepr.accept(_util.ctrl_number, int, int, int, int)
def CtrlRange(ctrl, min, max, in_min=0, in_max=127):
    """
    CtrlRange(ctrl, min, max, in_min=0, in_max=127)

    Linearly map control change values for controller *ctrl* from the interval
    [*in_min*, *in_max*] to the interval [*min*, *max*].
    Any input value less than or equal to *in_min* results in an output value
    of *min*. Likewise, any value of *in_max* or greater results in an output
    value of *max*.
    """
    if in_min > in_max:
        # swap ranges so that in_min is less than in_max
        in_min, in_max = in_max, in_min
        min, max = max, min
    return _Unit(_mididings.CtrlRange(ctrl, min, max, in_min, in_max))


@_overload.mark(
    """
    CtrlCurve(ctrl, gamma)
    CtrlCurve(ctrl, curve=...)
    CtrlCurve(ctrl, offset=...)
    CtrlCurve(ctrl, multiply=...)
    CtrlCurve(ctrl, multiply, offset)

    Transform control change values. See :func:`~.Velocity()` for a
    description of the parameters.
    """
)
@_unitrepr.accept(_util.ctrl_number, (float, int))
def CtrlCurve(ctrl, gamma):
    return _Unit(_mididings.CtrlCurve(
                        ctrl, gamma, _mididings.TransformMode.GAMMA))

@_overload.mark
@_unitrepr.accept(_util.ctrl_number, (float, int))
def CtrlCurve(ctrl, curve):
    return _Unit(_mididings.CtrlCurve(
                        ctrl, curve, _mididings.TransformMode.CURVE))

@_overload.mark
@_unitrepr.accept(_util.ctrl_number, int)
def CtrlCurve(ctrl, offset):
    return _Unit(_mididings.CtrlCurve(
                        ctrl, offset, _mididings.TransformMode.OFFSET))

@_overload.mark
@_unitrepr.accept(_util.ctrl_number, (float, int))
def CtrlCurve(ctrl, multiply):
    return _Unit(_mididings.CtrlCurve(
                        ctrl, multiply, _mididings.TransformMode.MULTIPLY))

@_overload.mark
@_unitrepr.accept(_util.ctrl_number, (float, int), int)
def CtrlCurve(ctrl, multiply, offset):
    return (CtrlCurve(ctrl, multiply=multiply)
            >> CtrlCurve(ctrl, offset=offset))


@_overload.mark(
    """
    PitchbendRange(min, max, in_min=-8192, in_max=8191)
    PitchbendRange(down, up, range=...)

    Change the pitchbend range to values between *min* and *max*, or to the
    given number of semitones *down* and *up*. The latter requires the tone
    generator's pitchbend range to be specified as *range*.
    """
)
@_unitrepr.accept(int, int, int, int)
def PitchbendRange(min, max, in_min=-8192, in_max=8191):
    return _Unit(_mididings.PitchbendRange(min, max, in_min, in_max))

@_overload.mark
@_unitrepr.accept(int, int, int)
def PitchbendRange(down, up, range):
    return PitchbendRange(int(float(down)/range*8192),
                          int(float(up)/range*8191))
