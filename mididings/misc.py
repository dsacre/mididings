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

import main as _main
import _mididings


NOTE_NAMES = {
    'c':   0,
    'c#':  1, 'db':  1,
    'd':   2,
    'd#':  3, 'eb':  3,
    'e':   4,
    'f':   5,
    'f#':  6, 'gb':  6,
    'g':   7,
    'g#':  8, 'ab':  8,
    'a':   9,
    'a#': 10, 'bb': 10,
    'b':  11,
}

NOTE_NUMBERS = {
     0: 'c',
     1: 'c#',
     2: 'd',
     3: 'd#',
     4: 'e',
     5: 'f',
     6: 'f#',
     7: 'g',
     8: 'g#',
     9: 'a',
    10: 'a#',
    11: 'b',
}


def notename2number(name):
    name = name.lower()
    for n in NOTE_NAMES:
        octave = name[len(n):]
        if name.startswith(n) and (octave.isdigit() or (octave[0] == '-' and octave[1:].isdigit())):
            num = NOTE_NAMES[n] + (int(octave) + _main._config['octave_offset']) * 12
            if num < 0 or num > 127:
                raise ValueError()
            return num
    raise ValueError()


def note2number(note):
    try:
        return int(note)
    except ValueError:
        return notename2number(note)


def noterange2numbers(noterange):
    try:
        # single note?
        return (note2number(noterange),) * 2
    except:
        if not isinstance(noterange, tuple):
            noterange = noterange.split(':', 1)
        return note2number(noterange[0]), note2number(noterange[1])


def notenumber2name(n):
    return NOTE_NUMBERS[n % 12] + str(n / 12 - _main._config['octave_offset'])



def flatten(seq):
    r = []
    for i in seq:
        if (isinstance(i, (tuple, list))):
            r.extend(flatten(i))
        else:
            r.append(i)
    return r


def issequence(seq):
    try:
        iter(seq)
        return True
    except:
        return False


def port_number(port):
    try:
        return int(port) - _main._config['data_offset']
    except ValueError:
        try:
            return _main._config['out_ports'].index(port)
        except ValueError:
            try:
                return _main._config['in_ports'].index(port)
            except:
                raise ValueError('invalid port name: %s' % port)

def channel_number(channel):
    return channel - _main._config['data_offset']

def program_number(program):
    return program - _main._config['data_offset']


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
