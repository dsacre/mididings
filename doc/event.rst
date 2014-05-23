.. module:: mididings.event

.. _event:

Module :mod:`mididings.event`
=============================

This module defines classes and functions for dealing with MIDI events in
Python code, e.g. when using :func:`~.Process()` or :func:`~.Call()`.

.. autoclass:: MidiEvent
    :no-members:

    Each event has these attributes:

    .. autoattribute:: type
    .. autoattribute:: port
    .. autoattribute:: channel

    .. attribute:: data1

        The first data byte, meaning depends on event type.

    .. attribute:: data2

        The second data byte, meaning depends on event type.

    The following attributes are only valid for certain event types, and
    accessing them will raise an error otherwise:

    .. autoattribute:: note
    .. autoattribute:: velocity
    .. autoattribute:: ctrl
    .. autoattribute:: value
    .. autoattribute:: program
    .. autoattribute:: sysex


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
