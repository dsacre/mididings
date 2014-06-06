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

import _mididings

import mididings.patch as _patch
import mididings.scene as _scene
import mididings.util as _util
import mididings.misc as _misc
import mididings.setup as _setup
import mididings.constants as _constants
import mididings.overload as _overload
import mididings.arguments as _arguments
from mididings.units.base import _UNIT_TYPES

import time as _time
import weakref as _weakref
import threading as _threading
import gc as _gc
import atexit as _atexit
import os as _os
import sys as _sys

if _sys.version_info >= (3,):
    raw_input = input


_TheBackend = None
_TheEngine = None


def _start_backend():
    global _TheBackend
    if _TheBackend is None:
        _TheBackend = _mididings.create_backend(
            _setup.get_config('backend'),
            _setup.get_config('client_name'),
            _setup._in_portnames,
            _setup._out_portnames
        )
        if _TheBackend:
            _TheBackend.connect_ports(_setup._in_port_connections,
                                      _setup._out_port_connections)


class Engine(_mididings.Engine):
    def __init__(self):
        _start_backend()

        verbose = not _setup.get_config('silent')
        # initialize C++ base class
        _mididings.Engine.__init__(self, _TheBackend, verbose)

        self._scenes = {}

    def setup(self, scenes, control, pre, post):
        # build and setup all scenes and scene groups
        for number, scene in scenes.items():
            if isinstance(scene, _scene.SceneGroup):
                self._scenes[number] = (scene.name, [])

                for subscene in scene.subscenes:
                    sceneobj = _scene._parse_scene(subscene)
                    self._scenes[number][1].append(sceneobj.name)

                    # build patches
                    patch = _patch.Patch(sceneobj.patch)
                    init_patch = _patch.Patch(sceneobj.init_patch)
                    exit_patch = _patch.Patch(sceneobj.exit_patch)
                    # add scene to base class object
                    self.add_scene(_util.actual(number),
                                   patch, init_patch, exit_patch)
            else:
                sceneobj = _scene._parse_scene(scene)
                self._scenes[number] = (sceneobj.name, [])

                # build patches
                patch = _patch.Patch(sceneobj.patch)
                init_patch = _patch.Patch(sceneobj.init_patch)
                exit_patch = _patch.Patch(sceneobj.exit_patch)
                # add scene to base class object
                self.add_scene(_util.actual(number),
                               patch, init_patch, exit_patch)

        # build and setup control, pre, and post patches
        control_patch = _patch.Patch(control) if control else None
        pre_patch = _patch.Patch(pre) if pre else None
        post_patch = _patch.Patch(post) if post else None
        # tell base class object about these patches
        self.set_processing(control_patch, pre_patch, post_patch)

        global _TheEngine
        _TheEngine = _weakref.ref(self)

        _gc.collect()
        _gc.disable()

    def run(self):
        self._quit = _threading.Event()

        # delay before actually sending any midi data (give qjackctl
        # patchbay time to react...)
        self._start_delay()

        self._call_hooks('on_start')

        initial_scene, initial_subscene = \
            self._parse_scene_number(_setup.get_config('initial_scene'))

        # start the actual event processing
        self.start(initial_scene, initial_subscene)

        try:
            # wait() with no timeout also blocks KeyboardInterrupt, but
            # a very long timeout doesn't. weird...
            while not self._quit.isSet():
                self._quit.wait(86400)
        except KeyboardInterrupt:
            pass
        finally:
            self._call_hooks('on_exit')
            global _TheEngine
            _TheEngine = None

    def _start_delay(self):
        delay = _setup.get_config('start_delay')
        if delay is not None:
            if delay > 0:
                _time.sleep(delay)
            else:
                raw_input("press enter to start midi processing...")

    def _parse_scene_number(self, number):
        if number in self._scenes:
            # single scene number, no subscene
            return (_util.actual(number), -1)
        elif (_misc.issequence(number) and
                len(number) > 1 and number[0] in self._scenes):
            # scene/subscene numbers as tuple...
            if _util.actual(number[1]) < len(self._scenes[number[0]][1]):
                # both scene and subscene numbers are valid
                return (_util.actual(number[0]), _util.actual(number[1]))
            # subscene number is invalid
            return (_util.actual(number[0]), -1)
        # no such scene
        return (-1, -1)

    def scene_switch_callback(self, scene, subscene):
        # scene and subscene parameters are the actual numbers without offset!
        if scene == -1:
            # no scene specified, use current
            scene = _mididings.Engine.current_scene(self)
        if subscene == -1:
            # no subscene specified, use first
            subscene = 0

        # save actual subscene index
        subscene_index = subscene

        # add data offset to scene/subscene numbers
        scene = _util.offset(scene)
        subscene = _util.offset(subscene)

        found = (scene in self._scenes and
                 (not subscene_index or
                    subscene_index < len(self._scenes[scene][1])))

        # get string representation of scene/subscene number
        if (subscene_index or
                (scene in self._scenes and len(self._scenes[scene][1]))):
            number = "%d.%d" % (scene, subscene)
        else:
            number = str(scene)

        if not _setup.get_config('silent'):
            if found:
                # get scene/subscene name
                scene_data = self._scenes[scene]
                if scene_data[1]:
                    name = "%s - %s" % (scene_data[0],
                                        scene_data[1][subscene_index])
                else:
                    name = scene_data[0]

                scene_desc = (("%s: %s" % (number, name)) if name
                                else str(number))
                print("switching to scene %s" % scene_desc)
            else:
                print("no such scene: %s" % number)

        if found:
            self._call_hooks('on_switch_scene', scene, subscene)

    def _call_hooks(self, name, *args):
        for hook in _setup.get_hooks():
            if hasattr(hook, name):
                f = getattr(hook, name)
                f(*args)

    def switch_scene(self, scene, subscene=None):
        _mididings.Engine.switch_scene(self,
            _util.actual(scene),
            _util.actual(subscene) if subscene is not None else -1
         )

    def switch_subscene(self, subscene):
        _mididings.Engine.switch_scene(self, -1, _util.actual(subscene))

    def current_scene(self):
        return _util.offset(_mididings.Engine.current_scene(self))

    def current_subscene(self):
        return _util.offset(_mididings.Engine.current_subscene(self))

    def scenes(self):
        return self._scenes

    def process_event(self, ev):
        ev._finalize()
        return _mididings.Engine.process_event(self, ev)

    def output_event(self, ev):
        ev._finalize()
        _mididings.Engine.output_event(self, ev)

    def process(self, ev):
        ev._finalize()
        return _mididings.Engine.process(self, ev)

    def restart(self):
        _atexit.register(self._restart)
        self.quit()

    @staticmethod
    def _restart():
        # run the same interpreter with the same arguments again
        _os.execl(_sys.executable, _sys.executable, *_sys.argv)

    def quit(self):
        self._quit.set()



@_overload.mark(
    """
    run(patch)
    run(scenes=..., control=None, pre=None, post=None)

    Start the MIDI processing. This is usually the last function called by a
    mididings script.
    The first version just runs a single patch, while the second version
    allows switching between multiple scenes.

    :param patch: a single patch.
    :param scenes: a dictionary with program numbers as keys, and
        :class:`Scene` objects, :class:`SceneGroup` objects or plain patches
        as values.
    :param control: an optional "control" patch, which is always active, and
        runs in parallel to the current scene.
    :param pre: an optional patch that allows common processing to take place
        before every scene. Does not affect the control patch.
    :param post: an optional patch that allows common processing to take place
        after every scene. Does not affect the control patch.
    """
)
@_arguments.accept(_UNIT_TYPES)
def run(patch):
    if (isinstance(patch, dict) and
            all(not isinstance(k, _constants._EventType)
                for k in patch.keys())):
        # bypass the overload mechanism (just this once...) if there's no way
        # the given dict could be accepted as a split
        run(scenes=patch)
    else:
        e = Engine()
        e.setup({_util.offset(0): patch}, None, None, None)
        e.run()

@_overload.mark
@_arguments.accept(
    _UNIT_TYPES,
    _arguments.nullable(_UNIT_TYPES),
    _arguments.nullable(_UNIT_TYPES),
    _arguments.nullable(_UNIT_TYPES)
)
def run(scenes, control=None, pre=None, post=None):
    e = Engine()
    e.setup(scenes, control, pre, post)
    e.run()


def switch_scene(scene, subscene=None):
    """
    Switch to the given scene number.
    """
    _TheEngine().switch_scene(scene, subscene)

def switch_subscene(subscene):
    """
    Switch to the given subscene number.
    """
    _TheEngine().switch_subscene(subscene)

def current_scene():
    """
    Return the current scene number.
    """
    return _TheEngine().current_scene()

def current_subscene():
    """
    Return the current subscene number.
    """
    return _TheEngine().current_subscene()

def scenes():
    """
    Return a dictionary of all scenes. Keys are scene numbers, values are
    tuples containing the scene name and a (possibly empty) list of subscene
    names.
    """
    return _TheEngine().scenes()

def output_event(ev):
    """
    Send an event directly to an output port, completely bypassing any other
    event processing.
    """
    _TheEngine().output_event(ev)

def in_ports():
    """
    Return a list of the configured input port names.
    """
    return _setup._in_portnames

def out_ports():
    """
    Return a list of the configured output port names.
    """
    return _setup._out_portnames

def time():
    """
    Return the time in seconds (floating point) since some unspecified
    starting point. Unlike Python's :func:`time.time()`, this clock is
    guaranteed to be monotonic.
    """
    return _TheEngine().time()

def active():
    """
    Return ``True`` if the mididings engine is active (the :func:`~.run()`
    function is running).
    """
    return _TheEngine is not None and _TheEngine() is not None

def restart():
    """
    Restart the mididings script by terminating the current process, and then
    running the same Python interpreter with the same arguments again.
    This will not work properly if :func:`~.run()` is not the last call in
    your script, or if you're running mididings in an interactive Python
    interpreter.
    """
    _TheEngine().restart()

def quit():
    """
    Terminate mididings by making the :func:`~.run()` function return.
    """
    _TheEngine().quit()



def process_file(infile, outfile, patch):
    """
    Process a MIDI file, using pysmf.
    """
    import smf

    # create dummy engine with no inputs or outputs
    _setup._config_impl(backend='dummy')
    engine = Engine()
    engine.setup({_util.offset(0): patch}, None, None, None)

    # open input file
    smf_in = smf.SMF(infile)

    # create SMF object with same ppqn and number of tracks as input file
    smf_out = smf.SMF()
    smf_out.ppqn = smf_in.ppqn
    for n in range(len(smf_in.tracks)):
        smf_out.add_track()

    for smf_ev in smf_in.events:
        if smf_ev.midi_buffer[0] == 0xff:
            # event is metadata. copy to output unmodified
            smf_out.add_event(smf.Event(smf_ev.midi_buffer),
                              smf_ev.track_number, pulses=smf_ev.time_pulses)
        else:
            ev = _mididings.buffer_to_midi_event(smf_ev.midi_buffer,
                              smf_ev.track_number, smf_ev.time_pulses)

            # use base class version of process_event() to bypass calling
            # ev._finalize(), which would fail since ev is of type
            # _mididings.MidiEvent.
            for out_ev in _mididings.Engine.process_event(engine, ev):
                buf, track, pulses = _mididings.midi_event_to_buffer(out_ev)
                smf_out.add_event(smf.Event(buf), track, pulses=pulses)

    smf_out.save(outfile)
