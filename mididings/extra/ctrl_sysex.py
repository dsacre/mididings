# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2011  Sébastien Devaux
# Copyright (C) 2012-2014  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

from mididings import *
from mididings import event
from mididings import util


class _CtrlToSysEx(object):
    def __init__(self, sysex, index, checksum_start):
        self.sysex = util.sysex_data(sysex)
        self.index = index
        self.checksum_start = checksum_start

    def __call__(self, ev):
        sysex = self.sysex
        sysex[self.index] = ev.value

        if self.checksum_start is not None:
            checksum = sum(self.sysex[self.checksum_start:-2])
            sysex[-2] = (128 - checksum) % 128

        return event.SysExEvent(ev.port, sysex)


def CtrlToSysEx(ctrl, sysex, index, checksum_start=None):
    """
    Convert control change to system exclusive event using a sysex pattern.

    :param ctrl: controller number to be replaced.
    :param sysex: sysex pattern.
    :param index: index of sysex pattern byte to be replaced by the
        controller value.
    :param checksum_start: index of first sysex byte to be incorporated into
        Roland checksum computation. The checksum will replace the
        next-to-last byte of the sysex pattern.
        If this parameter is ``None``, no checksum is computed.
    """
    return CtrlFilter(ctrl) % Process(
                _CtrlToSysEx(sysex, index, checksum_start))
