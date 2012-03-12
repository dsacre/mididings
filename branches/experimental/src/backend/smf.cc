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

#include "config.hh"
#include "backend/smf.hh"


namespace Mididings {
namespace Backend {


SMFBackend::SMFBackend(std::string const & infile, std::string const & outfile)
  : _outfile(outfile)
{
    smf_t *smf_in = smf_load(infile.c_str());
    if (!smf_in) {
        throw Error("couldn't load input file");
    }
    _smf_in.reset(smf_in, smf_delete);

    _smf_out.reset(smf_new(), smf_delete);

    if (smf_set_ppqn(_smf_out.get(), _smf_in->ppqn)) {
        // can't happen
    }

    for (int n = 1; n <= _smf_in->number_of_tracks; ++n) {
        smf_add_track(_smf_out.get(), smf_track_new());
    }
}


void SMFBackend::start(InitFunction init, CycleFunction cycle)
{
    init();
    cycle();

    if (smf_save(_smf_out.get(), _outfile.c_str())) {
        throw Error("couldn't save output file");
    }
}


bool SMFBackend::input_event(MidiEvent & ev)
{
    while (true)
    {
        smf_event_t *smf_ev = smf_get_next_event(_smf_in.get());

        if (!smf_ev) {
            return false;
        }
        else if (smf_event_is_metadata(smf_ev)) {
            // yuck
            smf_event_t *smf_ev_out = smf_event_new_from_pointer(smf_ev->midi_buffer, smf_ev->midi_buffer_length);
            smf_track_add_event_pulses(smf_get_track_by_number(_smf_out.get(), smf_ev->track_number), smf_ev_out, smf_ev->time_pulses);
        }
        else {
            ev = buffer_to_midi_event(smf_ev->midi_buffer, smf_ev->midi_buffer_length, smf_ev->track_number - 1, smf_ev->time_pulses);
            return true;
        }
    }
}


void SMFBackend::output_event(MidiEvent const & ev)
{
    unsigned char data[3];
    std::size_t len;
    int track;
    uint64_t pulses;

    midi_event_to_buffer(ev, data, len, track, pulses);

    smf_event_t *smf_ev = smf_event_new_from_pointer(data, len);
    smf_track_add_event_pulses(smf_get_track_by_number(_smf_out.get(), track + 1), smf_ev, pulses);
}


} // Backend
} // Mididings
