#
# connections.py - how to connect units in series or in parallel,
# and how to split by event type or channel
#

from mididings import *

config(
    out_ports = 2
)


run(
    ChannelSplit({
        # for events arriving on channel 1:
        # - add a second voice one octave above the original note.
        # - route all events to port 2.
        1:  [ Pass(), Transpose(12) ] >> Port(2),

        # for events arriving on channel 2:
        # - increase velocity of note events, route them to port 1, channel 1.
        # - route CC events to port 1, channel 3.
        # - ignore all other events.
        2: {
            NOTE:   Velocity(20) >> Port(1) >> Channel(1),
            CTRL:   Port(1) >> Channel(3)
        }
    })
)
