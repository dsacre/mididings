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

from __future__ import absolute_import as _absolute_import

from mididings import Call as _Call

import dbus as _dbus


class _SendDBUS(object):
    def __init__(self, service, path, interface, method, args):
        self.bus = _dbus.SessionBus()
        self.service = service
        self.path = path
        self.interface = interface
        self.method = method
        self.args = args

    def __call__(self, ev):
        obj = self.bus.get_object(self.service, self.path)
        func = obj.get_dbus_method(self.method, self.interface)
        args = ((x(ev) if hasattr(x, '__call__') else x) for x in self.args)
        func(*args)


def SendDBUS(service, path, interface, method, *args):
    """
    Send a DBUS message.
    Instead of a specific value, each data argument may also be a Python
    function that takes a single :class:`~.MidiEvent` parameter, and
    returns the value to be sent.
    """
    return _Call(_SendDBUS(service, path, interface, method, args))
