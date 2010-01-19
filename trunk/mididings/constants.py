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

from misc import NamedFlag as _NamedFlag
from misc import NamedBitMask as _NamedBitMask


NONE            = _NamedBitMask(0, 'NONE')

NOTEON          = _NamedBitMask(1 << 0, 'NOTEON')
NOTEOFF         = _NamedBitMask(1 << 1, 'NOTEOFF')
NOTE            = _NamedBitMask(NOTEON | NOTEOFF, 'NOTE')
CTRL            = _NamedBitMask(1 << 2, 'CTRL')
PITCHBEND       = _NamedBitMask(1 << 3, 'PITCHBEND')
AFTERTOUCH      = _NamedBitMask(1 << 4, 'AFTERTOUCH')
POLY_AFTERTOUCH = _NamedBitMask(1 << 5, 'POLY_AFTERTOUCH')
PROGRAM         = _NamedBitMask(1 << 6, 'PROGRAM')
# for backward compatibility
PROG = PROGRAM

SYSEX           = _NamedBitMask(1 << 7, 'SYSEX')

SYSCM_QFRAME    = _NamedBitMask(1 << 8, 'SYSCM_QFRAME')
SYSCM_SONGPOS   = _NamedBitMask(1 << 9, 'SYSCM_SONGPOS')
SYSCM_SONGSEL   = _NamedBitMask(1 << 10, 'SYSCM_SONGSEL')
SYSCM_TUNEREQ   = _NamedBitMask(1 << 11, 'SYSCM_TUNEREQ')
SYSCM           = _NamedBitMask(SYSCM_QFRAME | SYSCM_SONGPOS | SYSCM_SONGSEL | SYSCM_TUNEREQ, 'SYSCM')

SYSRT_CLOCK     = _NamedBitMask(1 << 12, 'SYSRT_CLOCK')
SYSRT_START     = _NamedBitMask(1 << 13, 'SYSRT_START')
SYSRT_CONTINUE  = _NamedBitMask(1 << 14, 'SYSRT_CONTINUE')
SYSRT_STOP      = _NamedBitMask(1 << 15, 'SYSRT_STOP')
SYSRT_SENSING   = _NamedBitMask(1 << 16, 'SYSRT_SENSING')
SYSRT_RESET     = _NamedBitMask(1 << 17, 'SYSRT_RESET')
SYSRT           = _NamedBitMask(SYSRT_CLOCK | SYSRT_START | SYSRT_CONTINUE | SYSRT_STOP | SYSRT_SENSING | SYSRT_RESET, 'SYSRT')

DUMMY           = _NamedBitMask(1 << 30, 'DUMMY')
ANY             = _NamedBitMask(~0, 'ANY')

_NUM_EVENT_TYPES = 18


EVENT_PORT      = _NamedFlag(-1, 'EVENT_PORT')
EVENT_CHANNEL   = _NamedFlag(-2, 'EVENT_CHANNEL')
# generic
EVENT_DATA1     = _NamedFlag(-3, 'EVENT_DATA1')
EVENT_DATA2     = _NamedFlag(-4, 'EVENT_DATA2')
# note
EVENT_NOTE      = _NamedFlag(-3, 'EVENT_NOTE')
EVENT_VELOCITY  = _NamedFlag(-4, 'EVENT_VELOCITY')
# controller
EVENT_PARAM     = _NamedFlag(-3, 'EVENT_PARAM')
EVENT_VALUE     = _NamedFlag(-4, 'EVENT_VALUE')
# program change
EVENT_PROGRAM   = _NamedFlag(-4, 'EVENT_PROGRAM')
