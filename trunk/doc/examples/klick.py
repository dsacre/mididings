#
# klick.py - uses SendOSC() to start/stop klick, or change its tempo
#
# klick: http://das.nasophon.de/klick/
#
# CC #14 starts/stops the metronome, CC #15 changes tempo.
#
# For this script to work, run klick listening on OSC port 1234:
# klick -o 1234
#

from mididings import *
from mididings.extra.osc import SendOSC

port = 1234

run(
    Filter(CTRL) >> [
        CtrlFilter(14) >> [
            CtrlValueFilter( 0,  63) >> SendOSC(port, '/klick/metro/stop'),
            CtrlValueFilter(64, 127) >> SendOSC(port, '/klick/metro/start'),
        ],
        CtrlFilter(15) >> SendOSC(port, '/klick/simple/set_tempo', lambda ev: 60 + ev.value)
    ]
    >> Discard()
)
