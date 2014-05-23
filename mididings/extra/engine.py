# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2014  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

from mididings import Call as _Call
import mididings.engine as _engine


def Restart():
    """
    Call :func:`.engine.restart()`.
    """
    return _Call(lambda ev: _engine.restart())

def Quit():
    """
    Call :func:`.engine.quit()`.
    """
    return _Call(lambda ev: _engine.quit())
