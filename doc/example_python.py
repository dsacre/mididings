# example_python.py - shows how to process MIDI events in Python

from mididings import *


# Events on channel 1 are sent to the output, with the velocity
# of note-on events inverted.
# Events on all other channels are discarded.
def process(ev):
    if ev.channel == 1:
        if ev.type_ == NOTEON:
            ev.velocity = 127 - ev.velocity
        return True
    else:
        return False


run(Call(process))
