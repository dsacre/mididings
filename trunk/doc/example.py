# example.py - a very simple mididings setup
#
# This is a setup with just one input and one output port.
#

from mididings import *

run(
    ChannelSplit({
        # incoming events on channel 1
        1: {
            # send notes and control changes on both channel 1 and channel 2.
            # the output on channel 1 is transposed up one octave
            NOTE | CTRL: [
                    Transpose(12) >> Channel(1),
                    Channel(2),
                ],
            # send program changes to channel 3
            PROGRAM: Channel(3),
            # discard pitch bend events
            PITCHBEND: Discard(),
        },
        # incoming events on channel 2:
        # convert CC #42 to PC messages, send on channel 4.
        # all other events are discarded
        2: CtrlFilter(42) >> ProgChange(EVENT_VALUE) >> Channel(4)
    })
)
