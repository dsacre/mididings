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

from mididings.units import *
from mididings.scene import *
from mididings.event import *
from mididings.main import *


import inspect as _inspect

def _prune_globals(d):
    return [n for (n, m) in d.items() if not _inspect.ismodule(m) and not n.startswith('_')]

__all__ = _prune_globals(globals())
