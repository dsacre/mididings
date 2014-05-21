.. module:: mididings

.. _main:

Module :mod:`mididings`
=======================


.. _main-config:

Global Configuration
--------------------

These global settings can be configured using the :func:`config()` function
described below:

.. c:var:: backend

    The MIDI backend to be used:

    * | ``'alsa'``: Use the ALSA sequencer.
    * | ``'jack'``: Use JACK MIDI. All MIDI events are buffered and processed
        outside the JACK process callback, and will thus be delayed by (at
        least) one period.
    * | ``'jack-rt'``: Use JACK MIDI. All MIDI events are processed directly
        in the JACK process callback. Running Python code in a realtime
        context may cause xruns (or worse), so it's recommended not to use
        the :func:`Process()` unit, or many of the units from the
        :mod:`mididings.extra` module, which use :func:`Process()`
        internally. All other units from the main :mod:`mididings` module
        are safe to use.

    The default, if available, is ``'alsa'``.

.. c:var:: client_name

    The ALSA or JACK client name to be used. The default is ``'mididings'``.

.. c:var:: in_ports
           out_ports

    Defines the number and names of input and output ports, and optionally
    external ports to connect them to. The default is one input and one output
    port.

    Possible values are:

    * | Integers: Simply indicates the number of ports to create (named
        ``in_n`` and ``out_n``, respectively, where ``n`` is the index of the
        port).

    * | Lists of ports:
        Each port is either described by a single string specifying its name,
        or by a list/tuple containing the port name, followed by any number
        of regular expressions specifying ports to connect to.
      | These regular expressions are matched against the full name
        (clientname:portname) of each external port. ALSA clients and ports can
        be referred to using either their names or numbers.

    .. code::

        # create two input ports
        in_ports = 2

        # create three output ports with custom names, and automatically
        # connect two of those ports to other clients
        out_ports = [
            'foo',
            ('bar', '24:0', 'yoshimi:midi in'),
            ('baz', 'LinuxSampler:.*'),
        ]

.. c:var:: data_offset

    Determines whether program, port and channel numbers used in your script
    are in the range 1-128 (with data_offset = 1) or 0-127 (with
    data_offset = 0). The default is 1.

.. c:var:: octave_offset

    The note-octave notation used in your script, specified as the number of
    octaves between MIDI note number 0 and the note called "C0".
    The default is 2, meaning that "middle C" (note number 60) is named "C3".
    Another typical value is 1, meaning that "middle C" is "C4".

.. c:var:: initial_scene

    The number of the first scene to be activated.

.. c:var:: start_delay

    The number of seconds to wait before sending any MIDI events (i.e.
    switching to the first scene). A small value like 0.5 can be used to give
    tools like qjackctl's patchbay time to connect the ports.
    A value of 0 instructs mididings to wait for the user to press enter.
    The default is None, meaning not to wait at all.


.. _main-functions:

Functions
---------

.. autofunction:: config

    .. code::

        # set some configuration values
        config(
            client_name = 'test',
            out_ports = 2,
            octave_offset = 1,
        )

.. autofunction:: hook

.. autofunction:: run


.. _main-classes:

Classes
-------

.. autoclass:: Scene

.. autoclass:: SceneGroup

.. code::

    # define one scene (song) with 3 subscenes (parts)
    SceneGroup("Example Song", [
        Scene("Intro", intro_patch),
        Scene("Verse", verse_patch),
        Scene("Chorus", chorus_patch),
    ])
