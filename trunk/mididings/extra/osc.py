# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2009  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

from mididings import CallAsync

import liblo as _liblo


class _SendOSC(object):
    def __init__(self, target, path, args):
        self.target = target
        self.path = path
        self.args = args

    def __call__(self, ev):
        args = (x(ev) if callable(x) else x for x in self.args)
        _liblo.send(self.target, self.path, *args)


def SendOSC(target, path, *args):
    return CallAsync(_SendOSC(target, path, args))
