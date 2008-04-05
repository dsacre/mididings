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

from mididings import *


class InitAction(units._Unit):
    def __init__(self, init, proc):
        self.init_patch = init
        self.proc_patch = proc


class Output(InitAction):
    def __init__(self, port, channel, program=-1):
        InitAction.__init__(self,
            ProgChange(port, channel, program) if program != -1 else None,
            Port(port) >> Channel(channel),
        )


def unfold_patches(patches):
    def traverse(p, init):
        if isinstance(p, units._Chain):
            return traverse(p.items[0], init) >> traverse(p.items[1], init)
        elif isinstance(p, list):
            return Fork([ traverse(i, init) for i in p ])
        elif isinstance(p, dict):
            return Split(dict(((n, traverse(i, init)) for n, i in p.items())))
        elif isinstance(p, InitAction):
            if p.init_patch:
                init.append(p.init_patch)
            return p.proc_patch
        elif isinstance(p, units._Unit):
            return p

    def conv_patch(p):
        if isinstance(p, tuple):
            init_patch = p[0]
            patch = traverse(p[1], init_patch)
        else:
            init_patch = []
            patch = traverse(p, init_patch)

        return init_patch, patch

    return dict((n, conv_patch(p)) for n, p in patches.items())
