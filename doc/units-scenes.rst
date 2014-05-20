.. currentmodule:: mididings


.. _units-scene-switch:

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

        # route all events to output 'synth', channel 1, and set the volume to 100
        Output('synth', 1, volume=100)

.. autoclass:: OutputTemplate

    ::

        # define an instrument by specifying its output port, channel, program
        # number and transposition, then use the same instrument in two different
        # patches at different volumes
        synth = Transpose(12) >> OutputTemplate('synth', 1, 42)

        patch1 = synth(64)
        patch2 = synth(127)

        # the above is equivalent to:
        patch1 = Transpose(12) >> Output('synth', 1, 42, 64)
        patch2 = Transpose(12) >> Output('synth', 1, 42, 127)
