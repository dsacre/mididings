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

#include "setup.h"
#include "backend_alsa.h"
#include "util.h"

#include <iostream>

using namespace std;


Setup * TheSetup = NULL;


Setup::Setup(const string & backend_name,
             const string & client_name,
             int in_ports, int out_ports,
             const vector<string> & in_portnames,
             const vector<string> & out_portnames)
  : _current(NULL),
    _noteon_patches(MAX_SIMULTANEOUS_NOTES),
    _event_buffer1(EVENT_BUFFER_SIZE),
    _event_buffer2(EVENT_BUFFER_SIZE),
    _current_output_buffer(NULL)
{
    DEBUG_FN();

    if (backend_name == "alsa") {
        _backend.reset(new BackendAlsa(client_name, in_ports, out_ports, in_portnames, out_portnames));
    }
}


Setup::~Setup()
{
    DEBUG_FN();
}


void Setup::add_patch(int i, PatchPtr patch, PatchPtr init_patch)
{
    ASSERT(_patches.find(i) == _patches.end());

    _patches[i] = patch;
    if (init_patch) {
        _init_patches[i] = init_patch;
    }
}


void Setup::set_processing(PatchPtr ctrl_patch, PatchPtr pre_patch, PatchPtr post_patch)
{
    ASSERT(!_ctrl_patch);
    ASSERT(!_pre_patch);
    ASSERT(!_post_patch);
    _ctrl_patch = ctrl_patch;
    _pre_patch = pre_patch;
    _post_patch = post_patch;
}


void Setup::run()
{
    if (!_backend) return;

    _backend->run(*this);
}


void Setup::switch_patch(int n)
{
    n++; ///////////

    DEBUG_FN();
    DEBUG_PRINT("switching to patch " << n);

    PatchMap::iterator i = _patches.find(n);
    if (i != _patches.end()) {
        _current = &*i->second;

        PatchMap::iterator k = _init_patches.find(n);
        if (k != _init_patches.end()) {
            MidiEvent dummy;
            k->second->process(dummy);
        }
    } else {
        cerr << "no such patch: " << n << endl;
    }
}


const Setup::MidiEventVector & Setup::process(const MidiEvent & ev)
{
    Patch *p = NULL;

    _event_buffer1.clear();

    if (_ctrl_patch) {
//        _current_output_buffer = NULL;
        _current_output_buffer = &_event_buffer1;
        _ctrl_patch->process(ev);
    }

    if (ev.type == MIDI_EVENT_NOTEON) {
        // note on: store current patch
        _noteon_patches.insert(make_pair(make_notekey(ev), _current));
        p = _current;
    }
    else if (ev.type == MIDI_EVENT_NOTEOFF) {
        // note off: retrieve and remove stored patch
        NotePatchMap::iterator i = _noteon_patches.find(make_notekey(ev));
        if (i != _noteon_patches.end()) {
            p = i->second;
            _noteon_patches.erase(i);
        }
    }
    else {
        // anything else: just use current patch
        p = _current;
    }
//    DEBUG_PRINT(p);

    // preprocessing
//    _event_buffer1.clear();
    _current_output_buffer = &_event_buffer1;

    if (_pre_patch) {
        _pre_patch->process(ev);
    } else {
        buffer_event(ev);
    }

    // process patch
    _event_buffer2.clear();
    _current_output_buffer = &_event_buffer2;

    if (p) {
        for (MidiEventVector::const_iterator i = _event_buffer1.begin(); i != _event_buffer1.end(); ++i) {
            p->process(*i);
        }
    }

    // postprocessing
    if (_post_patch) {
        _event_buffer1.clear();
        _current_output_buffer = &_event_buffer1;
        for (MidiEventVector::const_iterator i = _event_buffer2.begin(); i != _event_buffer2.end(); ++i) {
            _post_patch->process(*i);
        }
        return _event_buffer1;
    } else {
        return _event_buffer2;
    }

    _current_output_buffer = NULL;
}
