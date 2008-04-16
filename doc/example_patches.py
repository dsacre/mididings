# example_patches.py - a simple example setup, demonstrating patch switching
#
# This script defines three different patches:
#
# patch 1:  play piano, program 1.
# patch 2:  play organ, transposed one octave down.
# patch 3:  split keyboard at C3. the lower part plays piano, program 4,
#           the upper part plays strings.
#
# It's assumed that the piano is connected to port 1, listening on channel 1.
# Organ and strings are both connected to port 2, with the organ listening on
# channel 7, and the strings listening on channel 13.
#
# Program changes on channel 16 switch between patches.
# All outgoing MIDI events are also printed to stdout.


from mididings import *

config(
    # create two output ports
    out_ports = 2,
)

# define the output ports/channels for all synths
piano = Port(1) >> Channel(1)
organ = Port(2) >> Channel(7)
strings = Port(2) >> Channel(13)

# define the program changes to switch between the two piano sounds, and
# route them to the correct output
piano_1 = ProgChange(1) >> piano
piano_4 = ProgChange(4) >> piano


run_patches(
    patches = {
        # patch 1: switch piano to program 1, then route all MIDI to it
        1: (piano_1, piano),
        # patch 2: transpose one octave down, route all MIDI to organ
        2: Transpose(-12) >> organ,
        # patch 3: switch piano to program 4. split keyboard at C3,
        # route lower part to piano, upper part to strings
        3: (piano_4, KeySplit('c3', piano, strings)),
    },
    # control patch: filter out everything but program changes on channel 16
    control = Filter(PROGRAM) >> ChannelFilter(16) >> PatchSwitch(),
    # preprocessing: filter out program changes, everything else is sent
    # to the patch
    pre = ~Filter(PROGRAM),
    # postprocessing: print all outgoing events
    post = Print('out'),
)
