.. currentmodule:: mididings


.. _connect:

Connections
===========

Serial and Parallel
-------------------

.. dingsfun:: A >> B <Chain>
              Chain(units)

    Connect units in series. ``A >> B`` is equivalent to ``Chain([A, B])``.

    Incoming MIDI events will be processed by unit **A** first, then by unit
    **B**.  If an event is filtered out by unit **A**,
    it is not processed any further, and unit **B** will not be called. ::

        # transpose one octave down, then set channel to 1
        Transpose(-12) >> Channel(1)


.. dingsfun:: [ A, B, ... ] <Fork>
              A // B <Fork>
              Fork(units, remove_duplicates=True)

    Connect units in parallel. ``[ A, B ]`` is equivalent to ``A // B`` and
    ``Fork([A, B])``.
    All units will be called with identical copies of incoming MIDI events.
    The output will be the sum of all the units' outputs. ::

        # send events to both channels 1 and 2
        [ Channel(1), Channel(2) ]
        # or:
        Channel(1) // Channel(2)

.. dingsfun:: +A <Unit.add>
              A.add() <Unit.add>

    Apply **A** to a duplicate of each event and leave the original unchanged.
    This is a shortcut for ``[ Pass(), A ]``.


Units are always called in the order they appear in a patch, using a
"breadth-first" approach. For example, given the patch ::

    Fork([ Port('foo'), Port('bar') ]) >> Fork([ Channel(1), Channel(2) ])

``Port('foo')`` will be called before ``Port('bar')``, and the two events
produced by the first :func:`Fork()` are then passed on to the second
:func:`Fork()` individually.
The four events resulting from this patch are thus emitted in the order
'foo 1', 'foo 2', 'bar 1', 'bar 2'.

Normally, mididings automatically removes identical events that are
the immediate result of units being connected in parallel. For example,
while ``[Pass(), Transpose(12)]`` results in two different events for each
incoming note-on or note-off event, it does not produce duplicate
controller or program change events, although both :func:`Pass()` and
:func:`Transpose()` leave those events entirely unchanged.
With :func:`Fork()` it is also possible to disable the automatic removal
of identical MIDI events by setting *remove_duplicates* to ``False``.


Filtering and Splitting
-----------------------

.. dingsfun:: Filter(types, ...)

    Filter by event type. Types are represented by the constants described
    in section :ref:`event-types`.
    Multiple types can be combined as bit masks, or given as lists or as
    separate parameters. ::

        # allow only program and control changes to go through
        Filter(PROGRAM, CTRL)
        # these are equivalent:
        Filter(PROGRAM|CTRL)
        Filter([PROGRAM, CTRL])

    See section :ref:`units-filters` for units that allow filtering by
    different event properties.

.. dingsfun:: ~F <Filter.invert>
              F.invert() <Filter.invert>

    Invert the filter **F**. Note that for filters which only affect certain
    kinds of events, other events will remain unaffected when the filter is
    inverted.
    For example, an inverted :func:`KeyFilter()` will match a different note
    range, but neither the original nor the inverted filter will have any
    effect on controllers or program changes. ::

        # remove CC events with controller number 42
        ~CtrlFilter(42)

.. dingsfun:: -F <Filter.negate>
              F.negate() <Filter.negate>

    Negate the filter **F**. Unlike ``~F``, this matches exactly the events
    that **F** doesn't.


.. dingsfun:: { T1: A, T2: B, ... } <Split>
              Split(mapping)

    Split by event type. ``{ t1: a, t2: b }`` is equivalent to
    ``Split({ T1: A, T2: B, ... })``, and both are merely a shorter way of
    saying ``[ Filter(T1) >> A, Filter(T2) >> B ]``. ::

        # send note events to channel 1 and CC events to channel 2
        { NOTE: Channel(1), CTRL: Channel(2) }

    See section :ref:`units-splits` for units that allow splitting by different
    event properties.


    All split units are just combinations of multiple filters of the same
    type.
    Tuples can be used to pass multiple arguments to a split's underlying
    filters (lists won't work, as they are not hashable and thus can't be
    used as keys in a dictionary).
    In addition to any filter arguments, splits also allow ``None`` to be
    used as a key. This acts as an ``else`` clause that is executed when
    none of the other conditions match::

        ChannelSplit({
            1:      ...,    # if channel == 1
            (2, 3): ...,    # if channel == 2 or channel == 3
            None:   ...,    # else
        })


Selective Processing
--------------------

Every filter can act as a selector that restricts some processing steps to
certain events:

.. dingsfun:: S % A <Selector.apply>
              S.apply(A) <Selector.apply>

    Apply **A** only to events which match selector **S**, and leave events
    which don't unchanged.
    If **S** is a single filter, this is equivalent to ``[ S >> A, -S ]``. ::

        # transpose only events on channel 2
        ChannelFilter(2) % Transpose(3)

.. dingsfun:: S % (A, B) <Selector.apply>
              S.apply(A, B) <Selector.apply>

    Apply **A** to events which match selector **S**, and **B** to events
    which don't. ::

        # change notes between C3 and C5 to channel 1,
        # and all other notes to channel 2:
        KeyFilter('c3:c5') % (Channel(1), Channel(2))

Multiple filters can be combined into more complex selectors:

.. dingsfun:: (S1 & S2 & ...) <AndSelector>
              And(conditions)

    Build a selector for events that match all of the given filters or
    selectors. ``(S1 & S2)`` is equivalent to ``And([S1, S2])``.

.. dingsfun:: (S1 | S2 | ...) <OrSelector>
              Or(conditions)

    Build a selector for events that match at least one of the given filters
    or selectors. ``(S1 | S2)`` is equivalent to ``Or([S1, S2])``. ::

        # change controllers 23 and 42 on channel 1 to channel 2:
        (ChannelFilter(1) & (CtrlFilter(23) | CtrlFilter(42))) % Channel(2)
