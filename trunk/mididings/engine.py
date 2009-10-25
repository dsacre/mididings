# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2009  Dominic Sacré  <dominic.sacre@gmx.de>
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
import util
import misc

import time
import weakref
import gc


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
            if not isinstance(p, tuple):
                init = []
                proc = p
            else:
                init = [p[0]]
                proc = p[1]

            init += patch.get_init_actions(proc)

            self.add_patch(i - main._config['data_offset'], patch.Patch(proc), patch.Patch(init))

        ctrl = patch.Patch(control) if control else None
        pre_patch = patch.Patch(pre) if pre else None
        post_patch = patch.Patch(post) if post else None
        self.set_processing(ctrl, pre_patch, post_patch)

        self.patch_switch_callback = None
        self.quit = False

        # delay before actually sending any midi data (give qjackctl patchbay time to react...)
        if main._config['start_delay'] != None:
            if main._config['start_delay'] > 0:
                time.sleep(main._config['start_delay'])
            else:
                raw_input("press enter to start midi processing...")

        main.TheEngine = weakref.proxy(self)

        gc.collect()
        gc.disable()

    def run(self, first_patch, patch_switch_callback):
        # hmmm...
        self.patch_switch_callback = patch_switch_callback
        self.start(util.patch_number(first_patch))

        if main._config['osc_port']:
            import liblo
            s = liblo.Server(main._config['osc_port'])
            s.add_method('/mididings/switch_scene', 'i', self.osc_switch_scene_cb)
            s.add_method('/mididings/quit', '', self.osc_quit_cb)
            while not self.quit:
                s.recv(1000)
        else:
            while True:
                time.sleep(3600)

    def process_file(self):
        self.start(0)

    def make_portnames(self, ports, prefix):
        return ports if misc.issequence(ports) else \
               [ prefix + str(n + main._config['data_offset']) for n in range(ports) ]

    def patch_switch_handler(self, n, found):
        n += main._config['data_offset']

        if main._config['verbose']:
            if found: print "switching to patch: %d" % n
            else: print "no such patch: %d" % n

        if found:
            if self.patch_switch_callback:
                self.patch_switch_callback(n)

            if main._config['osc_notify_port']:
                import liblo
                liblo.send(main._config['osc_notify_port'], '/mididings/scene', n)

    def osc_switch_scene_cb(self, path, args):
        self.switch_patch(args[0] - main._config['data_offset'])

    def osc_quit_cb(self, path, args):
        self.quit = True
