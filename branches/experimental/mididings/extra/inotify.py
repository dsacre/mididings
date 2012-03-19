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

import os as _os
import sys as _sys

import pyinotify as _pyinotify


class AutoRestart(object):
    def __init__(self, modules=True, filenames=[]):
        self.modules = modules
        self.filenames = filenames

    def on_start(self):
        self.wm = _pyinotify.WatchManager()
        self.notifier = _pyinotify.ThreadedNotifier(self.wm)

        if self.modules:
            # add watches for imported modules
            for m in _sys.modules.values():
                # builtin modules don't have a __file__ attribute
                if hasattr(m, '__file__'):
                    f = m.__file__
                    # only watch modules with relative path or in the current working directory
                    if not _os.path.isabs(f) or f.startswith(_os.getcwd()):
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