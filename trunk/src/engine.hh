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

    typedef boost::shared_ptr<Patch> PatchPtr;
    typedef std::map<int, PatchPtr> PatchMap;
    typedef unsigned int EventKey;
    typedef std::tr1::unordered_map<EventKey, Patch *> NotePatchMap;
    typedef std::tr1::unordered_map<EventKey, Patch *> SustainPatchMap;

    typedef Patch::Events Events;
    typedef Patch::EventIter EventIter;
    typedef Patch::EventRange EventRange;


    Engine(PyObject * self,
           std::string const & backend_name,
           std::string const & client_name,
           std::vector<std::string> const & in_ports,
           std::vector<std::string> const & out_ports,
           bool verbose);

    ~Engine();

    void add_patch(int i, PatchPtr patch, PatchPtr init_patch);
    void set_processing(PatchPtr ctrl_patch, PatchPtr pre_patch, PatchPtr post_patch);

    void start(int first_patch);

    void switch_patch(int n);
    bool sanitize_event(MidiEvent & ev) const;

    int current_patch() const { return _current_num; }

    PythonCaller & python_caller() const { return *_python_caller; }

#ifdef ENABLE_TEST
    std::vector<MidiEvent> process_test(MidiEvent const & ev);
#endif

  private:

    void run_init(int first_patch);
    void run_cycle();
    void run_async();

    void process(Events & buffer, MidiEvent const & ev);
    void process_patch_switch(Events & buffer, int n);


    Patch * get_matching_patch(MidiEvent const & ev);


    EventKey make_notekey(MidiEvent const & ev) const {
        return ev.port | ev.channel << 16 | ev.note.note << 24;
    }
    EventKey make_sustainkey(MidiEvent const & ev) const {
        return ev.port | ev.channel << 16;
    }

    PyObject * _self;
    bool _verbose;

    boost::shared_ptr<Backend> _backend;

    PatchMap _patches;
    PatchMap _init_patches;

    PatchPtr _ctrl_patch;
    PatchPtr _pre_patch;
    PatchPtr _post_patch;
    PatchPtr _sanitize_patch;

    Patch * _current;
    int _current_num;

    int _new_patch;

    NotePatchMap _noteon_patches;
    SustainPatchMap _sustain_patches;

    Events _buffer;

    boost::mutex _process_mutex;

    boost::scoped_ptr<PythonCaller> _python_caller;
};


#endif // _ENGINE_HH
