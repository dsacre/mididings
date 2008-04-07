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

#include <iostream>
//#include <sys/time.h>
//#include <time.h>
#include <boost/python/call_method.hpp>

using namespace std;


Setup * TheSetup = NULL;


Setup::Setup(PyObject * self,
             const string & backend_name,
             const string & client_name,
             const vector<string> & in_ports,
             const vector<string> & out_ports)
  : _self(self),
    _current(NULL),
    _noteon_patches(MAX_SIMULTANEOUS_NOTES),
    _sustain_patches(MAX_SUSTAIN_PEDALS),
    _event_buffer_pre_out(EVENT_BUFFER_SIZE),
    _event_buffer_patch_out(EVENT_BUFFER_SIZE),
    _event_buffer_final(EVENT_BUFFER_SIZE),
    _output_buffer(NULL)
{
    DEBUG_FN();

    if (backend_name == "alsa") {
        _backend.reset(new BackendAlsa(client_name, in_ports, out_ports));
    }

    _num_out_ports = (int)out_ports.size();
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
        _output_buffer = &_event_buffer_final;
        _ctrl_patch->process(ev);
    }

//    DEBUG_PRINT(p);

    // preprocessing, write events to intermediate buffer
    _output_buffer = &_event_buffer_pre_out;

    if (_pre_patch) {
        _pre_patch->process(ev);
    } else {
        buffer_event(ev);
    }

    // process patch, write events to another buffer
    _output_buffer = &_event_buffer_patch_out;

    for (MidiEventVector::const_iterator i = _event_buffer_pre_out.begin(); i != _event_buffer_pre_out.end(); ++i) {
        get_matching_patch(ev)->process(*i);
    }

    // postprocessing, write events to final buffer
    _output_buffer = &_event_buffer_final;
    for (MidiEventVector::const_iterator i = _event_buffer_patch_out.begin(); i != _event_buffer_patch_out.end(); ++i) {
        if (_post_patch) {
            _post_patch->process(*i);
        } else {
            buffer_event(*i);
        }
    }

    _output_buffer = NULL;

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


void Setup::switch_patch(int n, const MidiEvent & ev)
{
    PatchMap::iterator i = _patches.find(n);

    boost::python::call_method<void>(_self, "print_switch_patch", n, i != _patches.end());

    if (i != _patches.end()) {
        _current = &*i->second;

        PatchMap::iterator k = _init_patches.find(n);
        if (k != _init_patches.end()) {
            // temporarily redirect output to patch_out so events will go through postprocessing
            MidiEventVector *p = _output_buffer;
            _output_buffer = &_event_buffer_patch_out;

            k->second->process(ev);

            _output_buffer = p;
        }
    }
}


bool Setup::sanitize_event(MidiEvent & ev, bool print) const
{
    if (ev.port < 0 || ev.port >= num_out_ports()) {
        if (print) cout << "invalid port, event discarded" << endl;
        return false;
    }

    if (ev.channel < 0 || ev.channel > 15) {
        if (print) cout << "invalid channel, event discarded" << endl;
        return false;
    }

    switch (ev.type) {
        case MIDI_EVENT_NOTEON:
        case MIDI_EVENT_NOTEOFF:
            if (ev.note.note < 0 || ev.note.note > 127) {
                if (print) cout << "invalid note number, event discarded" << endl;
            }
            if (ev.note.velocity < 0) ev.note.velocity = 0;
            if (ev.note.velocity > 127) ev.note.velocity = 127;
            return true;
        case MIDI_EVENT_CTRL:
            if (ev.ctrl.param < 0 || ev.ctrl.param > 127) {
                if (print) cout << "invalid controller number, event discarded" << endl;
            }
            if (ev.ctrl.value < 0) ev.ctrl.value = 0;
            if (ev.ctrl.value > 127) ev.ctrl.value = 127;
            return true;
        case MIDI_EVENT_PITCHBEND:
            if (ev.ctrl.value < -8192) ev.ctrl.value = -8192;
            if (ev.ctrl.value >  8191) ev.ctrl.value =  8191;
            return true;
        case MIDI_EVENT_PROGRAM:
            if (ev.ctrl.value < 0 || ev.ctrl.value > 127) {
                if (print) cout << "invalid program number, event discarded" << endl;
            }
            return true;
        default:
            return false;
    }
}
