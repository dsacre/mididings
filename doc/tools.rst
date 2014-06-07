:tocdepth: 2

.. _tools:

Command Line Tools and GUI
==========================

.. highlight:: sh


.. _mididings:

:command:`mididings`
--------------------

The mididings command line tool offers several ways to run patches without
writing full-fledged Python scripts.
See ``mididings --help`` for a list of all command line options.


.. _scripts:

mididings Patches and Scripts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Simple patches can be specified directly on the command line::

    $ mididings "Transpose(3) >> Channel(2)"

mididings scripts in general are regular Python source files.
They can be executed either by invoking the Python interpreter directly,
or by invoking mididings with the ``-f`` option::

    $ python test.py
    # or:
    $ mididings -f test.py

These two commands differ in that the latter reads the :ref:`default-config`,
while the former does not.
For convenience, ``mididings -f`` also imports the :mod:`mididings` and
:mod:`mididings.extra` modules automatically, so that scripts may omit
these import statements.


.. _interactive:

Interactive Shell
^^^^^^^^^^^^^^^^^

mididings provides a shell based on an interactive Python interpreter,
offering history and tab-completion, to quickly build and test patches:

.. code-block:: pycon

    $ mididings -s
    mididings 2014+rf6e2d01, using Python 3.3.2+
    >>> run(Filter(NOTE) >> Channel(2) // Channel(3))
    ^C
    >>> run(Filter(NOTE|CTRL) >> Channel(1) // Channel(13))
    ^C
    >>> ...

The ALSA or JACK backend is initialized at startup and remains active if a
call to the :func:`~.run()` function is interrupted.
This way you can easily switch patches without reconnecting your clients.

If mididings is started with the ``-S`` option, you don't even need to call
the :func:`~.run()` function explicitly, and any valid patches you enter
will be started automatically.
This can be bypassed by prepending a space, resulting in Python's usual
behavior of evaluating the expression you entered, and displaying its result:

.. code-block:: pycon

    $ mididings -S
    mididings 2014+rf6e2d01, using Python 3.3.2+
    >>> ChannelFilter(2) % Transpose(3)
    ^C
    >>>  ChannelFilter(2) % Transpose(3)
    [ChannelFilter(channels=[2]) >> Transpose(offset=3), -ChannelFilter(channels=[2])]
    >>> ...


.. _logger:

MIDI Event Logger
^^^^^^^^^^^^^^^^^

To execute a patch consisting of a single :func:`~.Print()` unit,
with client name ``'printdings'``, run ``mididings -p``.


.. _port-connect:

Ports and Connections
^^^^^^^^^^^^^^^^^^^^^

The ``-A``, ``-J`` and ``-R`` command line options correspond to (and override)
the :c:data:`backend` setting.
The ``-i`` and ``-o`` options can be used to specify the number (but not names)
of input and output ports.
The ``-I`` and ``-O`` options may be specified multiple times, once for each
port, to specify other client's ports to connect to. ::

    # split output of jack-keyboard between fluidsynth and yoshimi
    $ mididings -R -o 2 -I jack-keyboard:midi_out \
        -O fluidsynth-midi:midi -O yoshimi:midi\ in \
        "KeySplit('c3', Port(1), Port(2))"

.. _default-config:

Default Configuration File
^^^^^^^^^^^^^^^^^^^^^^^^^^

mididings reads settings from :file:`$XDG_CONFIG_HOME/mididings/default.py`
(:file:`~/.config/mididings/default.py`), if that file exists.
This file will typically contain a call to :func:`~.config()`, but may also be
used to import additional modules, define classes or functions, and set global
variables.
Anything stored in the global scope within this config file is automatically
made available to your mididings scripts or patches.  ::

    # change default octave_offset to match Scientific Pitch Notation
    $ echo "config(octave_offset=1)" >> ~/.config/mididings/default.py
    # use JACK by default
    $ echo "config(backend='jack')" >> ~/.config/mididings/default.py

Global :func:`~.config()` settings made here can be overridden by settings
in mididings scripts, which in turn can be overridden by mididings command
line options.

.. note::

    The configuration file is only read when invoking the :command:`mididings`
    command line application.
    It is not used when the :mod:`mididings` module is imported from a regular
    Python script.


.. _livedings:

:command:`livedings`
--------------------

livedings is a graphical frontend for mididings that allows
you to monitor and trigger scene changes.
It runs as a separate application that uses OSC to communicate with
mididings.
To use it, enable the :class:`~.OSCInterface` hook in your mididings script

.. code-block:: py

    from mididings.extra.osc import OSCInterface

    hook(OSCInterface())
    ...

Then run the ``livedings`` application.

By default, livedings uses the standard Tk theme. Specify the ``-T``
option to switch to a custom theme with higher contrast and larger fonts.
See ``livedings --help`` for more options.

The buttons at the bottom of the screen can be used to switch to the
previous/next scene, previous/next subscene, and to send all-notes-off
messages (panic) on all output ports. It's also possible to use the
arrow keys to switch scenes (up/down) and subscenes (left/right).


.. _send_midi:

:command:`send_midi`
--------------------

send_midi is a simple utility to send MIDI events to any ALSA or
JACK MIDI client, using a terse command line format::

    $ send_midi LinuxSampler:0 NOTEON,1,60,127 CTRL,2,7,66
    $ send_midi -J mididings:in_.* PROGRAM,1,42
    $ send_midi 14:0 SYSEX,F0,23,42,F7

See ``send_midi --help`` for a list of all command line options.
