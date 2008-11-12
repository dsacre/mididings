#
# klick.py - uses SendOSC() to start/stop klick, or change its tempo
#
# klick: http://das.nasophon.de/klick/
#
# For this script to work, run klick listening on OSC port 1234
# (klick -o 1234), or use CC 13 to start it
#

from mididings import *
from mididings.extra.osc import SendOSC

port = 1234

run(
    Filter(CTRL) >> CtrlSplit({
        # CC 13: run/terminate klick process
        13: CtrlValueSplit(
                64,
                SendOSC(port, '/klick/quit'),
                System('klick -P -o %d' % port)
            ),
        # CC 14: start/stop playing
        14: CtrlValueSplit(
                64,
                SendOSC(port, '/klick/metro/stop'),
                SendOSC(port, '/klick/metro/start'),
            ),
        # CC 15: change tempo
        15: SendOSC(port, '/klick/simple/set_tempo', lambda ev: 60 + ev.value)
    })
)
