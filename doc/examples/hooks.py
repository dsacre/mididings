#
# hooks.py - demonstrates the use of hooks extending mididings' functionality.
#

from mididings import *
from mididings.extra.osc import OSCInterface
from mididings.extra.inotify import AutoRestart
from mididings.extra import MemorizeScene

config(
    out_ports = 2,
)

hook(
    # OSC interface: sending the message /mididings/switch_scene with a scene
    # number as a parameter to port 5678 switches scenes
    OSCInterface(5678),
    # auto-restart: edit and save this file in a text editor while it's
    # running, and mididings will automatically restart itself (!)
    AutoRestart(),
    # memorize scene: every time this script is restarted, it automatically
    # comes back with the previously active scene
    MemorizeScene('scene.txt')
)

run(
    scenes = {
        # scene 1: route everything to the first output port
        1:  Port(1),

        # scene 2: route everything to the second output port
        2:  Port(2),
    },
)

