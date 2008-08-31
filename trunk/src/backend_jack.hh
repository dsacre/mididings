/*
 * mididings
 *
 * Copyright (C) 2008  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef _BACKEND_JACK_HH
#define _BACKEND_JACK_HH

#include "backend.hh"
#include "midi_event.hh"

#include <string>
#include <vector>

#include <boost/thread/condition.hpp>
#include <boost/thread/mutex.hpp>

#include <jack/types.h>
#include <jack/midiport.h>

#include "util/ringbuffer.hh"


class BackendJack
  : public Backend
{
  public:
    BackendJack(std::string const & client_name,
                std::vector<std::string> const & in_portnames,
                std::vector<std::string> const & out_portnames);
    virtual ~BackendJack();

    virtual void input_event(MidiEvent & ev);
    virtual void output_event(MidiEvent const & ev);
    virtual void drop_input();
    virtual void flush_output();

  private:
    int process(jack_nframes_t);

    static int process_(jack_nframes_t, void *);

    MidiEvent jack_to_midi_event(jack_midi_event_t const & jack_ev, int port);
    void midi_event_to_jack(MidiEvent const & ev, unsigned char *data, std::size_t & len, int & port);

    jack_client_t *_client;
    std::vector<jack_port_t *> _in_ports;
    std::vector<jack_port_t *> _out_ports;

    das::ringbuffer<MidiEvent> _in_rb;
    das::ringbuffer<MidiEvent> _out_rb;

    boost::condition _cond;
    boost::mutex _mutex;
};


#endif // _BACKEND_JACK_HH
