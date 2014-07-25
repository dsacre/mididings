/*
 * mididings
 *
 * Copyright (C) 2008-2014  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#include "config.hh"
#include "backend/jack_buffered.hh"

#include <jack/jack.h>
#include <jack/thread.h>

#include <algorithm>

#include <boost/version.hpp>

#include "util/debug.hh"


namespace mididings {
namespace backend {


JACKBufferedBackend::JACKBufferedBackend(
        std::string const & client_name,
        PortNameVector const & in_port_names,
        PortNameVector const & out_port_names)
  : JACKBackend(client_name, in_port_names, out_port_names)
  , _in_rb(config::JACK_MAX_EVENTS)
  , _out_rb(config::JACK_MAX_EVENTS)
  , _quit(false)
{
}


void JACKBufferedBackend::start(InitFunction init, CycleFunction cycle)
{
    // clear event buffers
    _in_rb.reset();
    _out_rb.reset();

    _quit = false;

    boost::function<void()> func = boost::bind(
                    &JACKBufferedBackend::process_thread, this, init, cycle);

    // start processing thread
#if BOOST_VERSION >= 105000
    boost::thread::attributes attr;
    attr.set_stack_size(config::JACK_BUFFERED_THREAD_STACK_SIZE);
    _thread.reset(new boost::thread(attr, func));
#else
    _thread.reset(new boost::thread(func));
#endif


    // try to use realtime scheduling for MIDI processing thread
    int jack_rtprio = jack_client_real_time_priority(_client);

    if (jack_rtprio != -1) {
        int rtprio = jack_rtprio - config::JACK_BUFFERED_RTPRIO_OFFSET;
        rtprio = std::max(rtprio, 1);
        jack_acquire_real_time_scheduling(_thread->native_handle(), rtprio);
    }
}


void JACKBufferedBackend::stop()
{
    if (_thread) {
        _quit = true;
        _cond.notify_one();

        _thread->join();
    }
}


void JACKBufferedBackend::process_thread(InitFunction init,
                                         CycleFunction cycle)
{
    init();
    cycle();
}


int JACKBufferedBackend::process(jack_nframes_t nframes)
{
    MidiEvent ev;

    // store all incoming events in the input ringbuffer
    while (read_event(ev, nframes)) {
        if (!_in_rb.write(ev)) {
            DEBUG_PRINT("couldn't write event to input ringbuffer");
        }
        _cond.notify_one();
    }

    // clear all JACK output buffers
    clear_buffers(nframes);

    // read all events from output ringbuffer, write to JACK output buffers
    while (_out_rb.read_space()) {
        _out_rb.read(ev);
        if (!write_event(ev, nframes)) {
            DEBUG_PRINT("couldn't write event to output buffer");
        }
    }

    return 0;
}


bool JACKBufferedBackend::input_event(MidiEvent & ev)
{
    // wait until there are events to be read from the ringbuffer
    while (!_in_rb.read_space()) {
        boost::mutex::scoped_lock lock(_mutex);
        _cond.wait(lock);

        // check for program termination
        if (_quit) {
            return false;
        }
    }

    VERIFY(_in_rb.read(ev));

    return true;
}


void JACKBufferedBackend::output_event(MidiEvent const & ev)
{
    if (!_out_rb.write(ev)) {
        DEBUG_PRINT("couldn't write event to output ringbuffer");
    }
}


} // backend
} // mididings
