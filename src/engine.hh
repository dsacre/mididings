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


extern class Engine *TheEngine;


class Engine
  : public das::global_object<Engine, ::TheEngine>
{
  public:
    static const int MAX_SIMULTANEOUS_NOTES = 64;
    static const int MAX_SUSTAIN_PEDALS = 4;
//    static const int EVENT_BUFFER_SIZE = 16;

    typedef boost::shared_ptr<Patch> PatchPtr;
    typedef std::map<int, PatchPtr> PatchMap;
    typedef unsigned int EventKey;
    typedef std::tr1::unordered_map<EventKey, Patch *> NotePatchMap;
    typedef std::tr1::unordered_map<EventKey, Patch *> SustainPatchMap;


    typedef std::vector<MidiEvent> MidiEventVector;


    Engine(PyObject * self,
           const std::string & backend_name,
           const std::string & client_name,
           const std::vector<std::string> & in_ports,
           const std::vector<std::string> & out_ports,
           bool verbose,
           bool remove_duplicates);

    ~Engine();

    void add_patch(int i, PatchPtr patch, PatchPtr init_patch);
    void set_processing(PatchPtr ctrl_patch, PatchPtr pre_patch, PatchPtr post_patch);

    int num_out_ports() const { return _num_out_ports; }

    bool remove_duplicates() const { return _remove_duplicates; }

    void run();

    void switch_patch(int n, const MidiEvent & ev);

    const MidiEventVector & process(const MidiEvent & ev);

    const MidiEventVector & init_events();


    bool sanitize_event(MidiEvent & ev) const;

    bool call_now(boost::python::object & fun, MidiEvent & ev) {
        return _python_caller->call_now(fun, ev);
    }

    void call_deferred(boost::python::object & fun, MidiEvent const & ev) {
        _python_caller->call_deferred(fun, ev);
    }

  private:
    Patch * get_matching_patch(const MidiEvent & ev);

    static inline EventKey make_notekey(const MidiEvent & ev) {
        return ev.port | ev.channel << 16 | ev.note.note << 24;
    }
    static inline EventKey make_sustainkey(const MidiEvent & ev) {
        return ev.port | ev.channel << 16;
    }

    PyObject * _self;
    bool _verbose;
    bool _remove_duplicates;

    boost::shared_ptr<Backend> _backend;
    int _num_out_ports;

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
