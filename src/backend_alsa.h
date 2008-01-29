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

#ifndef _BACKEND_ALSA_H
#define _BACKEND_ALSA_H

#include "backend.h"
#include "midi_event.h"

#include <alsa/asoundlib.h>

#include <string>
#include <vector>
#include <map>


class BackendAlsa
  : public Backend
{
  public:
    BackendAlsa(const std::string & client_name,
                int in_ports, int out_ports,
                const std::vector<std::string> & in_portnames,
                const std::vector<std::string> & out_portnames);
    virtual ~BackendAlsa();

    virtual void run(class Setup & setup);

  private:
    MidiEvent alsa_to_midi_event(const snd_seq_event_t & alsa_ev);
    snd_seq_event_t midi_event_to_alsa(const MidiEvent & ev);

    snd_seq_t *_seq_handle;
    std::vector<int> _portid_in;
    std::map<int, int> _portid_in_rev;
    std::vector<int> _portid_out;
};


#endif // _BACKEND_ALSA_H
