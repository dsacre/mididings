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

import Tkinter


class LiveThemedFactory(object):
    def __init__(self, options):
        self.options = options

    def Frame(self, master, **options):
        w = Tkinter.Frame(master)
        w.config(background=self.options.color)
        w.config(**options)
        return w

    def AutoScrollbar(self, master, **options):
        w = self._AutoScrollbar(master)
        w.config(
            background=self.options.color,
            activebackground=self.options.color_highlight,
            troughcolor='black',
            borderwidth=1,
            relief='flat',
            width=16,
        )
        w.config(**options)
        return w

    class _AutoScrollbar(Tkinter.Scrollbar):
        def set_show_hide(self, show, hide):
            self._show = show
            self._hide = hide

        def set(self, lo, hi):
            if float(lo) <= 0.0 and float(hi) >= 1.0:
                self._hide()
            else:
                self._show()
            Tkinter.Scrollbar.set(self, lo, hi)

    def Listbox(self, master, **options):
        w = Tkinter.Listbox(master)
        w.config(
            background='black',
            foreground=self.options.color,
            selectbackground='black',
            selectforeground=self.options.color_highlight,
            selectborderwidth=0,
            borderwidth=0,
            highlightthickness=0,
            activestyle='none',
            font=self.options.list_font,
            selectmode='single'
        )
        w.config(**options)
        return w

    def Button(self, master, **options):
        w = Tkinter.Button(master)
        w.config(
            background='black',
            foreground=self.options.color,
            activebackground='black',
            activeforeground=self.options.color_highlight,
            highlightcolor='red',
            highlightbackground='yellow',
            borderwidth=0,
            highlightthickness=0,
            relief='flat',
            font='Sans 20 bold',
        )
        w.config(**options)
        return w
