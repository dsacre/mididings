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

from mididings.live.widgets import LiveThemedFactory, UnthemedFactory
from mididings.live.osc_control import LiveOSC

import sys
if sys.version_info >= (3,):
    unichr = chr


class LiveDings(object):
    def __init__(self, options):
        self.options = options

        # start OSC server
        self.osc = LiveOSC(self, self.options.control_port, self.options.listen_port)
        self.osc.start()

        if self.options.themed:
            widget_factory = LiveThemedFactory(self.options.color,
                                               self.options.color_highlight,
                                               self.options.color_background)
        else:
            widget_factory = UnthemedFactory()

        # create the main window
        self.win = widget_factory.Tk(padx=8, pady=8)
        self.win.minsize(480, 120)
        self.win.geometry('%dx%d' % (self.options.width, self.options.height))

        if self.options.name:
            self.win.title('livedings - %s' % self.options.name)
        else:
            self.win.title('livedings')

        # track window resizing
        self.win.bind('<Configure>', lambda event: self.win.after_idle(self.update, True))

        # configure the grid
        self.win.grid_rowconfigure(0, weight=1)
        self.win.grid_columnconfigure(1, minsize=self.options.list_width, weight=0)
        for n in range(3, 8):
            self.win.grid_columnconfigure(n, weight=1, minsize=64)

        # create listbox
        self.listbox = widget_factory.Listbox(self.win, font=self.options.list_font,
                                              selectmode='single', activestyle='none',
                                              highlightthickness=0)
        self.listbox.grid(column=1, row=0, rowspan=2, sticky='nsew', padx=8)
        self.listbox.bind('<ButtonRelease-1>', lambda event: self.on_select_scene())

        # create scrollbar for listbox. will be attached to the grid only when necessary
        self.scrollbar = widget_factory.AutoScrollbar(self.win, orient='vertical')
        self.scrollbar.set_show_hide(
            lambda: self.scrollbar.grid(column=0, row=0, rowspan=2, sticky='ns'),
            lambda: self.scrollbar.grid_forget()
        )
        self.scrollbar.config(command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        # create separator
        separator = widget_factory.Frame(self.win, width=2)
        separator.grid(column=2, row=0, rowspan=2, sticky='ns')

        # create canvas
        self.canvas = widget_factory.Canvas(self.win, highlightthickness=0)
        if self.options.color_background is not None:
            self.canvas.config(background=self.options.color_background)
        self.canvas.grid(column=3, columnspan=5, row=0, sticky='nsew')
        self.canvas.bind('<Button-1>', self.on_button_press)
        self.canvas.bind('<ButtonRelease-1>', self.on_button_release)

        # create buttons
        try:
            button_size = int(int(self.options.font.split(' ')[1]) / 1.5)
        except IndexError:
            button_size = 20
        button_font = 'Sans %d bold' % button_size

        self.btn_prev_scene = widget_factory.Button(self.win, text=unichr(0x25c0)*2,
                                                    width=64, font=button_font, command=self.osc.prev_scene)
        self.btn_prev_scene.grid(column=3, row=1, padx=8)
        self.btn_next_scene = widget_factory.Button(self.win, text=unichr(0x25b6)*2,
                                                    width=64, font=button_font, command=self.osc.next_scene)
        self.btn_next_scene.grid(column=4, row=1, padx=8)

        self.btn_prev_subscene = widget_factory.Button(self.win, text=unichr(0x25c0),
                                                       width=64, font=button_font, command=self.osc.prev_subscene)
        self.btn_prev_subscene.grid(column=5, row=1, padx=8)
        self.btn_next_subscene = widget_factory.Button(self.win, text=unichr(0x25b6),
                                                       width=64, font=button_font, command=self.osc.next_subscene)
        self.btn_next_subscene.grid(column=6, row=1, padx=8)

        self.btn_panic = widget_factory.Button(self.win, text="!",
                                               width=64, font=button_font, command=self.osc.panic)
        self.btn_panic.grid(column=7, row=1, padx=8)

        # attempt to calculate the height of one line in the current font. this is crazy...
        try:
            self.line_height = int(self.options.font.split(' ')[1]) * 2
        except Exception:
            # whatever...
            self.line_height = 72

        # some keybindings
        self.win.bind('<Left>', lambda event: self.osc.prev_subscene())
        self.win.bind('<Right>', lambda event: self.osc.next_subscene())
        self.win.bind('<Up>', lambda event: self.osc.prev_scene())
        self.win.bind('<Down>', lambda event: self.osc.next_scene())
        self.win.bind('<Escape>', lambda event: self.osc.panic())
        # prevent left/right keys from scrolling the listbox
        self.win.bind_class('Listbox', "<Left>", lambda event: None)
        self.win.bind_class('Listbox', "<Right>", lambda event: None)

        # get config from mididings
        self.osc.query()

        self._ready = False

        # window dimensions
        self._width = 0
        self._height = 0
        # mouse click position
        self._click_x = 0
        self._click_y = 0

    def on_select_scene(self):
        cursel = self.listbox.curselection()
        if cursel:
            self.osc.switch_scene(sorted(self.scenes.keys())[int(cursel[0])])

    def on_button_press(self, event):
        self._click_x = event.x
        self._click_y = event.y

    def on_button_release(self, event):
        if (self._ready and self._click_y > 8 + 3 * self.line_height and
            self._click_y < 8 + (len(self.scenes[self.current_scene][1])+3) * self.line_height):
            n = (self._click_y - (8 + 3 * self.line_height)) / self.line_height
            self.osc.switch_subscene(n + self.data_offset)

    def update(self, resize=False):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # check if the window size really changed
        if resize and width == self._width and height == self._height:
            return

        self.draw_canvas(width, height)
        self._width = width
        self._height = height

    def set_data_offset(self, data_offset):
        self.data_offset = data_offset

    def set_scenes(self, scenes):
        self.scenes = scenes
        self.update_scenes()
        self._ready = True

    def set_current_scene(self, scene, subscene):
        self.current_scene = scene
        self.current_subscene = subscene
        self.listbox.selection_clear(0, 'end')
        self.listbox.selection_set(sorted(self.scenes.keys()).index(scene))
        self.update()

    def update_scenes(self):
        self.listbox.delete(0, 'end')
        for n in sorted(self.scenes.keys()):
            name = self.scenes[n][0]
            if name:
                self.listbox.insert('end', "%d: %s" % (n, name))
            else:
                self.listbox.insert('end', "%d" % n)

    def draw_canvas(self, width, height):
        if not self._ready or not len(self.scenes):
            return

        scene = self.current_scene
        subscene = self.current_subscene
        scene_name, subscene_names = self.scenes[scene]
        has_subscenes = bool(len(subscene_names))

        if not scene_name:
            scene_name = "(unnamed)"

        self.canvas.delete('all')

        # draw scene number
        self.canvas.create_text(
            24,
            8,
            text=("%d.%d" % (scene, subscene)) if has_subscenes else str(scene),
            fill=self.options.color,
            font=self.options.font,
            anchor='nw'
        )

        # draw scene name
        self.canvas.create_text(
            width / 2 + 24,
            8 + 1.5 * self.line_height,
            text=scene_name,
            fill=self.options.color_highlight,
            font=self.options.font,
            anchor='n'
        )

        # draw subscenes
        for n, s in enumerate(subscene_names):
            self.canvas.create_text(
                width / 2 + 24,
                8 + (n+3) * self.line_height,
                text=s if s else "(unnamed)",
                fill=self.options.color_highlight if n + self.data_offset == subscene else self.options.color,
                font=self.options.font,
                anchor='n'
            )

        # draw indicator
        self.canvas.create_text(
            16,
            8 + 1.5 * self.line_height if not has_subscenes else 8 + (subscene - self.data_offset + 3) * self.line_height,
            text=unichr(0x25b6),
            fill=self.options.color_highlight,
            font=self.options.font,
            anchor='nw'
        )

    def run(self):
        self.win.mainloop()
