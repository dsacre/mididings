#
# router.py - A simple OSC-controlled MIDI router that sends all incoming
# events to the output port/channel determined by the current scene/subscene.
#
# To route the output to a different MIDI port/channel, send an OSC message
# /mididings/switch_scene <port> <channel>
# to UDP port 56418.
#
# For example, using the send_osc command from pyliblo:
# $ send_osc 56418 /mididings/switch_scene 13 1
#

from mididings import *
from mididings.extra.osc import OSCInterface

NPORTS = 16

config(
    out_ports=NPORTS,
)

hook(
    OSCInterface(56418, 56419),
)

# return a list of 16 scenes, each routing to a different channel on the
# specified port
def routing_channels(port):
    return [
        Scene("Channel %d" % c, Port(port) >> Channel(c))
        for c in range(1, 17)
    ]

# return a dict with one scene group per port, each containing 16 scenes
def routing_ports():
    return dict(
        (p, SceneGroup("Port %d" % p, routing_channels(p)))
        for p in range(1, NPORTS + 1)
    )

run(
    scenes=routing_ports()
)
