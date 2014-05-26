.. currentmodule:: mididings

:tocdepth: 2

.. _misc:

Miscellaneous
=============


.. _event-types:

Event Types
-----------

Every event has one of the following types:

+---------------------------+-------------------------------+
| Symbolic constant         | MIDI event type               |
+===========================+===============================+
| :const:`NOTEON`           | Note-on event                 |
+---------------------------+-------------------------------+
| :const:`NOTEOFF`          | Note-off event                |
+---------------------------+-------------------------------+
| :const:`CTRL`             | Control change event          |
+---------------------------+-------------------------------+
| :const:`PROGRAM`          | Program change event          |
+---------------------------+-------------------------------+
| :const:`PITCHBEND`        | Pitchbend event               |
+---------------------------+-------------------------------+
| :const:`AFTERTOUCH`       | Channel aftertouch event      |
+---------------------------+-------------------------------+
| :const:`POLY_AFTERTOUCH`  | Polyphonic aftertouch event   |
+---------------------------+-------------------------------+
| :const:`SYSEX`            | System exclusive event        |
+---------------------------+-------------------------------+
| :const:`SYSCM_QFRAME`     | MTC quarter frame             |
+---------------------------+-------------------------------+
| :const:`SYSCM_SONGPOS`    | Song position pointer         |
+---------------------------+-------------------------------+
| :const:`SYSCM_SONGSEL`    | Song select                   |
+---------------------------+-------------------------------+
| :const:`SYSCM_TUNEREQ`    | Tune request                  |
+---------------------------+-------------------------------+
| :const:`SYSRT_CLOCK`      | Timing clock                  |
+---------------------------+-------------------------------+
| :const:`SYSRT_START`      | Start sequence                |
+---------------------------+-------------------------------+
| :const:`SYSRT_CONTINUE`   | Continue sequence             |
+---------------------------+-------------------------------+
| :const:`SYSRT_STOP`       | Stop sequence                 |
+---------------------------+-------------------------------+
| :const:`SYSRT_SENSING`    | Active sensing                |
+---------------------------+-------------------------------+
| :const:`SYSRT_RESET`      | System reset                  |
+---------------------------+-------------------------------+


For use in filters, the following constants are also defined:

+---------------------------+-------------------------------------------------+
| Symbolic constant         | Matched MIDI event types                        |
+===========================+=================================================+
| :const:`NOTE`             | Any note event                                  |
|                           | (:const:`NOTEON` | :const:`NOTEOFF`)            |
+---------------------------+-------------------------------------------------+
| :const:`SYSCM`            | Any system common event                         |
|                           | (:const:`SYSCM_QFRAME` |                        |
|                           | :const:`SYSCM_SONGPOS` |                        |
|                           | :const:`SYSCM_SONGSEL` |                        |
|                           | :const:`SYSCM_TUNEREQ`)                         |
+---------------------------+-------------------------------------------------+
| :const:`SYSRT`            | Any system realtime event                       |
|                           | (:const:`SYSRT_CLOCK` | :const:`SYSRT_START` |  |
|                           | :const:`SYSRT_CONTINUE` | :const:`SYSRT_STOP` | |
|                           | :const:`SYSRT_SENSING` |                        |
|                           | :const:`SYSRT_RESET`)                           |
+---------------------------+-------------------------------------------------+
| :const:`SYSTEM`           | Any system (non-channel) event                  |
|                           | (:const:`SYSEX` | :const:`SYSCM` |              |
|                           | :const:`SYSRT`)                                 |
+---------------------------+-------------------------------------------------+
| :const:`NONE`             | No event                                        |
+---------------------------+-------------------------------------------------+
| :const:`ANY`              | Any event                                       |
+---------------------------+-------------------------------------------------+


Event types are bit masks, so when building filters, they can be combined
using operators ``|`` (bitwise or) and ``~`` (bitwise negation).


.. _event-attributes:

Event Attributes
----------------

These constants are used by :ref:`units-generators` and the
:func:`SceneSwitch()` unit to refer to an event's data attributes:

+----------------------------+
| Symbolic constant          |
+============================+
| :const:`EVENT_PORT`        |
+----------------------------+
| :const:`EVENT_CHANNEL`     |
+----------------------------+
| :const:`EVENT_DATA1`       |
+----------------------------+
| :const:`EVENT_DATA2`       |
+----------------------------+
| :const:`EVENT_NOTE`        |
+----------------------------+
| :const:`EVENT_VELOCITY`    |
+----------------------------+
| :const:`EVENT_CTRL`        |
+----------------------------+
| :const:`EVENT_VALUE`       |
+----------------------------+
| :const:`EVENT_PROGRAM`     |
+----------------------------+


.. _notes:

Note Names and Ranges
---------------------

Many mididings units accept notes and/or note ranges as parameters.
Notes can be specified either as a MIDI note number or by their name,
consisting of one letter, optionally ``'b'`` or ``'#'``, and an octave number.
Examples of valid note names are ``'c3'``, ``'g#4'``, or ``'eb2'``.

Note ranges can be specified either as a 2-tuple of note numbers or names,
e.g. ``(48, 60)`` or ``('c2', 'c3')``, or as two note names
separated by a colon, e.g. ``'g#3:c6'``.

Like all ranges in Python, note ranges are semi-open (do not include
their upper limit), so ``'g#3:c6'`` matches notes from g#3
up to b5, but not c6.
It's also possible to omit either the upper or the lower limit, for
example ``'c4:'`` matches all notes above (and including) c4,
while ``':a2'`` matches all note up to (but not including) a2.


.. _ports:

Port Names
----------

Internally, ports are always referred to by their number.
For instance, when an event is received on the second input port, and is
not explicitly routed to another port, it will be sent to the second
output port, regardless of port names.

If you named your input and output ports using the :c:data:`in_ports` and
:c:data:`out_ports` parameters to :func:`config()`, you can also refer to
them by their names in all units that accept ports as parameters.

To avoid ambiguities, port names should be unique
(with the JACK backend they must be).



.. _python:

mididings and Python
--------------------

mididings is a little peculiar in the way it uses Python, so here's a couple
of things you might need to know...


.. _overload:

Overloaded Functions
^^^^^^^^^^^^^^^^^^^^

Python does not support overloaded functions per se, but mididings implements
a mechanism that allows functions to have behave differently depending not
only on the number of arguments, but also on the parameters' names.

For example, while ``Velocity(offset=32)`` increases MIDI note velocities
by 32, ``Velocity(fixed=32)`` changes velocities to a fixed value of 32.

When multiple versions of a function accept the same number of parameters,
it's necessary to explicitly name the parameters of the version you'd like
to use. Cases where parameter names are mandatory are indicated in this
documentation by an equal sign followed by an ellipsis,
as in **Velocity**\ *(fixed=...)*.
Most functions also have a "default" version that does not require specifying
the name of any parameter.
In mididings it is usually possible to explicitly name parameters though,
regardless of whether it's actually required for a particular function
invocation.

Other than that, the documentation follows common Python conventions for
the notation of positional arguments, variable arguments and keyword
arguments.


Everything is an Object
^^^^^^^^^^^^^^^^^^^^^^^

Everything in mididings is a Python object, and can be assigned to
variables, returned from functions, etc.::

    # add a fifth (7 semitones) above each note, and route all events
    # to channel 2 (of course there are easier ways to do this)
    def add_interval(n):
        return Pass() // Transpose(n)

    route = Channel(2)
    mypatch = add_interval(7) >> route

    run(mypatch)


Line Break and Indentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

As in any other Python code, line breaks delimit statements, and indentation
delimits blocks.
However, as a rule of thumb, both line breaks and indentation are irrelevant
as long as at least one parenthesis or bracket remains open.

Many mididings patches consist of lists and dictionaries, so line breaks and
indentation may not be an issue, but often it is convenient to put
patches in parentheses in order to allow them to span multiple lines::

    mypatch = (
        Filter(~PROGRAM) >> Print("this line is getting kind of long") >>
        Transpose(12) >> Velocity(curve=1.0)
    )


Operator Precedence
^^^^^^^^^^^^^^^^^^^

Overloading operators in Python can not change their precedence.
This is a list of all operators relevant to mididings, in order of
their precedence (highest to lowest):

+---------------+-----------------------------------+
| Operator      | Meaning in mididings              |
+===============+===================================+
| | (...)       | | Binding (parentheses)           |
| | [A, B, ...] | | Connection in parallel (list)   |
+---------------+-----------------------------------+
| | ~F          | | Filter inversion                |
| | -F          | | Filter negation                 |
| | +F          | | Apply to duplicate              |
+---------------+-----------------------------------+
| | A // B      | | Connection in parallel          |
| | S % A       | | Selector "then"                 |
+---------------+-----------------------------------+
| A >> B        | Connection in series              |
+---------------+-----------------------------------+
| S1 & S2       | Selector "and"                    |
+---------------+-----------------------------------+
| S1 | S2       | Selector "or"                     |
+---------------+-----------------------------------+


In short, remember that...

- parallel connection binds stronger than serial.
- selectors (of more than one filter) must be in parentheses.
- when in doubt, you can always use additional parentheses.

.. note::

    Operator overloading doesn't apply if both sides of the
    operator are builtin Python types like :class:`list` or :class:`dict`.
    In some cases it may be necessary to wrap those in
    :func:`Fork()` or :func:`Split()`.
