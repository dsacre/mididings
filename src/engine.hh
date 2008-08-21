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

#ifndef _ENGINE_HH
#define _ENGINE_HH

#include "patch.hh"
#include "backend.hh"
#include "python_caller.hh"

#include <string>
#include <vector>
#include <map>
#include <tr1/unordered_map>

#include <boost/shared_ptr.hpp>
#include <boost/scoped_ptr.hpp>

#include <boost/thread/mutex.hpp>

#include <boost/python/object.hpp>

#include "util/global_object.hh"


extern class Engine * TheEngine;


class Engine
  : public das::global_object<Engine, ::TheEngine>
{
  public:

    static int const MAX_SIMULTANEOUS_NOTES = 64;
    static int const MAX_SUSTAIN_PEDALS = 4;

    typedef boost::shared_ptr<Patch> PatchPtr;
    typedef std::map<int, PatchPtr> PatchMap;
    typedef unsigned int EventKey;
    typedef std::tr1::unordered_map<EventKey, Patch *> NotePatchMap;
    typedef std::tr1::unordered_map<EventKey, Patch *> SustainPatchMap;


    Engine(PyObject * self,
           std::string const & backend_name,
           std::string const & client_name,
           std::vector<std::string> const & in_ports,
           std::vector<std::string> const & out_ports,
           bool verbose);

    ~Engine();

    void add_patch(int i, PatchPtr patch, PatchPtr init_patch);
    void set_processing(PatchPtr ctrl_patch, PatchPtr pre_patch, PatchPtr post_patch);

    int num_out_ports() const { return _num_out_ports; }

    void run();

    void switch_patch(int n);
    bool sanitize_event(MidiEvent & ev) const;

    PythonCaller & python_caller() const { return *_python_caller; }

#ifdef ENABLE_TEST
    std::vector<MidiEvent> process_test(MidiEvent const & ev)
    {
        std::vector<MidiEvent> v;
        Patch::Events buffer;

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

  private:

    void process(Patch::Events & buffer, MidiEvent const & ev);
    void process_patch_switch(Patch::Events & buffer, int n);


    Patch * get_matching_patch(MidiEvent const & ev);


    inline EventKey make_notekey(MidiEvent const & ev) const {
        return ev.port | ev.channel << 16 | ev.note.note << 24;
    }
    inline EventKey make_sustainkey(MidiEvent const & ev) const {
        return ev.port | ev.channel << 16;
    }

    PyObject * _self;
    bool _verbose;
    int _num_out_ports;

    boost::shared_ptr<Backend> _backend;

    PatchMap _patches;
    PatchMap _init_patches;

    PatchPtr _ctrl_patch;
    PatchPtr _pre_patch;
    PatchPtr _post_patch;
    PatchPtr _sanitize_patch;

    Patch * _current;

    int _new_patch;

    NotePatchMap _noteon_patches;
    SustainPatchMap _sustain_patches;

    boost::mutex _process_mutex;

    boost::scoped_ptr<PythonCaller> _python_caller;
};


#endif // _ENGINE_HH
