.. module:: mididings.event

.. _event:

Module :mod:`mididings.event`
=============================

This module defines classes and functions for dealing with MIDI events in
Python code, e.g. when using :func:`~.Process()` or :func:`~.Call()`.

.. autoclass:: MidiEvent
    :no-members:

    Each event has these attributes:

    .. attribute:: type

        The event type, one of the :ref:`event-types` constants.

    .. attribute:: port

        The port number.

    .. attribute:: channel

        The channel number.

    .. attribute:: data1

        The first data byte, meaning depends on event type.

    .. attribute:: data2

        The second data byte, meaning depends on event type.

    The following attributes are only valid for certain event types, and
    accessing them will raise an error otherwise:

    .. attribute:: note

        The note number, stored in :attr:`data1`.

    .. attribute:: velocity

        The velocity value, stored in :attr:`data2`.

    .. attribute:: ctrl

        The controller number, stored in :attr:`data1`.

    .. attribute:: value

        The controller value, stored in :attr:`data2`.

    .. attribute:: program

        The program number, stored in :attr:`data2`.
        Unlike :attr:`data2`, this attribute properly observes the
        :c:data:`data_offset` setting.

    .. attribute:: sysex

        SysEx data.


Several utility functions are defined to simplify the creation of
event objects. Each of these functions returns a newly created object of
type :class:`MidiEvent`:

.. autofunction:: NoteOnEvent
.. autofunction:: NoteOffEvent
.. autofunction:: CtrlEvent
.. autofunction:: PitchbendEvent
.. autofunction:: AftertouchEvent
.. autofunction:: PolyAftertouchEvent
.. autofunction:: ProgramEvent
.. autofunction:: SysExEvent
