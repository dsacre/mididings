.. module:: mididings.extra


.. _extra-units:

:mod:`mididings.extra` Units
============================

These units offer some more advanced/specific functionality than what's
provided in the core mididings module.
Unless otherwise noted, they are made available by importing the
:mod:`mididings.extra` module.

.. note::

    Some of these units are implemented in Python using :func:`~.Process()`,
    and are thus not safe to use with the ``jack-rt`` backend.


.. _extra-voicing:

Voicing
-------

.. autofunction:: Harmonize

    ::

        # add a third above each note, based on the C# harmonic minor scale
        Harmonize('c#', 'minor_harmonic', ['unison', 'third'])

.. autofunction:: VoiceFilter

.. autofunction:: VoiceSplit

    ::

        #route up to three voices to different channels
        VoiceSplit([Channel(1), Channel(2), Channel(3)])

.. autofunction:: LimitPolyphony

.. autofunction:: MakeMonophonic


.. _extra-splits:

Splits
------

.. autofunction:: FloatingKeySplit

    ::

        # split the keyboard somewhere between C2 and C3
        FloatingKeySplit('c2', 'c3', Channel(1), Channel(2))


.. _extra-util:

Utilities
---------

.. autofunction:: PedalToNoteoff

.. autofunction:: LatchNotes

.. autofunction:: SuppressPC

.. autofunction:: KeyColorFilter

.. autofunction:: CtrlToSysEx

.. autofunction:: Panic

.. autofunction:: Restart

.. autofunction:: Quit


.. _extra_message:

Messaging
---------

.. autofunction:: mididings.extra.osc.SendOSC

    Defined in :mod:`mididings.extra.osc`.
    Requires `pyliblo <http://das.nasophon.de/pyliblo/>`_.

.. autofunction:: mididings.extra.dbus.SendDBUS

    Defined in :mod:`mididings.extra.dbus`.
    Requires dbus-python.

    ::

        # change FFADO output volume using a MIDI controller
        CtrlFilter(42) >> SendDBUS(
            'org.ffado.Control',
            '/org/ffado/Control/DeviceManager/%s/Mixer/OUT0Gain' % DEVICEID,
            'org.ffado.Control.Element.Continuous',
            'setValue',
            lambda ev: ev.value * (2**17)
        )
