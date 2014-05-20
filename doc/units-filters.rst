.. currentmodule:: mididings


.. _units-filters:

Filters
-------

.. autofunction:: PortFilter

.. autofunction:: ChannelFilter

.. autofunction:: KeyFilter

    .. code::

        # match a note range
        KeyFilter('c1:a3')
        # match anything above middle C (note number 60)
        KeyFilter(lower=60)
        # match individual notes
        KeyFilter(notes=[60, 61, 'c5'])

.. autofunction:: VelocityFilter

.. autofunction:: CtrlFilter

    .. code::

        # remove all sustain pedal messages
        ~CtrlFilter(64)

.. autofunction:: CtrlValueFilter

.. autofunction:: ProgramFilter

.. autofunction:: SysExFilter

    .. code::

        # match SysEx messages starting with 'F0 07 15 42'
        SysExFilter('\xf0\x07\x15\x42')
        # match SysEx messages for Yamaha devices
        SysExFilter(manufacturer=0x43)


For filters which accept an arbitrary number of arguments, each argument may
also be a list or tuple of values. The following filters are equivalent::

    PortFilter(1, 2, 3, 4)
    PortFilter([1, 2, 3, 4])
    PortFilter(1, 2, (3, 4))
