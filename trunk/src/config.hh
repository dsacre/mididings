/*
 * mididings
 *
 * Copyright (C) 2008-2012  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef MIDIDINGS_CONFIG_HH
#define MIDIDINGS_CONFIG_HH

// XXX Python.h must be included before any system header, so let's get this over with.
// this allows us to keep the include order sane everywhere else.
#include <Python.h>

#include <cstring>


namespace Mididings {


namespace Config
{
    // total number of events that can be stored simultaneously in the event list during each process cycle
    static int const MAX_EVENTS = 1024;

    // maximum number of notes that can be remembered in case of a scene switch (so note-offs can be routed accordingly).
    // this is more of a soft limit, additional memory will be allocated if necessary (not RT-safe!)
    static int const MAX_SIMULTANEOUS_NOTES = 64;
    // maximum number of sustain pedal states that can be remembered in case of a scene switch
    static int const MAX_SUSTAIN_PEDALS = 4;

    static int const MAX_ASYNC_CALLS = 256;
    static int const ASYNC_JOIN_TIMEOUT = 3000;
    static int const ASYNC_CALLBACK_INTERVAL = 50;

    static std::size_t const ALSA_SYSEX_CHUNK_SIZE = 256;

    static int const MAX_JACK_EVENTS = 128;
    // maximum size of JACK MIDI events. in reality this depends on the JACK period size...
    static int const MAX_JACK_EVENT_SIZE = 4096;

    // realtime priority offset for buffered JACK backend, subtracted from JACK's own priority
    static int const JACK_BUFFERED_RTPRIO_OFFSET = 10;
}


} // Mididings


#endif // MIDIDINGS_CONFIG_HH
