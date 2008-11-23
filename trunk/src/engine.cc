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

#include "config.hh"
#include "engine.hh"
#include "backend_alsa.hh"

#ifdef ENABLE_JACK_MIDI
  #include "backend_jack.hh"
#endif
#ifdef ENABLE_SMF
  #include "backend_smf.hh"
#endif

#include "python_util.hh"
#include "units.hh"

#include <boost/thread/thread.hpp>
#include <boost/bind.hpp>

#include <iostream>

#ifdef ENABLE_BENCHMARK
  #include <sys/time.h>
  #include <time.h>
#endif

#include <boost/python/call_method.hpp>

#include "util/debug.hh"


Engine * TheEngine = NULL;


Engine::Engine(PyObject * self,
               std::string const & backend_name,
               std::string const & client_name,
               std::vector<std::string> const & in_ports,
               std::vector<std::string> const & out_ports,
               bool verbose)
  : _self(self)
  , _verbose(verbose)
  , _current(NULL)
  , _current_num(-1)
  , _new_patch(-1)
  , _noteon_patches(Config::MAX_SIMULTANEOUS_NOTES)
  , _sustain_patches(Config::MAX_SUSTAIN_PEDALS)
  , _python_caller(new PythonCaller(boost::bind(&Engine::run_async, this)))
{
    DEBUG_FN();

    if (backend_name == "alsa") {
        _backend.reset(new BackendAlsa(client_name, in_ports, out_ports));
    }
#ifdef ENABLE_JACK_MIDI
    else if (backend_name == "jack") {
        _backend.reset(new BackendJackBuffered(client_name, in_ports, out_ports));
    }
    else if (backend_name == "jack-rt") {
        _backend.reset(new BackendJackRealtime(client_name, in_ports, out_ports));
    }
#endif
#ifdef ENABLE_SMF
    else if (backend_name == "smf") {
        _backend.reset(new BackendSmf(in_ports[0], out_ports[0]));
    }
#endif
    else if (backend_name != "dummy") {
        throw std::runtime_error("invalid backend selected: " + backend_name);
    }

    Patch::UnitPtr sani(new Sanitize);
    Patch::ModulePtr mod(new Patch::Single(sani));
    _sanitize_patch.reset(new Patch(mod));
}


Engine::~Engine()
{
    DEBUG_FN();

    // needs to be gone before the engine can be destroyed
    _python_caller.reset();
    _backend.reset();
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


void Engine::start(int first_patch)
{
    _backend->start(
        boost::bind(&Engine::run_init, this, first_patch),
        boost::bind(&Engine::run_cycle, this)
    );
}


void Engine::run_init(int first_patch)
{
    boost::mutex::scoped_lock lock(_process_mutex);

    _buffer.clear();
    process_patch_switch(_buffer, first_patch);

    _backend->output_events(_buffer.begin(), _buffer.end());
    _backend->flush_output();
}


void Engine::run_cycle()
{
    MidiEvent ev;

    while (_backend->input_event(ev))
    {
#ifdef ENABLE_BENCHMARK
        timeval tv1, tv2;
        gettimeofday(&tv1, NULL);
#endif

        boost::mutex::scoped_lock lock(_process_mutex);

        _buffer.clear();

        // process the event
        process(_buffer, ev);

        // handle patch switches
        if (_new_patch != -1) {
            process_patch_switch(_buffer, _new_patch);
            _new_patch = -1;
        }

#ifdef ENABLE_BENCHMARK
        gettimeofday(&tv2, NULL);
        std::cout << (tv2.tv_sec - tv1.tv_sec) * 1000000 + (tv2.tv_usec - tv1.tv_usec) << std::endl;
#endif

        _backend->output_events(_buffer.begin(), _buffer.end());
        _backend->flush_output();
    }
}


void Engine::run_async()
{
    if (!_backend) {
        // backend already destroyed
        return;
    }

    boost::mutex::scoped_lock lock(_process_mutex);

    _buffer.clear();

    if (_new_patch != -1) {
        process_patch_switch(_buffer, _new_patch);
        _new_patch = -1;
    }

    _backend->output_events(_buffer.begin(), _buffer.end());
    _backend->flush_output();
}


#ifdef ENABLE_TEST
std::vector<MidiEvent> Engine::process_test(MidiEvent const & ev)
{
    std::vector<MidiEvent> v;
    Events buffer;

    if (!_current) {
        _current = &*_patches.find(0)->second;
    }

    process(buffer, ev);

    if (_new_patch != -1) {
        process_patch_switch(buffer, _new_patch);
        _new_patch = -1;
    }

    v.insert(v.end(), buffer.begin(), buffer.end());
    return v;
}
#endif


void Engine::process(Events & buffer, MidiEvent const & ev)
{
    ASSERT(buffer.empty());

    Patch * patch = get_matching_patch(ev);

    if (_ctrl_patch) {
        buffer.insert(buffer.end(), ev);
        _ctrl_patch->process(buffer);
    }

    EventIter it = buffer.insert(buffer.end(), ev);
    EventRange r = EventRange(it, buffer.end());

    if (_pre_patch) {
        _pre_patch->process(buffer, r);
    }

    patch->process(buffer, r);

    if (_post_patch) {
        _post_patch->process(buffer, r);
    }

    _sanitize_patch->process(_buffer, r);
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
            Patch *p = i->second;
            _noteon_patches.erase(i);
            return p;
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
            Patch *p = i->second;
            _sustain_patches.erase(i);
            return p;
        }
    }

    // anything else: just use current patch
    return _current;
}


void Engine::switch_patch(int n)
{
    _new_patch = n;
}


void Engine::process_patch_switch(Events & buffer, int n)
{
    PatchMap::iterator i = _patches.find(n);

    if (_patches.size() > 1) {
        scoped_gil_lock gil;
        boost::python::call_method<void>(_self, "patch_switch_handler", n, i != _patches.end());
    }

    if (i != _patches.end()) {
        _current = &*i->second;
        _current_num = n;

        PatchMap::iterator k = _init_patches.find(n);

        if (k != _init_patches.end()) {
            MidiEvent ev(MIDI_EVENT_DUMMY, 0, 0, 0, 0);

            EventIter it = buffer.insert(buffer.end(), ev);
            EventRange r(EventRange(it, buffer.end()));

            k->second->process(buffer, r);

            if (_post_patch) {
                _post_patch->process(buffer, r);
            }

            _sanitize_patch->process(buffer, r);
        }
    }
}


bool Engine::sanitize_event(MidiEvent & ev) const
{
    if (ev.port < 0 || (_backend && ev.port >= static_cast<int>(_backend->num_out_ports()))) {
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
                return false;
            }
            if (ev.note.velocity < 0) ev.note.velocity = 0;
            if (ev.note.velocity > 127) ev.note.velocity = 127;
            if (ev.type == MIDI_EVENT_NOTEON && ev.note.velocity < 1) ev.note.velocity = 1;
            return true;
        case MIDI_EVENT_CTRL:
            if (ev.ctrl.param < 0 || ev.ctrl.param > 127) {
                if (_verbose) std::cout << "invalid controller number, event discarded" << std::endl;
                return false;
            }
            if (ev.ctrl.value < 0) ev.ctrl.value = 0;
            if (ev.ctrl.value > 127) ev.ctrl.value = 127;
            return true;
        case MIDI_EVENT_PITCHBEND:
            if (ev.ctrl.value < -8192) ev.ctrl.value = -8192;
            if (ev.ctrl.value >  8191) ev.ctrl.value =  8191;
            return true;
        case MIDI_EVENT_AFTERTOUCH:
            if (ev.ctrl.value < 0) ev.ctrl.value = 0;
            if (ev.ctrl.value > 127) ev.ctrl.value = 127;
            return true;
        case MIDI_EVENT_PROGRAM:
            if (ev.ctrl.value < 0 || ev.ctrl.value > 127) {
                if (_verbose) std::cout << "invalid program number, event discarded" << std::endl;
                return false;
            }
            return true;
        default:
            return false;
    }
}
