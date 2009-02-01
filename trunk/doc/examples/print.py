#
# print.py - printing MIDI events to stdout
#

from mididings import *

config(
    in_ports = ['first', 'second'],
    out_ports = ['output'],
)

# prints events as they arrive, performs some processing, then prints them again

run(
    Print('before', portnames=Print.PORTNAMES_IN)
    >> ~Filter(PROGRAM)
    >> VelocityFilter(80, 128)
    >> Channel(3)
    >> Port('output')
    >> Print('after')
)
