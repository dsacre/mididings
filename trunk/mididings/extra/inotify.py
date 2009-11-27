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

from mididings import quit

import atexit as _atexit
import os as _os
import sys as _sys

try:
    import pyinotify as _pyinotify

except ImportError, ex:

    def AutoRestart(*args, **kwargs):
        raise ex

else:

    class AutoRestart(object):
        def __init__(self, *filenames):
            self.filenames = filenames

        def on_start(self):
            self.wm = _pyinotify.WatchManager()
            self.notifier = _pyinotify.ThreadedNotifier(self.wm)
            for f in self.filenames:
                self.wm.add_watch(f, _pyinotify.IN_MODIFY, self._process_IN_MODIFY)
            self.notifier.start()

        def on_exit(self):
            self.notifier.stop()

        def _process_IN_MODIFY(self, event):
            _atexit.register(self._restart)
            quit()

        def _restart(self):
            print "restarting..."
            _os.execl(_sys.executable, _sys.executable, *_sys.argv)
