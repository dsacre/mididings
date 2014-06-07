.. currentmodule:: mididings

:tocdepth: 2

.. _gettingstarted:

Getting Started
===============

.. _anatomy:

Anatomy of a mididings Script
-----------------------------

mididings configuration files are just Python scripts, although some of
Python's features are used in ways for which they weren't intended ;)
Technically speaking, mididings is an embedded domain-specific language
based on Python.

The main difference between mididings and regular Python scripts is that
mididings typically uses Python only at startup. Patches consist of Python
objects and nested data structures,
but not actual Python code to be executed once everything is set up.
Internally, patches are converted to C++ objects, and the processing
is done entirely in C++.
It is however possible to call back into Python, if necessary.

Although mididings is a Python module that can theoretically be imported
in other Python applications, it's really not designed to be used that way.
Think of mididings as a standalone application, that just happens to
use Python as its "user interface".


.. _examples:

Examples
--------

Let's start with something very simple::

    from mididings import *
    run(Transpose(3))

Here the import statement imports everything from the mididings Python module
into the global namespace. The :func:`run()` function is then used to
execute a simple patch, consisting of just a single :func:`Transpose()` unit.

You can start this script by saving it to a Python file and executing it,
for example:

.. code-block:: sh

    $ python transpose.py

What this script does is to create an ALSA MIDI client with one input and
one output port. It will then start listening for events on the input port,
transpose all incoming note-on and note-off events up by 3 semitones,
and send all events to the output port. Pressing :kbd:`Ctrl+C` terminates
the script.


Ok, that was easy. Now let's try something slightly more complex::

    from mididings import *

    config(
        backend='jack-rt',
        client_name='example',
    )

    run(
        Velocity(curve=1.0) >> [
            Transpose(12),
            Filter(NOTE|CTRL) >> Channel(3),
        ]
    )

The first thing that's new in this example is the :func:`config()` function.
This function is used to configure some global settings, and should usually
be called only once, at the start of the script. Here, it is used to select
the JACK backend instead of ALSA, and to change the JACK client name from
``'mididings'`` to ``'example'``.

Now, let's look at the patch inside the :func:`run()` function call.
There are four mididings units used in this patch:

- ``Velocity(curve=1.0)`` applies a velocity curve to all note-on events,
  increasing their velocity values.
- ``Transpose(12)`` transposes all note events up by 12 semitones.
- ``Filter(NOTE|CTRL)`` removes all events that are not note-on, note-off
  or CC events.
- ``Channel(3)`` changes the MIDI channel of all events to channel 3.

Each of these units is quite simple on its own, but what's important is
how the units are connected to each other:

- ``A >> B`` connects two units in series, so every event output by unit A
  is then passed to unit B.
- ``[A, B, ...]`` (which is just a :class:`list` in Python) connects units
  in parallel, so each of these units gets its own copy of incoming events
  and processes them individually.

A graphical representation of the patch above would look something like this:

.. image:: patch.png
   :alt: mididings example patch

For incoming note-on, note-off and CC events, this patch will output two
events: one on the original MIDI channel, with notes being transposed by
one octave, and one on channel 3, with no transposition.
All other event types will result in only one event being sent to the
output (on their original channel), because those event types are filtered
out in the lower branch of the patch.


Multiple Scenes
^^^^^^^^^^^^^^^

Often it's desirable to run not just a single patch, but many different
ones which can be switched using a MIDI controller.
With mididings it's possible to switch between an arbitrary number of
"scenes", each of which consists of one patch, and optionally an
"init-patch" that will be triggered every time you switch to that scene.

Here's an example::

    from mididings import *

    run(
        scenes = {
            1:  Scene("channel 1 only",
                    Channel(1)
                ),
            2:  Scene("channel 2, program 23",
                    Channel(2),
                    Program(23) >> Channel(2)
                ),
            3:  Scene("channel 2, program 42",
                    Channel(2),
                    Program(42) >> Channel(2)
                ),
            4:  Scene("channel 1/3 split",
                    KeySplit('c3',
                        Channel(1),
                        Channel(3)
                    )
                ),
        },
        control = Filter(PROGRAM) >> SceneSwitch(),
        pre = ~Filter(PROGRAM),
    )

This script defines 4 *scenes*.
In the first scene, all incoming events are simply routed to output channel 1.
In scenes 2 and 3, events are routed to channel 2. Additionally, when
switching to one of these scenes, MIDI program change messages will be
sent on that channel first.
The fourth scene splits the keyboard at C3 and routes both regions of the
keyboard to different output channels.

The *control* patch is used to switch between these scenes. The filter
lets only program changes through, which upon reaching the
:func:`SceneSwitch()` then trigger the scene switches.
In this example we assume that incoming program changes are only used for
switching scenes, and should not be processed by the currently active scene.
Therefore the *pre* patch is used to filter out these events.

This is a complete overview of the event flow when using multiple scenes:

.. image:: eventflow.png
    :alt: mididings event flow

The *control*, *pre* and *post* patches as well as any of the init patches
are optional and can be omitted if they are not needed.
The control patch can be used for any event processing that does not depend
on the currently active scene.

.. note::

    The use of init patches can often be significantly simplified
    by embedding them into the regular patches, in particular using the
    :func:`Output()` unit and the :class:`OutputTemplate` class.
