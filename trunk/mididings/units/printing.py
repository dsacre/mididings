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

from .call import _CallBase

from .. import main as _main
from .. import event as _event


class Print(_CallBase):
    PORTNAMES_NONE = 0
    PORTNAMES_IN   = 1
    PORTNAMES_OUT  = 2

    max_name_length = -1
    max_portname_length = -1
    portnames_used = False

    def __init__(self, name=None, types=_event.ANY, portnames=PORTNAMES_NONE):
        self.name = name
        self.types = types
        self.portnames = portnames

        # to be calculated later
        self.ports = None

        if portnames != Print.PORTNAMES_NONE:
            Print.portnames_used = True

        # find maximum name length
        if name:
            Print.max_name_length = max(Print.max_name_length, len(name))

        _CallBase.__init__(self, self.do_print, True, True)

    def do_print(self, ev):
        # get list of port names to be used
        # (delayed 'til first use, because _main.TheEngine doesn't yet exist during __init__)
        if self.ports == None:
            if self.portnames == Print.PORTNAMES_IN:
                self.ports = _main.TheEngine.in_ports
            elif self.portnames == Print.PORTNAMES_OUT:
                self.ports = _main.TheEngine.out_ports
            else:
                self.ports = []

        # find maximum port name length (delayed for the same reason as above)
        if Print.portnames_used and Print.max_portname_length == -1:
            all_ports = _main.TheEngine.in_ports + _main.TheEngine.out_ports
            Print.max_portname_length = max((len(p) for p in all_ports))

        if ev.type_ & self.types:
            if self.name:
                print '%-*s' % (Print.max_name_length + 1, self.name + ':'),
            elif Print.max_name_length != -1:
                # no name, but names used elsewhere, so indent appropriately
                print ' ' * (Print.max_name_length + 1),

            print ev.to_string(self.ports, Print.max_portname_length)


class PrintString(_CallBase):
    def __init__(self, string):
        self.string = string
        _CallBase.__init__(self, self.do_print, True, True)
    def do_print(self, ev):
        print self.string
