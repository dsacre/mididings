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


class PerChannel(object):
    def __init__(self, factory):
        self.per_channel = {}
        self.factory = factory

    def __call__(self, ev):
        k = (ev.port, ev.channel)
        if k not in self.per_channel:
            self.per_channel[k] = self.factory()
        return self.per_channel[k](ev)
