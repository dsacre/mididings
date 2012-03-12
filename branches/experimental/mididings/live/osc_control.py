# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2012  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import liblo


class LiveOSC(liblo.ServerThread):
    def __init__(self, dings, control_port, listen_port):
        liblo.ServerThread.__init__(self, listen_port)

        self.dings = dings
        self.control_port = control_port

        self._scenes = {}

    def query(self):
        self.send(self.control_port, '/mididings/query')

    def switch_scene(self, n):
        self.send(self.control_port, '/mididings/switch_scene', n)

    def switch_subscene(self, n):
        self.send(self.control_port, '/mididings/switch_subscene', n)

    def prev_scene(self):
        self.send(self.control_port, '/mididings/prev_scene')

    def next_scene(self):
        self.send(self.control_port, '/mididings/next_scene')

    def prev_subscene(self):
        self.send(self.control_port, '/mididings/prev_subscene')

    def next_subscene(self):
        self.send(self.control_port, '/mididings/next_subscene')

    def panic(self):
        self.send(self.control_port, '/mididings/panic')

    @liblo.make_method('/mididings/data_offset', 'i')
    def data_offset_cb(self, path, args):
        self.dings.set_data_offset(args[0])

    @liblo.make_method('/mididings/begin_scenes', '')
    def begin_scenes_cb(self, path, args):
        self._scenes = {}

    @liblo.make_method('/mididings/add_scene', None)
    def add_scene_cb(self, path, args):
        number, name = args[:2]
        subscenes = args[2:]
        self._scenes[number] = (name, subscenes)

    @liblo.make_method('/mididings/end_scenes', '')
    def end_scenes_cb(self, path, args):
        self.dings.set_scenes(self._scenes)

    @liblo.make_method('/mididings/current_scene', 'ii')
    def current_scene_cb(self, path, args):
        self.dings.set_current_scene(args[0], args[1])
