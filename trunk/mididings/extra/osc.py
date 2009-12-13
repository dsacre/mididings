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

from mididings import Call
import mididings.engine as _engine


try:
    import liblo as _liblo

except ImportError, ex:

    def OSCInterface(*args, **kwargs):
        raise ex
    def SendOSC(*args, **kwargs):
        raise ex

else:

    class OSCInterface(object):
        def __init__(self, port, notify_ports=[]):
            self.port = port
            self.notify_ports = notify_ports

        def on_start(self):
            if self.port != None:
                self.server = _liblo.ServerThread(self.port)
                self.server.add_method('/mididings/switch_scene', 'i', self._switch_scene_cb)
                self.server.add_method('/mididings/quit', '', self._quit_cb)
                self.server.start()

        def on_exit(self):
            if self.port != None:
                self.server.stop()
                del self.server

        def on_switch_scene(self, n):
            for p in self.notify_ports:
                _liblo.send(p, '/mididings/current_scene', n)

        def _switch_scene_cb(self, path, args):
            _engine.switch_scene(args[0])

        def _quit_cb(self, path, args):
            _engine.quit()



    class _SendOSC(object):
        def __init__(self, target, path, args):
            self.target = target
            self.path = path
            self.args = args

        def __call__(self, ev):
            args = (x(ev) if callable(x) else x for x in self.args)
            _liblo.send(self.target, self.path, *args)


    def SendOSC(target, path, *args):
        return Call(_SendOSC(target, path, args))
