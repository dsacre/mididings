.. currentmodule:: mididings


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

        # send a SysEx message read from a file
        SysEx(open('example.syx').read())

.. autofunction:: Generator
