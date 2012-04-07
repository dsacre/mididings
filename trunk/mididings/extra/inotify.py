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

import mididings.engine as _engine

import sys as _sys
import os as _os

import pyinotify as _pyinotify


class AutoRestart(object):
    def __init__(self, modules=True, filenames=[]):
        self.modules = modules
        self.filenames = filenames

    def on_start(self):
        self.wm = _pyinotify.WatchManager()
        self.notifier = _pyinotify.ThreadedNotifier(self.wm)

        if self.modules:
            # find the name of the main script being executed
            if '__mididings_main__' in _sys.modules:
                main_file = _sys.modules['__mididings_main__'].__file__
            elif hasattr(_sys.modules['__main__'], '__file__'):
                main_file = _sys.modules['__main__'].__file__
            else:
                main_file = None

            if main_file:
                base_dir = _os.path.dirname(_os.path.abspath(main_file))

                # add watches for imported modules
                for m in _sys.modules.values():
                    # builtin modules don't have a __file__ attribute
                    if hasattr(m, '__file__'):
                        f = _os.path.abspath(m.__file__)
                        # only watch file if it's in the same directory as the
                        # main script
                        if f.startswith(base_dir):
                            self.wm.add_watch(f, _pyinotify.IN_MODIFY, self._process_IN_MODIFY)

        # add watches for additional files
        for f in self.filenames:
            self.wm.add_watch(f, _pyinotify.IN_MODIFY, self._process_IN_MODIFY)

        self.notifier.start()

    def on_exit(self):
        self.notifier.stop()

    def _process_IN_MODIFY(self, event):
        print("file '%s' changed, restarting..." % event.pathname)
        _engine.restart()
