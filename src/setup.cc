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

#include "setup.hh"
#include "backend_alsa.hh"
#include "util/debug.hh"

//#include <iostream>
//#include <sys/time.h>
//#include <time.h>

using namespace std;


Setup * TheSetup = NULL;


Setup::Setup(const string & backend_name,
             const string & client_name,
             const vector<string> & in_ports,
             const vector<string> & out_ports)
  : _current(NULL),
    _noteon_patches(MAX_SIMULTANEOUS_NOTES),
    _sustain_patches(MAX_SUSTAIN_PEDALS),
    _event_buffer_pre_out(EVENT_BUFFER_SIZE),
    _event_buffer_patch_out(EVENT_BUFFER_SIZE),
    _event_buffer_final(EVENT_BUFFER_SIZE),
    _current_output_buffer(NULL)
{
    DEBUG_FN();

    if (backend_name == "alsa") {
        _backend.reset(new BackendAlsa(client_name, in_ports, out_ports));
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
    if (!_backend) {
        return;
    }

    _backend->run(*this);
}


void Setup::switch_patch(int n, const MidiEvent & ev)
{
//    DEBUG_PRINT("switching to patch " << n);

    PatchMap::iterator i = _patches.find(n);
    if (i != _patches.end()) {
        _current = &*i->second;

        PatchMap::iterator k = _init_patches.find(n);
        if (k != _init_patches.end()) {
            // temporarily redirect output to patch_out so events will go through postprocessing
            MidiEventVector *p = _current_output_buffer;
            _current_output_buffer = &_event_buffer_patch_out;

            k->second->process(ev);

            _current_output_buffer = p;
        }
//    } else {
//        cerr << "no such patch: " << n << endl;
    }
}


const Setup::MidiEventVector & Setup::process(const MidiEvent & ev)
{
//    timeval tv1, tv2;
//    gettimeofday(&tv1, NULL);

    // clear all buffers
    _event_buffer_pre_out.clear();
    _event_buffer_patch_out.clear();
    _event_buffer_final.clear();

    if (_ctrl_patch) {
        // all output events are written to the final buffer,
        // and will not be processed any further
        _current_output_buffer = &_event_buffer_final;
        _ctrl_patch->process(ev);
    }

//    DEBUG_PRINT(p);

    // preprocessing, write events to intermediate buffer
    _current_output_buffer = &_event_buffer_pre_out;

    if (_pre_patch) {
        _pre_patch->process(ev);
    } else {
        buffer_event(ev);
    }

    // process patch, write events to another buffer
    _current_output_buffer = &_event_buffer_patch_out;

    for (MidiEventVector::const_iterator i = _event_buffer_pre_out.begin(); i != _event_buffer_pre_out.end(); ++i) {
        get_matching_patch(ev)->process(*i);
    }

    // postprocessing, write events to final buffer
    _current_output_buffer = &_event_buffer_final;
    for (MidiEventVector::const_iterator i = _event_buffer_patch_out.begin(); i != _event_buffer_patch_out.end(); ++i) {
        if (_post_patch) {
            _post_patch->process(*i);
        } else {
            buffer_event(*i);
        }
    }

    _current_output_buffer = NULL;

//    gettimeofday(&tv2, NULL);
//    cout << (tv2.tv_sec * 1000000LL + tv2.tv_usec) - (tv1.tv_sec * 1000000LL + tv1.tv_usec) << endl;

    return _event_buffer_final;
}


Patch * Setup::get_matching_patch(const MidiEvent & ev)
{
    // note on: store current patch
    if (ev.type == MIDI_EVENT_NOTEON) {
        _noteon_patches.insert(make_pair(make_notekey(ev), _current));
        return _current;
    }
    // note off: retrieve and remove stored patch
    else if (ev.type == MIDI_EVENT_NOTEOFF) {
        NotePatchMap::iterator i = _noteon_patches.find(make_notekey(ev));
        if (i != _noteon_patches.end()) {
            _noteon_patches.erase(i);
            return i->second;
        }
    }
    // sustain pressed
    else if (ev.type == MIDI_EVENT_CTRL && ev.ctrl.param == 64 && ev.ctrl.value == 127) {
        _sustain_patches.insert(make_pair(make_sustainkey(ev), _current));
        return _current;
    }
    // sustain released
    else if (ev.type == MIDI_EVENT_CTRL && ev.ctrl.param == 64 && ev.ctrl.value == 0) {
        SustainPatchMap::iterator i = _sustain_patches.find(make_sustainkey(ev));
        if (i != _sustain_patches.end()) {
            _sustain_patches.erase(i);
            return i->second;
        }
    }

    // anything else: just use current patch
    return _current;
}
