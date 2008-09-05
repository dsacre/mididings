#
# harmonizer.py - example usage of the diatonic harmonizer
#

from mididings import *
from mididings.extra import Harmonize


# add a third above each note, based on the C# harmonic minor scale
run(
    Harmonize('c#', 'minor_harmonic', ['unison', 'third'])
)
