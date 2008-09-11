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
from .. import util as _util


class GenerateEvent(_mididings.GenerateEvent, _Unit):
    def __init__(self, type_, port, channel, data1, data2):
        _mididings.GenerateEvent.__init__(
            self, type_,
            _util.port_number(port) if isinstance(port, str) or port >= 0 else port,
            _util.channel_number(channel) if channel >= 0 else channel,
            data1, data2
        )


def CtrlChange(*args):
    if len(args) == 2:
        # CrtlChange(ctrl, value)
        ctrl, value = args
        return GenerateEvent(
                _event.CTRL,
                _event.EVENT_PORT,
                _event.EVENT_CHANNEL,
                _util.ctrl_number(ctrl) if ctrl >= 0 else ctrl,
                _util.ctrl_value(value) if value >= 0 else value
            )
    elif len(args) == 4:
        # CrtlChange(port, channel, ctrl, value)
        port, channel, ctrl, value = args
        return GenerateEvent(
                _event.CTRL,
                port,
                channel,
                _util.ctrl_number(ctrl) if ctrl >= 0 else ctrl,
                _util.ctrl_value(value) if value >= 0 else value
            )
    else:
        raise TypeError("CtrlChange() must be called with either two or four arguments")


def ProgChange(*args):
    if len(args) == 1:
        # ProgChange(program)
        return GenerateEvent(
                _event.PROGRAM,
                _event.EVENT_PORT,
                _event.EVENT_CHANNEL,
                0,
                _util.program_number(args[0])
            )
    elif len(args) == 3:
        # ProgChange(port, channel, program)
        port, channel, program = args
        return GenerateEvent(
                _event.PROGRAM,
                port,
                channel,
                0,
                _util.program_number(program)
            )
    else:
        raise TypeError("ProgChange() must be called with either one or three arguments")
