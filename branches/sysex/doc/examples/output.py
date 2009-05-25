#
# output.py - uses the Output() unit to simplify MIDI routing and sending program changes
#
# This script assumes that the folling sound sources are connected to mididings:
#
# - A sampler, connected to the first output port, listening on channel 1.
#   Program 1 is an acoustic piano sound, program 4 is a Rhodes piano.
#
# - A synthesizer, connected to the second output port.
#   On channel 3, program 7, there's an organ sound.
#   On channel 4, there's a string sound (no program change needed).
#
# Program changes on channel 16 switch between patches.
#

from mididings import *


config(
    # create two output ports
    out_ports = ['sampler', 'synth'],
)

piano   = Output('sampler', 1, 1)
rhodes  = Output('sampler', 1, 4)
organ   = Output('synth',   3, 7)
strings = Output('synth',   4)


run_patches(
    patches = {
        # patch 1: play piano.
        # this will switch the sampler to program 1, then route all events to it
        1:  piano,

        # patch 2: play organ, transposed one octave down
        2:  Transpose(-12) >> organ,

        # patch 3: split keyboard at C3, the lower part plays rhodes, the upper part plays strings
        3:  KeySplit('c3', rhodes, strings),
    },

    # control patch: use program changes on channel 16 to switch between patches
    control = Filter(PROGRAM) >> ChannelFilter(16) >> PatchSwitch(),

    # preprocessing: filter out program changes, everything else is sent to the current patch
    pre = ~Filter(PROGRAM),
)
