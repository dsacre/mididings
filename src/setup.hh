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

#ifndef _SETUP_HH
#define _SETUP_HH

#include "patch.hh"
#include "backend.hh"

#include <string>
#include <vector>
#include <map>
#include <tr1/unordered_map>
#include <boost/shared_ptr.hpp>

#include "util/global_object.hh"


extern class Setup *TheSetup;


class Setup
  : public das::global_object<Setup, ::TheSetup>
{
  public:
    static const int MAX_SIMULTANEOUS_NOTES = 64;
    static const int MAX_SUSTAIN_PEDALS = 4;
    static const int EVENT_BUFFER_SIZE = 16;

    typedef boost::shared_ptr<Patch> PatchPtr;
    typedef std::map<int, PatchPtr> PatchMap;
    typedef unsigned int EventKey;
    typedef std::tr1::unordered_map<EventKey, Patch *> NotePatchMap;
    typedef std::tr1::unordered_map<EventKey, Patch *> SustainPatchMap;


    typedef std::vector<MidiEvent> MidiEventVector;


    Setup(const std::string & backend_name,
          const std::string & client_name,
          const std::vector<std::string> & in_ports,
          const std::vector<std::string> & out_ports);

    ~Setup();

    void add_patch(int i, PatchPtr patch, PatchPtr init_patch);
    void set_processing(PatchPtr ctrl_patch, PatchPtr pre_patch, PatchPtr post_patch);

    void run();

    void switch_patch(int n, const MidiEvent & ev);

    const MidiEventVector & process(const MidiEvent & ev);


    void buffer_event(const MidiEvent & ev) {
        // this would cause the vector to be resized if it gets larger
        // than EVENT_BUFFER_SIZE -> not realtime safe
        if (_current_output_buffer) {
            _current_output_buffer->push_back(ev);
        }
    }

  protected:
    Patch * get_matching_patch(const MidiEvent & ev);

    static inline EventKey make_notekey(const MidiEvent & ev) {
        return ev.port | ev.channel << 16 | ev.note.note << 24;
    }
    static inline EventKey make_sustainkey(const MidiEvent & ev) {
        return ev.port | ev.channel << 16;
    }

    boost::shared_ptr<Backend> _backend;

    PatchMap _patches;
    PatchMap _init_patches;

    PatchPtr _ctrl_patch;
    PatchPtr _pre_patch;
    PatchPtr _post_patch;

    Patch * _current;

    NotePatchMap _noteon_patches;
    SustainPatchMap _sustain_patches;

    MidiEventVector _event_buffer_pre_out;
    MidiEventVector _event_buffer_patch_out;
    MidiEventVector _event_buffer_final;

    MidiEventVector * _current_output_buffer;
};


#endif // _SETUP_HH
