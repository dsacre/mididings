#
# filters.py - how to use filters
#

from mididings import *


# the first filter allows only note and CC events to pass.
# the second filter is inverted (~), so it allows everything *but* CC events.
#
# since the filters are connected in series, this could of course be written simply as Filter(NOTE).

run(
    Filter(NOTE | CTRL) >> ~Filter(CTRL)
)
