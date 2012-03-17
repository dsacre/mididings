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

#ifndef MIDIDINGS_BACKEND_JACK_HH
#define MIDIDINGS_BACKEND_JACK_HH

#include "backend/base.hh"
#include "midi_event.hh"

#include <string>
#include <vector>

#include <jack/types.h>


namespace Mididings {
namespace Backend {


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

    virtual std::size_t num_out_ports() const { return _out_ports.size(); }

    virtual void connect_ports(PortConnectionMap const & in_port_connections,
                               PortConnectionMap const & out_port_connections);

  protected:
    // XXX this should be pure virtual.
    // it isn't, because the process thread is started within the c'tor
    virtual int process(jack_nframes_t) { return 0; } //= 0;

    void clear_buffers(jack_nframes_t nframes);
    bool read_event(MidiEvent & ev, jack_nframes_t nframes);
    bool write_event(MidiEvent const & ev, jack_nframes_t nframes);

    jack_client_t *_client;
    std::vector<jack_port_t *> _in_ports;
    std::vector<jack_port_t *> _out_ports;

    jack_nframes_t _current_frame;

  private:
    static int process_(jack_nframes_t, void *);

    void connect_ports_impl(PortConnectionMap const & port_connections, std::vector<jack_port_t *> const & ports, bool out);
    int connect_matching_ports(std::string const & port_name, std::string const & pattern, PortNameVector const & external_ports, bool out);

    // loop counters used by read_event()
    int _input_port;
    int _input_count;
};


} // Backend
} // Mididings


#endif // MIDIDINGS_BACKEND_JACK_HH
