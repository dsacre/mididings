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

import mididings as _m
import mididings.engine as _engine
import mididings.event as _event
import mididings.util as _util


def _panic_bypass():
    # send all notes off (CC #123) and sustain off (CC #64) to all output
    # ports and on all channels
    for p in _engine.out_ports():
        for c in range(16):
            _engine.output_event(
                _event.CtrlEvent(p, _util.offset(c), 123, 0))
            _engine.output_event(
                _event.CtrlEvent(p, _util.offset(c), 64, 0))


def Panic(bypass=True):
    """
    Generate all-notes-off (CC #123) and sustain off (CC #64) events on
    all channels.

    :param bypass:
        If true, events will be sent directly on all output ports, instead
        of originating from the :func:`Panic()` unit and being subject to
        further processing.
    """
    if bypass:
        return _m.Call(lambda ev: _panic_bypass())
    else:
        return _m.Fork([
            (_m.Ctrl(p, _util.offset(c), 123, 0) //
             _m.Ctrl(p, _util.offset(c), 64, 0))
                for p in _engine.out_ports()
                for c in range(16)
        ])
