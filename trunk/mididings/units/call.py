# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import _mididings

from .base import _Unit

from .. import event as _event

import thread as _thread


class _CallBase(_mididings.Call, _Unit):
    def __init__(self, fun, async, cont):
        self.fun = fun
        _mididings.Call.__init__(self, self.do_call, async, cont)
    def do_call(self, ev):
        # add additional properties
        ev.__class__ = _event.MidiEvent
        return self.fun(ev)


class Call(_CallBase):
    def __init__(self, fun):
        _CallBase.__init__(self, fun, False, False)


class CallAsync(_CallBase):
    def __init__(self, fun):
        _CallBase.__init__(self, fun, True, True)


class CallThread(_CallBase):
    def __init__(self, fun):
        self.fun_thread = fun
        _CallBase.__init__(self, self.do_thread, True, True)
    def do_thread(self, ev):
        # need to make a copy of the event.
        # the underlying C++ object will become invalid when this function returns
        ev_copy = _event.MidiEvent(ev.type_, ev.port_, ev.channel_, ev.data1, ev.data2)
        _thread.start_new_thread(self.fun_thread, (ev_copy,))
