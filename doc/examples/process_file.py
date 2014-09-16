#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# process_file.py
#
"""Shows how to process a standard MIDI file (SMF).

The input file is read in, the MIDI events are sent through the mididings
patch, and its output is written to a new file.

Replace the patch definition with your processing chain of mididings units.
It takes the same form as a patch passed to the ``mididings.run`` function.

Run the script from the command line like this::

    python process_file.py <infile.mid> <outfile.mid>

.. note:: The pysmf_ module needs to be installed to run this script.


.. _pysmf: http://das.nasophon.de/pysmf/

"""

import sys

from mididings import KeyFilter, process_file

if len(sys.argv) >= 3:
    infile = sys.argv[1]
    outfile = sys.argv[2]
else:
    print("Usage: %s <infile.mid> <outfile.mid>" % sys.argv[0])
    sys.exit(1)

# only let through notes C3 - G8
# other types of events are passed through unchanged
patch = KeyFilter(60, 127)

process_file(infile, outfile, patch)
