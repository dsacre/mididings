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
import util
import units


OCTAVE_OFFSET   = 2
PORT_OFFSET     = 1
CHANNEL_OFFSET  = 1
PROGRAM_OFFSET  = 1


class Patch(_mididings.Patch):
    def __init__(self, p):
        _mididings.Patch.__init__(self)

        i = Patch.Module(Patch.Input())
        o = Patch.Module(Patch.Output())

        r = self.build(p)

        # attach all inputs
        for c in r[0]:
            i.attach(c)
        # attach all outputs
        for c in r[1]:
            c.attach(o)

        self.set_start(i)

    # recursively connects all units in p
    # returns the lists of inputs and outputs of p
    def build(self, p):
        if isinstance(p, units._Chain):
            # build both items
            a = self.build(p.items[0])
            b = self.build(p.items[1])
            # connect all of a's outputs to all of b's inputs
            for x in a[1]:
                for y in b[0]:
                    x.attach(y)
            # return a's inputs and b's outputs
            return a[0], b[1]
        elif isinstance(p, list):
            # build all items, return all inputs and outputs
            inp, outp = [], []
            for m in p:
                r = self.build(m)
                inp += r[0]
                outp += r[1]
            return inp, outp
        elif isinstance(p, units._Unit):
            # single unit is both input and output
            m = Patch.Module(p)
            return [m], [m]
        else:
            # whoops...
            raise TypeError()


class Setup(_mididings.Setup):
    def __init__(self, patches, control,
                 preprocess, postprocess,
                 backend, client_name,
                 in_ports, out_ports):
        in_portnames = _mididings.string_vector()
        out_portnames = _mididings.string_vector()

        if not util.is_sequence(in_ports):
            in_ports = [ 'in_' + str(n + PORT_OFFSET) for n in range(in_ports) ]
        # fill vector with input port names
        for i in in_ports:
            in_portnames.push_back(i)

        if not util.is_sequence(out_ports):
            out_ports = [ 'out_' + str(n + PORT_OFFSET) for n in range(out_ports) ]
        # fill vector with output port names
        for i in out_ports:
            out_portnames.push_back(i)

        _mididings.Setup.__init__(self, backend, client_name, in_portnames, out_portnames)

        for i, p in patches.items():
            if isinstance(p, tuple):
                init_patch, patch = Patch(p[0]), Patch(p[1])
            else:
                init_patch, patch = None, Patch(p)
            self.add_patch(i - PROGRAM_OFFSET, patch, init_patch)

        ctrl = Patch(control) if control else None
        pre = Patch(preprocess) if preprocess else None
        post = Patch(postprocess) if postprocess else None
        self.set_processing(ctrl, pre, post)

        self.switch_patch(0)


def config(octave_offset=None,
           port_offset=None,
           channel_offset=None,
           program_offset=None):

    global OCTAVE_OFFSET
    global PORT_OFFSET
    global CHANNEL_OFFSET
    global PROGRAM_OFFSET

    if octave_offset != None:
        OCTAVE_OFFSET = octave_offset
    if port_offset != None:
        PORT_OFFSET = port_offset
    if channel_offset != None:
        CHANNEL_OFFSET = channel_offset
    if program_offset != None:
        PROGRAM_OFFSET = program_offset


def run(patches,
        control=None,
        preprocess=None,
        postprocess=None,
        backend='alsa',
        client_name='mididings',
        in_ports=1,
        out_ports=1):

    s = Setup(patches, control,
              preprocess, postprocess,
              backend, client_name,
              in_ports, out_ports)
    try:
        s.run()
    except KeyboardInterrupt:
        return


def test_run(patch, event):
    s = Setup({ PROGRAM_OFFSET: patch }, None, None, None,
              'dummy', 'mididings_test', 1, 1)
    r = s.process(event)
    return r[:]
