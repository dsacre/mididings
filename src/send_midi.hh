/*
 * mididings
 *
 * Copyright (C) 2013-2014  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef MIDIDINGS_SEND_MIDI_HH
#define MIDIDINGS_SEND_MIDI_HH

#include "backend/base.hh"

#include <string>
#include <vector>


namespace mididings {


void send_midi(std::string const & backend_name,
               std::string const & dest_port,
               std::vector<MidiEvent> const & events);


} // mididings


#endif // MIDIDINGS_SEND_MIDI_HH
