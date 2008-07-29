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

#include <boost/thread/recursive_mutex.hpp>

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

    void switch_patch(int n, MidiEvent const & ev);
    bool sanitize_event(MidiEvent & ev) const;

    bool call_now(boost::python::object & fun, MidiEvent & ev) {
        return _python_caller->call_now(fun, ev);
    }

    void call_deferred(boost::python::object & fun, MidiEvent const & ev) {
        _python_caller->call_deferred(fun, ev);
    }

#ifdef ENABLE_TEST
    std::vector<MidiEvent> process_test(MidiEvent const & ev)
    {
        std::vector<MidiEvent> v;
        Patch::Events buffer;

        process(buffer, ev);

        v.insert(v.end(), buffer.begin(), buffer.end());
        return v;
    }
#endif

  private:

    Patch::EventIterRange process(Patch::Events & buffer, MidiEvent const & ev);
    Patch::EventIterRange init_events();

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

    Patch * _current;

    NotePatchMap _noteon_patches;
    SustainPatchMap _sustain_patches;

    boost::recursive_mutex _process_mutex;

    boost::scoped_ptr<PythonCaller> _python_caller;
};


#endif // _ENGINE_HH
