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
import mididings.patch as _patch
import mididings.scene as _scene
import mididings.event as _event
import mididings.util as _util
import mididings.misc as _misc
import mididings.setup as _setup
from mididings.setup import get_config as _get_config
from mididings.setup import get_hooks as _get_hooks

import time as _time
import weakref as _weakref
import threading as _threading
import gc as _gc


_TheEngine = None


class Engine(_mididings.Engine):
    def __init__(self, scenes, control, pre, post):
        self.in_ports = self._make_portnames(_get_config('in_ports'), 'in_')
        self.out_ports = self._make_portnames(_get_config('out_ports'), 'out_')

        _mididings.Engine.__init__(
            self, _get_config('backend'),
            _get_config('client_name'),
            _misc.make_string_vector(self.in_ports),
            _misc.make_string_vector(self.out_ports),
            _get_config('verbose')
        )

        self._scene_names = {}

        for i, s in scenes.items():
            if isinstance(s, _scene.Scene):
                init = [s.init_patch] if s.init_patch else []
                proc = s.patch
                self._scene_names[i] = s.name if s.name else ''
            elif isinstance(s, tuple):
                init = [s[0]]
                proc = s[1]
                self._scene_names[i] = ''
            else:
                init = []
                proc = s
                self._scene_names[i] = ''

            init += _patch.get_init_actions(proc)

            self.add_scene(_util.scene_number(i), _patch.Patch(proc), _patch.Patch(init))

        control_patch = _patch.Patch(control) if control else None
        pre_patch = _patch.Patch(pre) if pre else None
        post_patch = _patch.Patch(post) if post else None
        self.set_processing(control_patch, pre_patch, post_patch)

        self._quit = _threading.Event()

        # delay before actually sending any midi data (give qjackctl patchbay time to react...)
        delay = _get_config('start_delay')
        if delay != None:
            if delay > 0:
                _time.sleep(delay)
            else:
                raw_input("press enter to start midi processing...")

        global _TheEngine
        _TheEngine = _weakref.proxy(self)

        _gc.collect()
        _gc.disable()

    def run(self):
        self._call_hooks('on_start')

        if _get_config('initial_scene') != None:
            initial_scene = _util.scene_number(_get_config('initial_scene'))
        else:
            initial_scene = -1
        self.start(initial_scene)

        try:
            # wait() with no timeout also blocks KeyboardInterrupt, but a very long timeout doesn't. weird...
            while not self._quit.isSet():
                self._quit.wait(86400)
        except KeyboardInterrupt:
            pass
        finally:
            self._call_hooks('on_exit')
            global _TheEngine
            _TheEngine = None

    def process_file(self):
        self.start(0)

    def _make_portnames(self, ports, prefix):
        if _misc.issequence(ports):
            return ports
        else:
            return [prefix + str(n + _get_config('data_offset')) for n in range(ports)]

    def _scene_switch_handler(self, n):
        n += _get_config('data_offset')
        found = n in self._scene_names
        name = self._scene_names[n] if found else None

        if _get_config('verbose'):
            if found:
                if name:
                    print "switching to scene %d: %s" % (n, name)
                else:
                    print "switching to scene %d" % n
            else:
                print "no such scene: %d" % n

        if found:
            self._call_hooks('on_switch_scene', n)

    def _call_hooks(self, name, *args):
        for hook in _get_hooks():
            if hasattr(hook, name):
                f = getattr(hook, name)
                f(*args)

    def switch_scene(self, n):
        _mididings.Engine.switch_scene(self, _util.scene_number(n))

    def current_scene(self):
        return _mididings.Engine.current_scene(self) + _get_config('data_offset')

    def get_scenes(self):
        return self._scene_names

    def quit(self):
        self._quit.set()



def run(*args, **kwargs):
    def run_patch(patch):
        e = Engine({ 0: patch }, None, None, None)
        e.run()
    def run_scenes(scenes, control=None, pre=None, post=None):
        e = Engine(scenes, control, pre, post)
        e.run()

    _misc.call_overload('run', args, kwargs, [
        run_patch,
        run_scenes
    ])

_misc.deprecated('run')
def run_scenes(scenes, control=None, pre=None, post=None):
    run(scenes, control, pre, post)

_misc.deprecated('run')
def run_patches(patches, control=None, pre=None, post=None):
    run(patches, control, pre, post)


def process_file(infile, outfile, patch):
    _setup.config(False,
        backend = 'smf',
        in_ports = [infile],
        out_ports = [outfile],
    )
    e = Engine({ 0: patch }, None, None, None)
    e.process_file()


def switch_scene(n):
    _TheEngine.switch_scene(n)

def current_scene():
    return _TheEngine.current_scene()

def get_scenes():
    return _TheEngine.get_scenes()


def quit():
    _TheEngine.quit()
