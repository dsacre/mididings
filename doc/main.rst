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
        in the JACK process callback, with no additional latency.

    The default, if available, is ``'alsa'``.

    .. note::

        Python code is not realtime safe, so it's recommended not to use
        the :func:`Process()` unit in conjunction with the **jack-rt** backend.

        With the buffering **jack** backend, Python code that does not finish
        in time merely causes MIDI events from mididings to be slightly
        delayed.
        With the **jack-rt** backend, it causes xruns which are potentially
        audible, may cause loss of MIDI events, and also affect other JACK
        clients!

        In practice, if you require sample-accurate MIDI processing with
        *zero latency*, but your JACK period size is *large enough*, you can
        often get away with **jack-rt** running Python code in a realtime
        context.
        On the other hand, if your JACK period size is small, the single period
        of delay caused by the buffering **jack** backend is likely to be
        unnoticable.

.. c:var:: client_name

    The ALSA or JACK client name to be used. The default is ``'mididings'``.

.. c:var:: in_ports
           out_ports

    Defines the number and names of input and output ports, and optionally
    external ports to connect them to. The default is one input and one output
    port.

    Possible values are:

    * | Integer: Indicates the number of ports to be created (named ``in_n``
        and ``out_n``, respectively, where ``n`` is the port number).

    * | List of ports:
        Each port is either described by a single string specifying its name,
        or by a list/tuple containing the port name, followed by any number
        of regular expressions specifying ports to connect to.
      | These regular expressions are matched against the full name
        (client:port) of each external port. ALSA clients and ports can
        be referred to using either their names or numbers.

    ::

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

    Determines whether program, port, channel and scene numbers used in your
    script are in the range 1-128 (with data_offset = 1) or 0-127 (with
    data_offset = 0). The default is 1.

.. c:var:: octave_offset

    The note-octave notation used in your script, specified as the number of
    octaves between MIDI note number 0 and the note called "C0".
    The default is 2, meaning that "middle C" (note number 60) is named "C3".
    Another typical value is 1, meaning that "middle C" is "C4".

.. c:var:: initial_scene

    The number of the first scene to be activated. The default is the scene
    with the lowest number.
    Also see :class:`~.extra.MemorizeScene`.

.. c:var:: start_delay

    The number of seconds to wait before sending any MIDI events (i.e.
    switching to the first scene). A small delay like 0.5 s can be used to give
    tools like QjackCtl's patchbay time to connect ports before sending initial
    MIDI events.
    A value of 0 instructs mididings to wait for the user to press enter.
    The default is ``None``, meaning not to wait at all.


.. _main-functions:

Functions
---------

.. autofunction:: config

    ::

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

::

    # define one scene (song) with 3 subscenes (parts)
    SceneGroup("Example Song", [
        Scene("Intro", intro_patch),
        Scene("Verse", verse_patch),
        Scene("Chorus", chorus_patch),
    ])
