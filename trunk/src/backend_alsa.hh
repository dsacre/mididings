/*
 * mididings
 *
 * Copyright (C) 2008-2009  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef _BACKEND_ALSA_HH
#define _BACKEND_ALSA_HH

#include "backend.hh"

#include <alsa/asoundlib.h>

#include <string>
#include <vector>
#include <map>
#include <boost/scoped_ptr.hpp>
#include <boost/thread/thread.hpp>


class BackendAlsa
  : public Backend
{
  public:
    BackendAlsa(std::string const & client_name,
                std::vector<std::string> const & in_ports,
                std::vector<std::string> const & out_ports);
    virtual ~BackendAlsa();

    virtual void start(InitFunction init, CycleFunction cycle);

    virtual bool input_event(MidiEvent & ev);
    virtual void output_event(MidiEvent const & ev);
    virtual void flush_output();

    virtual std::size_t num_out_ports() const { return _portid_out.size(); }

  private:
    MidiEvent alsa_to_midi_event(snd_seq_event_t const & alsa_ev);
    snd_seq_event_t midi_event_to_alsa(MidiEvent const & ev);

    void terminate_thread();

    snd_seq_t *_seq;
    std::vector<int> _portid_in;        // alsa input port ids
    std::map<int, int> _portid_in_rev;  // reverse mapping (port id -> port #)
    std::vector<int> _portid_out;       // alsa output port ids

    snd_midi_event_t *_parser;

    boost::scoped_ptr<boost::thread> _thrd;
};


#endif // _BACKEND_ALSA_HH
