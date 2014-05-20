.. currentmodule:: mididings


.. _units-call:

Function Calls
--------------

.. autofunction:: Process

    .. code::

        # invert velocities of all note-on events
        def invert_velocity(ev):
            if ev.type == NOTEON:
                ev.velocity = 128 - ev.velocity
            return ev

        run(Process(invert_velocity))

.. autofunction:: Call

.. autofunction:: System
