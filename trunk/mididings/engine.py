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
import scene
import event
import util
import misc

import time
import weakref
import threading
import gc


class Engine(_mididings.Engine):
    def __init__(self, scenes, control, pre, post):
        self.in_ports = self.make_portnames(main.config['in_ports'], 'in_')
        self.out_ports = self.make_portnames(main.config['out_ports'], 'out_')

        _mididings.Engine.__init__(
            self, main.config['backend'],
            main.config['client_name'],
            misc.make_string_vector(self.in_ports),
            misc.make_string_vector(self.out_ports),
            main.config['verbose']
        )

        self.scene_names = {}

        for i, s in scenes.items():
            if isinstance(s, scene.Scene):
                init = [s.init_patch] if s.init_patch else []
                proc = s.patch
                if s.name:
                    self.scene_names[i] = s.name
            elif isinstance(s, tuple):
                init = [s[0]]
                proc = s[1]
            else:
                init = []
                proc = s

            init += patch.get_init_actions(proc)

            self.add_scene(util.scene_number(i), patch.Patch(proc), patch.Patch(init))

        ctrl = patch.Patch(control) if control else None
        pre_patch = patch.Patch(pre) if pre else None
        post_patch = patch.Patch(post) if post else None
        self.set_processing(ctrl, pre_patch, post_patch)

        self._quit = threading.Event()

        # delay before actually sending any midi data (give qjackctl patchbay time to react...)
        delay = main.config['start_delay']
        if delay != None:
            if delay > 0:
                time.sleep(delay)
            else:
                raw_input("press enter to start midi processing...")

        main.TheEngine = weakref.proxy(self)

        gc.collect()
        gc.disable()

    def run(self):
        self.call_hooks('on_start')

        if main.config['initial_scene'] != None:
            initial_scene = util.scene_number(main.config['initial_scene'])
        else:
            initial_scene = 0
        self.start(initial_scene)

        try:
            # wait() with no timeout also blocks KeyboardInterrupt, but a very long timeout doesn't. weird...
            while not self._quit.isSet():
                self._quit.wait(86400)
        finally:
            self.call_hooks('on_exit')

    def process_file(self):
        self.start(0)

    def make_portnames(self, ports, prefix):
        if misc.issequence(ports):
            return ports
        else:
            return [prefix + str(n + main.config['data_offset']) for n in range(ports)]

    def scene_switch_handler(self, n, found):
        n += main.config['data_offset']
        name = self.scene_names[n] if n in self.scene_names else None

        if main.config['verbose']:
            if found:
                if name:
                    print "switching to scene %d: %s" % (n, name)
                else:
                    print "switching to scene %d" % n
            else:
                print "no such scene: %d" % n

        if found:
            self.call_hooks('on_switch_scene', n)

    def quit(self):
        self._quit.set()

    def call_hooks(self, name, *args):
        for hook in main._hooks:
            if hasattr(hook, name):
                f = getattr(hook, name)
                f(*args)
