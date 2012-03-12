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
                std::vector<std::string> const & in_portnames,
                std::vector<std::string> const & out_portnames);
    virtual ~JACKBackend();

    virtual std::size_t num_out_ports() const { return _out_ports.size(); }

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

    // loop counters used by read_event()
    int _input_port;
    int _input_count;
};


} // Backend
} // Mididings


#endif // MIDIDINGS_BACKEND_JACK_HH
