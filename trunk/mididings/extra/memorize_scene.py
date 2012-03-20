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

import mididings.setup as _setup
import mididings.engine as _engine

import sys as _sys


class MemorizeScene(object):
    def __init__(self, memo_file):
        self.memo_file = memo_file

    def on_start(self):
        try:
            f = open(self.memo_file)
            s = f.read()
            try:
                # single scene number
                _setup.config(initial_scene=int(s))
            except ValueError:
                try:
                    # scene and subscene number
                    _setup.config(initial_scene=tuple(map(int, s.split())))
                except ValueError:
                    pass
        except IOError:
            # couldn't open memo file, might not be an error
            pass

    def on_exit(self):
        try:
            f = open(self.memo_file, 'w')
            f.write("%d %d\n" % (_engine.current_scene(), _engine.current_subscene()))
        except IOError:
            # yuck. not willing to break compatibility with python 2.5 just yet...
            _, ex, _ = _sys.exc_info()
            print("couldn't store current scene:\n%s" % str(ex))
