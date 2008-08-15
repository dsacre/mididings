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
import main
import patch
import event
import misc

import time
import weakref


class Engine(_mididings.Engine):
    def __init__(self, patches, control, pre, post):
        self.in_ports = self.make_portnames(main._config['in_ports'], 'in_')
        self.out_ports = self.make_portnames(main._config['out_ports'], 'out_')

        _mididings.Engine.__init__(
            self, main._config['backend'],
            main._config['client_name'],
            misc.make_string_vector(self.in_ports),
            misc.make_string_vector(self.out_ports),
            main._config['verbose']
        )

        for i, p in patches.items():
            if isinstance(p, tuple):
                init_patch, process_patch = patch.Patch(p[0]), patch.Patch(p[1])
            else:
                init_patch, process_patch = None, patch.Patch(p)
            self.add_patch(i - main._config['data_offset'], process_patch, init_patch)

        ctrl = patch.Patch(control) if control else None
        pre_patch = patch.Patch(pre) if pre else None
        post_patch = patch.Patch(post) if post else None
        self.set_processing(ctrl, pre_patch, post_patch)

        # delay before actually sending any midi data (give qjackctl patchbay time to react...)
        if main._config['start_delay'] != None:
            if main._config['start_delay'] > 0:
                time.sleep(main._config['start_delay'])
            else:
                raw_input("press enter to start midi processing...")

#        self.switch_patch(0, event._DummyEvent())
#        self.switch_patch(0)

        main.TheEngine = weakref.proxy(self)

    def make_portnames(self, ports, prefix):
        return ports if misc.issequence(ports) else \
               [ prefix + str(n + main._config['data_offset']) for n in range(ports) ]

    def print_switch_patch(self, n, found):
        if main._config['verbose']:
            n += main._config['data_offset']
            if found: print "switching to patch: %d" % n
            else: print "no such patch: %d" % n
