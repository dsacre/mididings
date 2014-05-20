.. currentmodule:: mididings


.. _units-modifiers:

Modifiers
---------

.. autofunction:: Port

.. autofunction:: Channel

.. autofunction:: Transpose

.. autofunction:: Key

.. autofunction:: Velocity

    .. image:: velocity.png
       :alt: velocity

    Within mididings, velocity values may be (temporarily) greater than 127 or
    less than 1. When sending events through a MIDI output port, or by using
    the :func:`Sanitize()` unit, velocities greater than 127 will automatically
    be reduced to 127, and events with a velocity less than 1 will be removed.

    .. code::

        # increase velocity of note-on events, making the keyboard feel softer
        Velocity(curve=1.0)

.. autofunction:: VelocitySlope

    .. image:: velocityslope.png
       :alt: velocity slope

    .. code::

        # apply a velocity slope as seen in the graphic above
        VelocitySlope(notes=('b1','g2','g#3','d4'), offset=(-64, 32, 32, 0))

.. autofunction:: VelocityLimit

.. autofunction:: CtrlMap

    .. code::

        # convert sustain pedal to sostenuto
        CtrlMap(64, 66)

.. autofunction:: CtrlRange

.. autofunction:: CtrlCurve

.. autofunction:: PitchbendRange

    .. code::

        # set up the pitchbend wheel to bend a full octave down, but only
        # one whole step up, assuming the synth is set to a symmetric range of
        # 12 semitones
        PitchbendRange(-12, 2, range=12)
