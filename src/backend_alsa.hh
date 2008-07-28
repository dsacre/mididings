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

#ifndef _BACKEND_ALSA_HH
#define _BACKEND_ALSA_HH

#include "backend.hh"

#include <alsa/asoundlib.h>

#include <string>
#include <vector>
#include <map>


class BackendAlsa
  : public Backend
{
  public:
    BackendAlsa(const std::string & client_name,
                const std::vector<std::string> & in_ports,
                const std::vector<std::string> & out_ports);
    virtual ~BackendAlsa();

//    virtual void run(class Engine & engine);

    virtual bool get_event(MidiEvent & ev);
    virtual void output_event(MidiEvent const & ev);
    virtual void flush_output();

  private:
    MidiEvent alsa_to_midi_event(const snd_seq_event_t & alsa_ev);
    snd_seq_event_t midi_event_to_alsa(const MidiEvent & ev);

    snd_seq_t *_seq_handle;
    std::vector<int> _portid_in;        // alsa input port ids
    std::map<int, int> _portid_in_rev;  // reverse mapping (port id -> port #)
    std::vector<int> _portid_out;       // alsa output port ids
};


#endif // _BACKEND_ALSA_HH
