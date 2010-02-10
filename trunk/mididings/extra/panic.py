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

from mididings import *
import mididings.engine as _engine
import mididings.setup as _setup
import mididings.event as _event


def _Panic(ev):
    # send all notes off (CC #123) to all output ports and on all channels
    for p in _engine.get_out_ports():
        for c in range(16):
            _engine.output_event(_event.CtrlEvent(p, c + _setup.get_config('data_offset'), 123, 0))


def Panic():
    return Call(_Panic) >> Discard()
