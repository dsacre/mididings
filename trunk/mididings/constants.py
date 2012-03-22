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

from mididings.misc import NamedFlag as _NamedFlag
from mididings.misc import NamedBitMask as _NamedBitMask


class _EventType(_NamedBitMask):
    pass

class _EventAttribute(_NamedFlag):
    pass


NONE            = _EventType(0, 'NONE')

NOTEON          = _EventType(1 << 0, 'NOTEON')
NOTEOFF         = _EventType(1 << 1, 'NOTEOFF')
NOTE            = _EventType(NOTEON | NOTEOFF, 'NOTE')
CTRL            = _EventType(1 << 2, 'CTRL')
PITCHBEND       = _EventType(1 << 3, 'PITCHBEND')
AFTERTOUCH      = _EventType(1 << 4, 'AFTERTOUCH')
POLY_AFTERTOUCH = _EventType(1 << 5, 'POLY_AFTERTOUCH')
PROGRAM         = _EventType(1 << 6, 'PROGRAM')

SYSEX           = _EventType(1 << 7, 'SYSEX')

SYSCM_QFRAME    = _EventType(1 << 8, 'SYSCM_QFRAME')
SYSCM_SONGPOS   = _EventType(1 << 9, 'SYSCM_SONGPOS')
SYSCM_SONGSEL   = _EventType(1 << 10, 'SYSCM_SONGSEL')
SYSCM_TUNEREQ   = _EventType(1 << 11, 'SYSCM_TUNEREQ')
SYSCM           = _EventType(SYSCM_QFRAME | SYSCM_SONGPOS | SYSCM_SONGSEL | SYSCM_TUNEREQ, 'SYSCM')

SYSRT_CLOCK     = _EventType(1 << 12, 'SYSRT_CLOCK')
SYSRT_START     = _EventType(1 << 13, 'SYSRT_START')
SYSRT_CONTINUE  = _EventType(1 << 14, 'SYSRT_CONTINUE')
SYSRT_STOP      = _EventType(1 << 15, 'SYSRT_STOP')
SYSRT_SENSING   = _EventType(1 << 16, 'SYSRT_SENSING')
SYSRT_RESET     = _EventType(1 << 17, 'SYSRT_RESET')
SYSRT           = _EventType(SYSRT_CLOCK | SYSRT_START | SYSRT_CONTINUE | SYSRT_STOP | SYSRT_SENSING | SYSRT_RESET, 'SYSRT')

DUMMY           = _EventType(1 << 30, 'DUMMY')
ANY             = _EventType(~0, 'ANY')

_NUM_EVENT_TYPES = 18

_EVENT_TYPE_NAMES = {
    NOTEON:         'NOTEON',
    NOTEOFF:        'NOTEOFF',
    CTRL:           'CTRL',
    PITCHBEND:      'PITCHBEND',
    AFTERTOUCH:     'AFTERTOUCH',
    POLY_AFTERTOUCH:'POLY_AFTERTOUCH',
    PROGRAM:        'PROGRAM',
    SYSEX:          'SYSEX',
    SYSCM_QFRAME:   'SYSCM_QFRAME',
    SYSCM_SONGPOS:  'SYSCM_SONGPOS',
    SYSCM_SONGSEL:  'SYSCM_SONGSEL',
    SYSCM_TUNEREQ:  'SYSCM_TUNEREQ',
    SYSRT_CLOCK:    'SYSRT_CLOCK',
    SYSRT_START:    'SYSRT_START',
    SYSRT_CONTINUE: 'SYSRT_CONTINUE',
    SYSRT_STOP:     'SYSRT_STOP',
    SYSRT_SENSING:  'SYSRT_SENSING',
    SYSRT_RESET:    'SYSRT_RESET',
    DUMMY:          'DUMMY',
}


EVENT_PORT      = _EventAttribute(-1, 'EVENT_PORT')
EVENT_CHANNEL   = _EventAttribute(-2, 'EVENT_CHANNEL')
# generic
EVENT_DATA1     = _EventAttribute(-3, 'EVENT_DATA1')
EVENT_DATA2     = _EventAttribute(-4, 'EVENT_DATA2')
# note
EVENT_NOTE      = _EventAttribute(-3, 'EVENT_NOTE')
EVENT_VELOCITY  = _EventAttribute(-4, 'EVENT_VELOCITY')
# controller
EVENT_CTRL      = _EventAttribute(-3, 'EVENT_CTRL')
# for backward compatibility
EVENT_PARAM     = _EventAttribute(-3, 'EVENT_CTRL')
EVENT_PARAM._deprecated = True
EVENT_VALUE     = _EventAttribute(-4, 'EVENT_VALUE')
# program change
EVENT_PROGRAM   = _EventAttribute(-4, 'EVENT_PROGRAM')
