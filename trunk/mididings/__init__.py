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

from mididings.setup import config, hook
from mididings.engine import run, process_file
from mididings.constants import *
from mididings.scene import *
from mididings.units import *


__version__ = '20120419'


import mididings.misc as _misc
__all__ = _misc.prune_globals(globals())
