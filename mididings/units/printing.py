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

from mididings.units.call import _CallBase

import mididings.overload as _overload
import mididings.unitrepr as _unitrepr
import mididings.constants as _constants
import mididings.misc as _misc

import sys as _sys
import collections as _collections


class _Print(_CallBase):
    max_name_length = -1
    max_portname_length = -1
    portnames_used = False

    def __init__(self, name, portnames):
        if portnames is not None:
            _Print.portnames_used = True

        # find maximum name length
        if name:
            _Print.max_name_length = max(_Print.max_name_length, len(name))

        # using a separare object to do the actual printing avoids keeping
        # references back to this unit, thus preventing a cycle
        printer = _Printer(name, portnames)

        _CallBase.__init__(self, printer, True, True)


class _Printer(object):
    def __init__(self, name, portnames):
        self.name = name
        self.portnames = portnames
        # to be calculated later
        self.ports = None

    def __call__(self, ev):
        # lazy import to avoid problems with circular imports
        from mididings import engine

        # get list of port names to be used (delayed 'til first use,
        # because the engine doesn't yet exist during __init__)
        if self.ports is None:
            if self.portnames == 'in':
                self.ports = engine.in_ports()
            elif self.portnames == 'out':
                self.ports = engine.out_ports()
            else:
                self.ports = []

        # find maximum port name length (delayed for the same reason as above)
        if _Print.portnames_used and _Print.max_portname_length == -1:
            all_ports = engine.in_ports() + engine.out_ports()
            _Print.max_portname_length = max(len(p) for p in all_ports)

        if self.name:
            namestr = '%-*s ' % (_Print.max_name_length + 1, self.name + ':')
        elif _Print.max_name_length != -1:
            # no name, but names used elsewhere, so indent appropriately
            namestr = ' ' * (_Print.max_name_length + 2)
        else:
            namestr = ''

        if ev.type == _constants.SYSEX:
            eventmax = _misc.get_terminal_size()[1] - len(namestr)
        else:
            eventmax = 0
        eventstr = ev.to_string(self.ports, _Print.max_portname_length,
                                eventmax)

        print('%s%s' % (namestr, eventstr))


class _PrintString(_CallBase):
    def __init__(self, string):
        self.string = string
        _CallBase.__init__(self, self.do_print, True, True)
    def do_print(self, ev):
        string = (self.string(ev) if hasattr(self.string, '__call__')
                                else self.string)
        print(string)


@_overload.mark(
    """
    Print(name=None, portnames=None)
    Print(string=...)

    Print event data or strings to the console.

    :param name:
        an optional identifier that will be printed before any event data,
        in order to distinguish between multiple :func:`Print()` units
        in the same patch.

    :param portnames:
        determines which port names will be printed:

        - ``'in'``: the input port name corresponding to the event's
          port number.
        - ``'out'``: the output port name corresponding to the event's
          port number.
        - ``None``: port number only.

    :param string:
        print a fixed string.
        Alternatively *string* may also be a Python function that accepts
        a :class:`~.MidiEvent` argument and returns the string to be printed.
    """
)
@_unitrepr.accept((str, type(None)), ('in', 'out', None))
def Print(name=None, portnames=None):
    return _Print(name, portnames)

@_overload.mark
@_unitrepr.accept((str, _collections.abc.Callable))
def Print(string):
    return _PrintString(string)
