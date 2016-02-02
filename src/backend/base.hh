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

#ifndef MIDIDINGS_BACKEND_BASE_HH
#define MIDIDINGS_BACKEND_BASE_HH

#include <string>
#include <vector>
#include <map>
#include <stdexcept>
#include <boost/shared_ptr.hpp>
#include <boost/function.hpp>
#include <boost/noncopyable.hpp>

#include "midi_event.hh"


namespace mididings {
namespace backend {


struct Error
  : public std::runtime_error
{
    Error(std::string const & w)
      : std::runtime_error(w)
    {
    }
};


typedef boost::shared_ptr<class BackendBase> BackendPtr;

typedef std::vector<std::string> PortNameVector;
typedef std::map<std::string, std::vector<std::string> > PortConnectionMap;


std::vector<std::string> const & available();

BackendPtr create(
        std::string const & backend_name,
        std::string const & client_name,
        PortNameVector const & in_ports,
        PortNameVector const & out_ports);


// convert normalized MIDI data to one MidiEvent
MidiEvent buffer_to_midi_event(
        unsigned char const *data, std::size_t len,
        int port, uint64_t frame);

// convert MidiEvent object to normalized MIDI data
std::size_t midi_event_to_buffer(
        MidiEvent const & ev, unsigned char *data,
        std::size_t & len, int & port,
        uint64_t & frame);



class BackendBase
  : boost::noncopyable
{
  public:
    typedef boost::function<void()> InitFunction;
    typedef boost::function<void()> CycleFunction;

    BackendBase() { }
    virtual ~BackendBase() { }

    virtual void connect_ports(PortConnectionMap const &,
                               PortConnectionMap const &) { }

    virtual std::string get_actual_client_name() { }

    virtual int get_client_id() { }

    virtual std::string get_client_uuid() { }

    // start MIDI processing, run init function. depending on the backend,
    // cycle may be called once (and not return) or periodically.
    virtual void start(InitFunction init, CycleFunction cycle) = 0;

    // stop MIDI processing.
    virtual void stop() = 0;

    // get one event from input, return true if an event was read.
    // depending on the backend, this may block until an event is available.
    virtual bool input_event(MidiEvent & ev) = 0;

    // send one event to the output.
    virtual void output_event(MidiEvent const & ev) = 0;

    // send multiple events to the output.
    template <typename IterT>
    void output_events(IterT begin, IterT end) {
        for (IterT it = begin; it != end; ++it) {
            output_event(*it);
        }
    }

    // wait for all pending event output to be completed.
    virtual void finish() = 0;

    // return the number of output ports
    virtual std::size_t num_out_ports() const = 0;
};


} // backend
} // mididings


#endif // MIDIDINGS_BACKEND_BASE_HH
