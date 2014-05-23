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

import mididings as _m


_BLACK = [1, 3, 6, 8, 10]
_BLACK_KEYS = [_n for _n in range(128) if _n%12 in _BLACK]
_WHITE_KEYS = [_n for _n in range(128) if _n%12 not in _BLACK]


def KeyColorFilter(color):
    """
    Filter notes by key color.

    :param color:
        the key color, either ``'black'`` or ``'white'``.
    """
    if color == 'black':
        return _m.KeyFilter(notes=_BLACK_KEYS)
    elif color == 'white':
        return _m.KeyFilter(notes=_WHITE_KEYS)
