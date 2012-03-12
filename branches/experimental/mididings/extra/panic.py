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

from mididings import *
import mididings.engine as _engine
import mididings.event as _event
import mididings.util as _util


def _panic_bypass():
    # send all notes off (CC #123) and sustain off (CC #64) to all output ports and on all channels
    for p in _engine.out_ports():
        for c in range(16):
            _engine.output_event(_event.CtrlEvent(p, _util.NoDataOffset(c), 123, 0))
            _engine.output_event(_event.CtrlEvent(p, _util.NoDataOffset(c), 64, 0))


def Panic(bypass=True):
    if bypass:
        return Call(lambda ev: _panic_bypass()) >> Discard()
    else:
        return Fork([
            (Ctrl(p, _util.NoDataOffset(c), 123, 0) // Ctrl(p, _util.NoDataOffset(c), 64, 0))
                for p in _engine.out_ports()
                for c in range(16)
        ])
