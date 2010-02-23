# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2010  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

from mididings import Call
import mididings.engine as _engine
import mididings.util as _util
import mididings.setup as _setup

import mididings.extra.panic as _panic

import liblo as _liblo


class OSCInterface(object):
    def __init__(self, port, notify_ports=[]):
        self.port = port
        self.notify_ports = notify_ports

    def on_start(self):
        if self.port != None:
            self.server = _liblo.ServerThread(self.port)
            self.server.register_methods(self)
            self.server.start()

        self.send_config()

    def on_exit(self):
        if self.port != None:
            self.server.stop()
            del self.server

    def on_switch_scene(self, scene, subscene):
        for p in self.notify_ports:
            _liblo.send(p, '/mididings/current_scene', scene, subscene)

    def send_config(self):
        for p in self.notify_ports:
            # send data offset
            _liblo.send(p, '/mididings/data_offset', _setup.get_config('data_offset'))

            # send list of scenes
            _liblo.send(p, '/mididings/begin_scenes')
            s = _engine.get_scenes()
            for n in sorted(s.keys()):
                _liblo.send(p, '/mididings/add_scene', n, s[n][0], *s[n][1])
            _liblo.send(p, '/mididings/end_scenes')

    @_liblo.make_method('/mididings/query', '')
    def query_cb(self, path, args):
        self.send_config()
        for p in self.notify_ports:
            _liblo.send(p, '/mididings/current_scene', _engine.current_scene(), _engine.current_subscene())

    @_liblo.make_method('/mididings/switch_scene', 'i')
    @_liblo.make_method('/mididings/switch_scene', 'ii')
    def switch_scene_cb(self, path, args):
        _engine.switch_scene(*args)

    @_liblo.make_method('/mididings/switch_subscene', 'i')
    def switch_subscene_cb(self, path, args):
        _engine.switch_subscene(*args)

    @_liblo.make_method('/mididings/prev_scene', '')
    def prev_scene_cb(self, path, args):
        s = sorted(_engine.get_scenes().keys())
        n = s.index(_engine.current_scene()) - 1
        if n >= 0:
            _engine.switch_scene(s[n])

    @_liblo.make_method('/mididings/next_scene', '')
    def next_scene_cb(self, path, args):
        s = sorted(_engine.get_scenes().keys())
        n = s.index(_engine.current_scene()) + 1
        if n < len(s):
            _engine.switch_scene(s[n])

    @_liblo.make_method('/mididings/prev_subscene', '')
    @_liblo.make_method('/mididings/prev_subscene', 'i')
    def prev_subscene_cb(self, path, args):
        s = _engine.get_scenes()[_engine.current_scene()]
        n = _util.real(_engine.current_subscene()) - 1
        if len(s[1]) and len(args) and args[0]:
            n %= len(s[1])
        if n >= 0:
            _engine.switch_subscene(_util.offset(n))

    @_liblo.make_method('/mididings/next_subscene', '')
    @_liblo.make_method('/mididings/next_subscene', 'i')
    def next_subscene_cb(self, path, args):
        s = _engine.get_scenes()[_engine.current_scene()]
        n = _util.real(_engine.current_subscene()) + 1
        if len(s[1]) and len(args) and args[0]:
            n %= len(s[1])
        if n < len(s[1]):
            _engine.switch_subscene(_util.offset(n))

    @_liblo.make_method('/mididings/panic', '')
    def panic_cb(self, path, args):
        _panic.panic_bypass()

    @_liblo.make_method('/mididings/quit', '')
    def quit_cb(self, path, args):
        _engine.quit()



class _SendOSC(object):
    def __init__(self, target, path, args):
        self.target = target
        self.path = path
        self.args = args

    def __call__(self, ev):
        args = ((x(ev) if callable(x) else x) for x in self.args)
        _liblo.send(self.target, self.path, *args)


def SendOSC(target, path, *args):
    return Call(_SendOSC(target, path, args))
