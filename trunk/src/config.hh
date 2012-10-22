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

// XXX Python.h must be included before any system header, so let's get this
// over with. this allows us to keep the include order sane everywhere else.
#include <Python.h>

#include <cstring>


namespace Mididings {


namespace Config
{
    // Total number of events that can be stored simultaneously in the event
    // list during each process cycle
    static std::size_t const MAX_EVENTS = 1024;

    // Maximum number of notes that can be remembered in case of a scene switch
    // (so note-offs can be routed accordingly). This is more of a soft limit,
    // additional memory will be allocated if necessary (but not RT-safe!)
    static std::size_t const MAX_SIMULTANEOUS_NOTES = 64;
    // Maximum number of sustain pedal states that can be remembered in case
    // of a scene switch
    static std::size_t const MAX_SUSTAIN_PEDALS = 4;

    // Stack size of the asynchronous Python caller thread
    static std::size_t const ASYNC_THREAD_STACK_SIZE = 262144;
    // Maximum number of asynchronous calls that can be queued
    static std::size_t const MAX_ASYNC_CALLS = 256;
    // Time in milliseconds to wait for the async thread to exit on engine
    // shutdown
    static int const ASYNC_JOIN_TIMEOUT = 3000;
    // Maximum time in milliseconds for which the async thread can be idle.
    static int const ASYNC_CALLBACK_INTERVAL = 50;

    // Maximum number of bytes that may be sent to ALSA at once
    static std::size_t const ALSA_SYSEX_CHUNK_SIZE = 256;

    // Size of the JACK backend's input and output queues
    static std::size_t const JACK_MAX_EVENTS = 128;
    // Maximum size of JACK MIDI events. in reality this depends on the JACK
    // period size...
    static std::size_t const JACK_MAX_EVENT_SIZE = 4096;

    // Realtime priority offset for buffered JACK backend, subtracted from
    // JACK's own priority
    static int const JACK_BUFFERED_RTPRIO_OFFSET = 10;
    // Stack size of the processing thread in the buffered JACK backend
    static std::size_t const JACK_BUFFERED_THREAD_STACK_SIZE = 262144;
}


} // Mididings


#endif // MIDIDINGS_CONFIG_HH
