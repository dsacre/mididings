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

#ifndef MIDIDINGS_BACKEND_JACK_HH
#define MIDIDINGS_BACKEND_JACK_HH

#include "backend/base.hh"
#include "midi_event.hh"

#include <string>
#include <vector>
#include <queue>

#include <jack/types.h>


namespace mididings {
namespace backend {


/*
 * JACK backend base class.
 */
class JACKBackend
  : public BackendBase
{
  public:
    JACKBackend(std::string const & client_name,
                PortNameVector const & in_port_names,
                PortNameVector const & out_port_names);
    virtual ~JACKBackend();

    virtual std::size_t num_out_ports() const {
        return _out_ports.size();
    }

    virtual void connect_ports(PortConnectionMap const & in_port_connections,
                               PortConnectionMap const & out_port_connections);

  protected:
    // XXX this should be pure virtual.
    // it isn't, because the process thread is started from within the c'tor
    virtual int process(jack_nframes_t) {
        return 0;
    }

    void clear_buffers(jack_nframes_t nframes);
    bool read_event(MidiEvent & ev, jack_nframes_t nframes);
    bool write_event(MidiEvent const & ev, jack_nframes_t nframes);

    jack_client_t *_client;
    std::vector<jack_port_t *> _in_ports;
    std::vector<jack_port_t *> _out_ports;

    jack_nframes_t _current_frame;

  private:
    static int process_(jack_nframes_t nframes, void *arg);

    void fill_input_queue(jack_nframes_t nframes);

    void connect_ports_impl(PortConnectionMap const & port_connections,
                            std::vector<jack_port_t *> const & ports,
                            bool out);
    int connect_matching_ports(std::string const & port_name,
                            std::string const & pattern,
                            PortNameVector const & external_ports,
                            bool out);


    template <typename T, typename Container, typename Compare>
    class reservable_priority_queue
      : public std::priority_queue<T, Container, Compare>
    {
    public:
        typedef typename std::priority_queue<
            T, Container, Compare
        >::size_type size_type;

        reservable_priority_queue(size_type capacity = 0) {
            reserve(capacity);
        };
        void reserve(size_type capacity) {
            this->c.reserve(capacity);
        }
        size_type capacity() const {
            return this->c.capacity();
        }
    };

    struct compare_frame {
        bool operator() (MidiEvent const & lhs, MidiEvent const & rhs) const {
            return lhs.frame > rhs.frame;
        }
    };

    // queue of incoming MIDI events, ordered by frame
    reservable_priority_queue<
        MidiEvent, std::vector<MidiEvent>, compare_frame
    > _input_queue;

    // the frame at which the last event during each period was written
    std::vector<jack_nframes_t> _last_written_frame;
};


} // backend
} // mididings


#endif // MIDIDINGS_BACKEND_JACK_HH
