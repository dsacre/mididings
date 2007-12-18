/*
 * mididings
 *
 * Copyright (C) 2007  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef _SETUP_H
#define _SETUP_H

#include "patch.h"
#include "backend.h"

#include <string>
#include <vector>
#include <map>
#include <tr1/unordered_map>
#include <boost/shared_ptr.hpp>

#include "util.h"


extern class Setup *TheSetup;


class Setup
  : public global_object<Setup, ::TheSetup>
{
  public:
    static const int MAX_SIMULTANEOUS_NOTES = 64;
    static const int EVENT_BUFFER_SIZE = 16;

    typedef boost::shared_ptr<Patch> PatchPtr;
    typedef std::map<int, PatchPtr> PatchMap;
    typedef unsigned int NoteKey;
    typedef std::tr1::unordered_map<NoteKey, Patch *> NotePatchMap;

    typedef std::vector<MidiEvent> MidiEventVector;


    Setup(const std::string & backend_name,
          const std::string & client_name,
          int in_ports, int out_ports,
          const std::vector<std::string> & in_portnames,
          const std::vector<std::string> & out_portnames);

    ~Setup();

    void add_patch(int i, PatchPtr patch, PatchPtr init_patch);
    void set_processing(PatchPtr ctrl_patch, PatchPtr pre_patch, PatchPtr post_patch);

    void run();

    void switch_patch(int n);

    const MidiEventVector & process(const MidiEvent & ev);


    void buffer_event(const MidiEvent & ev) {
//        ASSERT(_current_output_buffer);
        // this would cause the vector to be resized if it gets larger
        // than EVENT_BUFFER_SIZE -> not realtime safe
        if (_current_output_buffer)
            _current_output_buffer->push_back(ev);
    }

  protected:
    static inline NoteKey make_notekey(const MidiEvent & ev) {
        return ev.port | ev.channel << 16 | ev.note.note << 24;
    }


    boost::shared_ptr<Backend> _backend;

    PatchMap _patches;
    PatchMap _init_patches;

    PatchPtr _ctrl_patch;
    PatchPtr _pre_patch;
    PatchPtr _post_patch;

    Patch * _current;

    NotePatchMap _noteon_patches;

    MidiEventVector _event_buffer1;
    MidiEventVector _event_buffer2;

    MidiEventVector * _current_output_buffer;
};


#endif // _SETUP_H
