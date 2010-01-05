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

import mididings.setup as _setup
import mididings.engine as _engine


class MemorizeScene(object):
    def __init__(self, memo_file):
        self.memo_file = memo_file

    def on_start(self):
        try:
            f = open(self.memo_file)
            _setup.config(initial_scene=int(f.read()))
        except IOError:
            # couldn't open memo file, might not be an error
            pass

    def on_exit(self):
        try:
            f = open(self.memo_file, 'w')
            f.write(str(_engine.current_scene()) + '\n')
        except IOError, ex:
            print "couldn't store current scene:\n%s" % str(ex)
