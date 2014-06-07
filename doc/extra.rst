.. currentmodule:: mididings.extra

:tocdepth: 2


.. _extra:

Module :mod:`mididings.extra`
=============================


.. _extra-hooks:

Hooks
-----

Hooks extend the functionality of mididings.
Instances of these classes can be registered using the :func:`~.hook()`
function.


.. autoclass:: MemorizeScene
    :no-members:

.. autoclass:: mididings.extra.inotify.AutoRestart
    :no-members:

    Defined in :mod:`mididings.extra.inotify`.
    Requires `pyinotify <https://github.com/seb-m/pyinotify>`_.

.. autoclass:: mididings.extra.osc.OSCInterface
    :no-members:

    Defined in :mod:`mididings.extra.osc`.
    Requires `pyliblo <http://das.nasophon.de/pyliblo/>`_.



.. _extra-gm:

General MIDI
------------

The :mod:`mididings.extra.gm` module contains constants for program and
controller numbers defined in the General MIDI standard.


Programs
^^^^^^^^

.. hlist::
    :columns: 2

    - ACOUSTIC_GRAND_PIANO
    - BRIGHT_ACOUSTIC_PIANO
    - ELECTRIC_GRAND_PIANO
    - HONKY_TONK_PIANO
    - ELECTRIC_PIANO_1
    - ELECTRIC_PIANO_2
    - HARPSICHORD
    - CLAVINET
    - CELESTA
    - GLOCKENSPIEL
    - MUSIC_BOX
    - VIBRAPHONE
    - MARIMBA
    - XYLOPHONE
    - TUBULAR_BELLS
    - DULCIMER
    - DRAWBAR_ORGAN
    - PERCUSSIVE_ORGAN
    - ROCK_ORGAN
    - CHURCH_ORGAN
    - REED_ORGAN
    - ACCORDION
    - HARMONICA
    - TANGO_ACCORDION
    - ACOUSTIC_GUITAR_NYLON
    - ACOUSTIC_GUITAR_STEEL
    - ELECTRIC_GUITAR_JAZZ
    - ELECTRIC_GUITAR_CLEAN
    - ELECTRIC_GUITAR_MUTED
    - OVERDRIVEN_GUITAR
    - DISTORTION_GUITAR
    - GUITAR_HARMONICS
    - ACOUSTIC_BASS
    - ELECTRIC_BASS_FINGER
    - ELECTRIC_BASS_PICK
    - FRETLESS_BASS
    - SLAP_BASS_1
    - SLAP_BASS_2
    - SYNTH_BASS_1
    - SYNTH_BASS_2
    - VIOLIN
    - VIOLA
    - CELLO
    - CONTRABASS
    - TREMOLO_STRINGS
    - PIZZICATO_STRINGS
    - ORCHESTRAL_HARP
    - TIMPANI
    - STRING_ENSEMBLE_1
    - STRING_ENSEMBLE_2
    - SYNTH_STRINGS_1
    - SYNTH_STRINGS_2
    - CHOIR_AAHS
    - VOICE_OOHS
    - SYNTH_VOICE
    - ORCHESTRA_HIT
    - TRUMPET
    - TROMBONE
    - TUBA
    - MUTED_TRUMPET
    - FRENCH_HORN
    - BRASS_SECTION
    - SYNTHBRASS_1
    - SYNTHBRASS_2
    - SOPRANO_SAX
    - ALTO_SAX
    - TENOR_SAX
    - BARITONE_SAX
    - OBOE
    - ENGLISH_HORN
    - BASSOON
    - CLARINET
    - PICCOLO
    - FLUTE
    - RECORDER
    - PAN_FLUTE
    - BLOWN_BOTTLE
    - SHAKUHACHI
    - WHISTLE
    - OCARINA
    - LEAD_1_SQUARE
    - LEAD_2_SAWTOOTH
    - LEAD_3_CALLIOPE
    - LEAD_4_CHIFF
    - LEAD_5_CHARANG
    - LEAD_6_VOICE
    - LEAD_7_FIFTHS
    - LEAD_8_BASS_LEAD
    - PAD_1_NEW_AGE
    - PAD_2_WARM
    - PAD_3_POLYSYNTH
    - PAD_4_CHOIR
    - PAD_5_BOWED
    - PAD_6_METALLIC
    - PAD_7_HALO
    - PAD_8_SWEEP
    - FX_1_RAIN
    - FX_2_SOUNDTRACK
    - FX_3_CRYSTAL
    - FX_4_ATMOSPHERE
    - FX_5_BRIGHTNESS
    - FX_6_GOBLINS
    - FX_7_ECHOES
    - FX_8_SCI_FI
    - SITAR
    - BANJO
    - SHAMISEN
    - KOTO
    - KALIMBA
    - BAGPIPE
    - FIDDLE
    - SHANAI
    - TINKLE_BELL
    - AGOGO
    - STEEL_DRUMS
    - WOODBLOCK
    - TAIKO_DRUM
    - MELODIC_TOM
    - SYNTH_DRUM
    - REVERSE_CYMBAL
    - GUITAR_FRET_NOISE
    - BREATH_NOISE
    - SEASHORE
    - BIRD_TWEET
    - TELEPHONE_RING
    - HELICOPTER
    - APPLAUSE
    - GUNSHOT


Controllers
^^^^^^^^^^^

.. hlist::
    :columns: 2

    - CTRL_BANK_SELECT_MSB
    - CTRL_MODULATION
    - CTRL_DATA_ENTRY_MSB
    - CTRL_VOLUME
    - CTRL_PAN
    - CTRL_EXPRESSION
    - CTRL_BANK_SELECT_LSB
    - CTRL_DATA_ENTRY_LSB
    - CTRL_SUSTAIN
    - CTRL_PORTAMENTO
    - CTRL_SOSTENUTO
    - CTRL_SOFT_PEDAL
    - CTRL_LEGATO_PEDAL
    - CTRL_NRPN_LSB
    - CTRL_NRPN_MSB
    - CTRL_RPN_LSB
    - CTRL_RPN_MSB
    - CTRL_RESET_ALL_CONTROLLERS
    - CTRL_ALL_NOTES_OFF
