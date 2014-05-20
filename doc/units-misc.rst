.. currentmodule:: mididings


.. _units-misc:

Miscellaneous
-------------

.. autofunction:: Print

    .. code::

        # a simple command-line MIDI event monitor
        $ mididings "Print()"

    .. code::

        # print a graph of note-on velocities
        Filter(NOTEON) % Print(string=lambda ev: '#' * ev.velocity)

.. autofunction:: Pass

.. autofunction:: Discard

.. autofunction:: Sanitize
