#
# aeolus.py - Aeolus stop control using one controller per stop
#
# Aeolus (http://www.kokkinizita.net/linuxaudio/aeolus/index.html)
# uses CC #98 to enable/disable stops. Changing a stop requires one message
# to select the button group and action, and another to select the button.
#
# This script converts simple CC messages, one CC# per stop, to the format
# expected by Aeolus. CCs 0-56 are mapped to the 57 buttons of the Aeolus
# default instrument. Stops are enabled by controller values >= 64.
#

from mididings import *

def aeolus_button(ctrl, group, button):
    return CtrlFilter(ctrl) >> CtrlValueSplit(64,
        [ Ctrl(98, 0x50 | group), Ctrl(98, button) ],
        [ Ctrl(98, 0x60 | group), Ctrl(98, button) ]
    )

run(
    Filter(CTRL) % (
        [ aeolus_button(     n, 0, n) for n in range(12) ] +
        [ aeolus_button(12 + n, 1, n) for n in range(13) ] +
        [ aeolus_button(25 + n, 2, n) for n in range(16) ] +
        [ aeolus_button(41 + n, 3, n) for n in range(16) ]
    )
)
