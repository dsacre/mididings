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

#include "engine.hh"
#include "backend_alsa.hh"
#include "util/debug.hh"

#include <iostream>

#ifdef ENABLE_BENCHMARK
  #include <sys/time.h>
  #include <time.h>
#endif

#include <boost/python/call_method.hpp>


Engine * TheEngine = NULL;


Engine::Engine(PyObject * self,
               std::string const & backend_name,
               std::string const & client_name,
               std::vector<std::string> const & in_ports,
               std::vector<std::string> const & out_ports,
               bool verbose)
  : _self(self),
    _verbose(verbose),
    _current(NULL),
    _noteon_patches(MAX_SIMULTANEOUS_NOTES),
    _sustain_patches(MAX_SUSTAIN_PEDALS),
    _python_caller(new PythonCaller())
{
    DEBUG_FN();

    if (backend_name == "alsa") {
        _backend.reset(new BackendAlsa(client_name, in_ports, out_ports));
    }

    _num_out_ports = (int)out_ports.size();
}


Engine::~Engine()
{
    DEBUG_FN();
}


void Engine::add_patch(int i, PatchPtr patch, PatchPtr init_patch)
{
    ASSERT(_patches.find(i) == _patches.end());

    _patches[i] = patch;
    if (init_patch) {
        _init_patches[i] = init_patch;
    }
}


void Engine::set_processing(PatchPtr ctrl_patch, PatchPtr pre_patch, PatchPtr post_patch)
{
    ASSERT(!_ctrl_patch);
    ASSERT(!_pre_patch);
    ASSERT(!_post_patch);
    _ctrl_patch = ctrl_patch;
    _pre_patch = pre_patch;
    _post_patch = post_patch;
}


void Engine::run()
{
    if (!_backend) {
        return;
    }

    // we'll stay in C++ land from now on, except for Call()
    Py_BEGIN_ALLOW_THREADS

    MidiEvent ev;

    while (_backend->input_event(ev)) {
        Patch::Events buffer;

        Patch::EventIterRange r = process(buffer, ev);

        _backend->output_events(r);
        _backend->flush_output();
    }

    Py_END_ALLOW_THREADS
}


Patch::EventIterRange Engine::process(Patch::Events & buffer, MidiEvent const & ev)
{
    boost::recursive_mutex::scoped_lock lock(_process_mutex);

#ifdef ENABLE_BENCHMARK
    timeval tv1, tv2;
    gettimeofday(&tv1, NULL);
#endif

    buffer.insert(buffer.end(), ev);

    Patch::EventIterRange range(buffer);

    Patch * patch = get_matching_patch(ev);

    if (_ctrl_patch) {
        _ctrl_patch->process(buffer, range);

        Patch::EventIter it = buffer.insert(buffer.end(), ev);
        range = Patch::EventIterRange(it, buffer.end());
    }

    if (_pre_patch) {
        range = _pre_patch->process(buffer, range);
    }

    range = patch->process(buffer, range);

    if (_post_patch) {
        range = _post_patch->process(buffer, range);
    }

#ifdef ENABLE_BENCHMARK
    gettimeofday(&tv2, NULL);
    std::cout << (tv2.tv_sec - tv1.tv_sec) * 1000000 + (tv2.tv_usec - tv1.tv_usec) << std::endl;
#endif

    return range;
}


Patch * Engine::get_matching_patch(MidiEvent const & ev)
{
    // note on: store current patch
    if (ev.type == MIDI_EVENT_NOTEON) {
        _noteon_patches.insert(std::make_pair(make_notekey(ev), _current));
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
        _sustain_patches.insert(std::make_pair(make_sustainkey(ev), _current));
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


Patch::EventIterRange Engine::init_events()
{
/*
    boost::recursive_mutex::scoped_lock lock(_process_mutex);

    _event_buffer_final.clear();

    // apply postprocessing
    _output_buffer = &_event_buffer_final;
    for (MidiEventVector::const_iterator i = _event_buffer_patch_out.begin(); i != _event_buffer_patch_out.end(); ++i) {
        if (_post_patch) {
            _post_patch->process(*i);
        } else {
            buffer_event(*i);
        }
    }

    return _event_buffer_final;
*/
    return Patch::EventIterRange();
}


void Engine::switch_patch(int n, MidiEvent const & ev)
{
#if 0
    boost::recursive_mutex::scoped_lock lock(_process_mutex);

    PatchMap::iterator i = _patches.find(n);

    if (_patches.size() > 1) {
        PyGILState_STATE gil = PyGILState_Ensure();
        boost::python::call_method<void>(_self, "print_switch_patch", n, i != _patches.end());
        PyGILState_Release(gil);
    }

    if (i != _patches.end()) {
        _current = &*i->second;

        PatchMap::iterator k = _init_patches.find(n);
        if (k != _init_patches.end()) {
/*
            // temporarily redirect output to patch_out so events will go through postprocessing
            MidiEventVector *p = _output_buffer;
            _output_buffer = &_event_buffer_patch_out;

            k->second->process(ev);

            _output_buffer = p;
*/
        }
    }
#endif
}


bool Engine::sanitize_event(MidiEvent & ev) const
{
    if (ev.port < 0 || ev.port >= num_out_ports()) {
        if (_verbose) std::cout << "invalid port, event discarded" << std::endl;
        return false;
    }

    if (ev.channel < 0 || ev.channel > 15) {
        if (_verbose) std::cout << "invalid channel, event discarded" << std::endl;
        return false;
    }

    switch (ev.type) {
        case MIDI_EVENT_NOTEON:
        case MIDI_EVENT_NOTEOFF:
            if (ev.note.note < 0 || ev.note.note > 127) {
                if (_verbose) std::cout << "invalid note number, event discarded" << std::endl;
            }
            if (ev.note.velocity < 0) ev.note.velocity = 0;
            if (ev.note.velocity > 127) ev.note.velocity = 127;
            if (ev.type == MIDI_EVENT_NOTEON && ev.note.velocity < 1) ev.note.velocity = 1;
            return true;
        case MIDI_EVENT_CTRL:
            if (ev.ctrl.param < 0 || ev.ctrl.param > 127) {
                if (_verbose) std::cout << "invalid controller number, event discarded" << std::endl;
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
                if (_verbose) std::cout << "invalid program number, event discarded" << std::endl;
            }
            return true;
        default:
            return false;
    }
}
