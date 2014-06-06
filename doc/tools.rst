.. _tools:

GUI and Command Line Tools
==========================


.. _mididings:

:command:`mididings`
--------------------

With the mididings command line application, simple patches can
be specified directly in your favorite shell, so sometimes there's no
need to write full-fledged Python scripts::

    $ mididings "Transpose(3) >> Channel(2)"

See ``mididings --help`` for a list of all command line options.

It's also worth mentioning that mididings can easily be used in an
interactive Python session::

    $ python -i -c "from mididings import *"
    >>> run(Transpose(3) >> Channel(2))


:command:`livedings`
--------------------

livedings is a graphical frontend for mididings that allows
you to monitor and trigger scene changes.
It runs as a separate application that uses OSC to communicate with
mididings.
To use it, enable the :class:`~.OSCInterface` hook in your mididings script::

    from mididings.extra.osc import OSCInterface

    hook(OSCInterface())
    ...

Then run livedings::

    $ livedings

By default, livedings uses the standard Tk theme. Specify the ``-T``
option to switch to a custom theme with higher contrast and larger fonts.
See ``livedings --help`` for more options.

The buttons at the bottom of the screen can be used to switch to the
previous/next scene, previous/next subscene, and to send all-notes-off
messages (panic) on all output ports. It's also possible to use the
arrow keys to switch scenes (up/down) and subscenes (left/right).


:command:`send_midi`
--------------------

send_midi is a simple utility to send MIDI events to any ALSA or
JACK MIDI client, using a terse command line format::

    $ send_midi LinuxSampler:0 NOTEON,1,60,127 CTRL,2,7,66
    $ send_midi -J mididings:in_.* PROGRAM,1,42
    $ send_midi 14:0 SYSEX,F0,23,42,F7

See ``send_midi --help`` for a list of all command line options.
