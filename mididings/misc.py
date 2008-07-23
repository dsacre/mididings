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


def flatten(seq):
    r = []
    for i in seq:
        if isinstance(i, (tuple, list)):
            r.extend(flatten(i))
        else:
            r.append(i)
    return r


def issequence(seq, accept_string=False):
    if not accept_string and isinstance(seq, str):
        return False
    try:
        iter(seq)
        return True
    except:
        return False


def make_string_vector(seq):
    vec = _mididings.string_vector()
    for i in seq:
        vec.push_back(i)
    return vec


def make_int_vector(seq):
    vec = _mididings.int_vector()
    for i in seq:
        vec.push_back(i)
    return vec
