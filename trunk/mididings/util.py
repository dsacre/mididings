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
import misc as _misc


NOTE_NUMBERS = {
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

NOTE_NAMES = {
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

CONTROLLER_NAMES = {
     0: 'Bank select (MSB)',
     1: 'Mod wheel',
     7: 'Volume',
    10: 'Pan',
    11: 'Expression',
    32: 'Bank select (LSB)',
    64: 'Sustain',
    65: 'Portamento',
    66: 'Sostenuto',
    67: 'Soft pedal',
    68: 'Legato pedal',
   121: 'Reset all controllers',
   123: 'All notes off',
}


# convert note name to MIDI note number
def note_number(note):
    try:
        # already a number?
        return int(note)
    except ValueError:
        note = note.lower()
        # find first digit
        for i in range(len(note)):
            if note[i].isdigit() or note[i] == '-':
                break
        return NOTE_NUMBERS[note[:i]] + (int(note[i:]) + _main._config['octave_offset']) * 12


# convert note range to tuple of MIDI note numbers
def note_range(notes):
    try:
        # single note?
        return (note_number(notes),) * 2
    except:
        if not isinstance(notes, tuple):
            notes = notes.split(':', 1)
        return note_number(notes[0]), note_number(notes[1])


# get note name from MIDI note number
def note_name(note):
    return NOTE_NAMES[note % 12] + str((note / 12) - _main._config['octave_offset'])


def tonic_note_number(key):
    return NOTE_NUMBERS[key]


# get controller description
def controller_name(ctrl):
    if ctrl in CONTROLLER_NAMES:
        return CONTROLLER_NAMES[ctrl]
    else:
        return None


# get port number from port name
def port_number(port):
    try:
        # already a number?
        return int(port) - _main._config['data_offset']
    except ValueError:
        in_ports = _main._config['in_ports']
        out_ports = _main._config['out_ports']
        is_in = (_misc.issequence(in_ports) and port in in_ports)
        is_out = (_misc.issequence(out_ports) and port in out_ports)

        if is_in and is_out and in_ports.index(port) != out_ports.index(port):
            raise ValueError("port name '%s' is ambiguous" % port)
        elif is_in:
            return in_ports.index(port)
        elif is_out:
            return out_ports.index(port)
        else:
            raise ValueError('invalid port name: %s' % port)


def channel_number(channel):
    return channel - _main._config['data_offset']


def program_number(program):
    return program - _main._config['data_offset']
