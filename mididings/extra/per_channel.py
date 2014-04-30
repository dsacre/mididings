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


class PerChannel(object):
    """
    Utility class, usable with Process() and Call(), that delegates events
    to different instances of the same class, using one instance per
    channel/port combination.
    New instances are created as needed, using the given factory function,
    when the first event with a new channel/port arrives.
    """
    def __init__(self, factory):
        self.channel_proc = {}
        self.factory = factory

    def __call__(self, ev):
        k = (ev.port, ev.channel)
        if k not in self.channel_proc:
            self.channel_proc[k] = self.factory()
        return self.channel_proc[k](ev)
