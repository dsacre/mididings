.. currentmodule:: mididings


.. _units-splits:

Splits
------

Splits are combinations of multiple filters of the same type. This::

    KeySplit({
        note_range: patch,
        ...
    })

is roughly equivalent to::

    Fork([
        KeyFilter(note_range) >> patch,
        ...
    ])

Tuples can be used to pass multiple arguments to a split's underlying filters
(lists won't work, as they are not hashable and can't be used as keys in a
dictionary).
In addition to the appropriate filter parameters, all splits with dictionary
arguments also allow ``None`` to be used as a key. This acts as an ``else``
clause that is executed when none of the other conditions match::

    ChannelSplit({
        1:      ...,    # if channel == 1
        (2, 3): ...,    # if channel == 2 or channel == 3
        None:   ...,    # else
    })

.. function:: Split(mapping)
    :noindex:

    Split by event type, see :func:`here <Split()>`.

.. autofunction:: PortSplit

.. autofunction:: ChannelSplit

.. autofunction:: KeySplit

.. autofunction:: VelocitySplit

.. autofunction:: CtrlSplit

.. autofunction:: CtrlValueSplit

.. autofunction:: ProgramSplit

.. autofunction:: SysExSplit
