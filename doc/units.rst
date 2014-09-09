.. currentmodule:: mididings


.. _units:

:mod:`mididings` Units
======================

Units are the basic building blocks from which you can build your mididings
patches.

.. note::

    This document doesn't describe what the documented functions do,
    but rather what the objects they return do.
    For example, the ``Transpose()`` function does not actually
    transpose anything.
    It merely returns an object that, when inserted into a
    patch, will transpose incoming events.


.. _units-filters:

Filters
-------

.. function:: Filter(types, ...)
    :noindex:

    Filter events by type, see :func:`here <Filter()>`.

.. autofunction:: PortFilter

.. autofunction:: ChannelFilter

.. autofunction:: KeyFilter

    ::

        # match a note range
        KeyFilter('c1:a3')
        # match anything above middle C (note number 60)
        KeyFilter(lower=60)
        # match individual notes
        KeyFilter(notes=[60, 61, 'c5'])

.. autofunction:: VelocityFilter

.. autofunction:: CtrlFilter

    ::

        # remove all sustain pedal messages
        ~CtrlFilter(64)

.. autofunction:: CtrlValueFilter

.. autofunction:: ProgramFilter

.. autofunction:: SysExFilter

    ::

        # match SysEx messages starting with 'F0 07 15 42'
        SysExFilter('\xf0\x07\x15\x42')
        # match SysEx messages for Yamaha devices
        SysExFilter(manufacturer=0x43)


For filters which accept an arbitrary number of arguments, each argument may
also be a list or tuple of values. The following filters are equivalent::

    PortFilter(1, 2, 3, 4)
    PortFilter([1, 2, 3, 4])
    PortFilter(1, 2, (3, 4))


.. _units-splits:

Splits
------

.. function:: Split(mapping)
    :noindex:

    Split by event type, see :func:`here <Split()>`.

.. autofunction:: PortSplit

    ::

        config(in_ports = ['keyboard', 'piano', 'footswitch'],
               out_ports = ['synth', 'sampler'])
        ...
        PortSplit({
            'keyboard':   Output('sampler', 1),
            'piano':      Transpose(-12) >> Output('sampler', 2),
            'footswitch': Output('synth', 1),
        })

.. autofunction:: ChannelSplit

.. autofunction:: KeySplit

    ::

        KeySplit('c3', Port('bass'), Port('piano'))

    ::

        KeySplit({
            ':c3':      Port('bass'),
            'c3:a#5':   Port('piano'),
            'a#5:':     Port('strings'),
        })

.. autofunction:: VelocitySplit

.. autofunction:: CtrlSplit

.. autofunction:: CtrlValueSplit

.. autofunction:: ProgramSplit

.. autofunction:: SysExSplit


.. _units-modifiers:

Modifiers
---------

.. autofunction:: Port

    ::

        # route to the second output port
        Port(2)
        # route to the port named 'synth'
        Port('synth')

.. autofunction:: Channel

.. autofunction:: Transpose

.. autofunction:: Key

.. autofunction:: Velocity

    .. image:: velocity.png
       :alt: velocity

    Within mididings, velocity values may be (temporarily) greater than 127 or
    less than 1. When sending events through a MIDI output port, or by using
    the :func:`Sanitize()` unit, velocities greater than 127 will automatically
    be reduced to 127, and events with a velocity less than 1 will be removed.

    ::

        # reduce velocity of note-on events by an offset
        Velocity(-20)
        # increase velocity of note-on events by applying a curve
        Velocity(curve=1.0)

.. autofunction:: VelocitySlope

    .. image:: velocityslope.png
       :alt: velocity slope

    ::

        # apply a velocity slope as seen in the graphic above
        VelocitySlope(notes=('b1','g2','g#3','d4'), offset=(-64, 32, 32, 0))

.. autofunction:: VelocityLimit

    ::

        # limit velocity values to a maximum of 100
        VelocityLimit(max=100)

.. autofunction:: CtrlMap

    ::

        # convert sustain pedal to sostenuto
        CtrlMap(64, 66)

.. autofunction:: CtrlRange

    .. image:: ctrlrange.png
        :alt: ctrlrange

    ::

        # invert controller 11
        CtrlRange(11, 127, 0)

.. autofunction:: CtrlCurve

.. autofunction:: PitchbendRange

    ::

        # set up the pitchbend wheel to bend a full octave down, but only
        # one whole step up, assuming the synth is set to a symmetric range of
        # 12 semitones
        PitchbendRange(-12, 2, range=12)


.. _units-generators:

Generators
----------

Generators change the type of an event, either generating an entirely new
event, or retaining some attributes of the original event.

If the *port* and *channel* arguments are omitted for any of these
generators, the values are retained from the incoming event.
To reuse other values, one of the :ref:`Event Attribute <event-attributes>`
constants can be used in place of any parameter.

.. autofunction:: NoteOn

.. autofunction:: NoteOff

.. autofunction:: Ctrl

    ::

        # convert aftertouch to CC #1 (modulation)
        Filter(AFTERTOUCH) % Ctrl(1, EVENT_VALUE)

.. autofunction:: Pitchbend

.. autofunction:: Aftertouch

.. autofunction:: PolyAftertouch

.. autofunction:: Program

.. autofunction:: SysEx

    ::

        # binary string notation
        SysEx('\xf0\x04\x08\x15\x16\x23\x42\xf7')
        # ASCII string notation
        SysEx('F0 04 08 15 16 23 42 F7')
        # list notation
        SysEx([0xf0, 0x04, 0x08, 0x15, 0x16, 0x23, 0x42, 0xf7])
        # sysex message read from a file
        SysEx(open('example.syx').read())

.. autofunction:: Generator


.. _units-call:

Function Calls
--------------

.. autofunction:: Process

    ::

        # invert velocities of all note-on events
        def invert_velocity(ev):
            if ev.type == NOTEON:
                ev.velocity = 128 - ev.velocity
            return ev

        run(Process(invert_velocity))

.. autofunction:: Call

.. autofunction:: System


.. _units-scenes:

Scene Switching
---------------

.. autofunction:: SceneSwitch

    ::

        # switch scenes based on incoming program change messages
        Filter(PROGRAM) >> SceneSwitch()

.. autofunction:: SubSceneSwitch

    ::

        # switch to the next subscene when C1 is pressed
        Filter(NOTEON) >> KeyFilter('c1') >> SubSceneSwitch(1)

.. autofunction:: Init

    Most of the time it's more convenient to create a :class:`Scene` object
    with an explicit init patch, or to use :func:`Output()`, rather than
    using :func:`Init()` directly.

.. autofunction:: Exit

.. autofunction:: Output

    ::

        # route all events to output 'synth', channel 1, and set volume to 100
        Output('synth', 1, volume=100)

.. autoclass:: OutputTemplate

    ::

        # define an instrument by specifying its output port, channel,
        # program number and transposition, then use the same instrument
        # in two different patches at different volumes
        synth = Transpose(12) >> OutputTemplate('synth', 1, 42)

        patch1 = synth(64)
        patch2 = synth(127)

        # the above is equivalent to:
        patch1 = Transpose(12) >> Output('synth', 1, 42, 64)
        patch2 = Transpose(12) >> Output('synth', 1, 42, 127)


.. _units-misc:

Miscellaneous
-------------

.. autofunction:: Print

    ::

        # a simple command-line MIDI event monitor
        $ mididings "Print()"

    ::

        # print a graph of note-on velocities
        Filter(NOTEON) % Print(string=lambda ev: '#' * ev.velocity)

.. autofunction:: Pass

.. autofunction:: Discard

.. autofunction:: Sanitize
