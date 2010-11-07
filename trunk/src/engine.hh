/*
 * mididings
 *
 * Copyright (C) 2008-2010  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef MIDIDINGS_ENGINE_HH
#define MIDIDINGS_ENGINE_HH

#include "patch.hh"
#include "backend/base.hh"
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


namespace Mididings {


extern class Engine * TheEngine;


class Engine
  : public das::global_object<Engine, TheEngine>
{
  public:

    typedef boost::shared_ptr<Patch> PatchPtr;

    struct Scene {
        Scene(PatchPtr patch_, PatchPtr init_patch_)
          : patch(patch_), init_patch(init_patch_) { }

        PatchPtr patch;
        PatchPtr init_patch;
    };

    typedef boost::shared_ptr<Scene> ScenePtr;
    typedef std::map<int, std::vector<ScenePtr> > SceneMap;

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

    void add_scene(int i, PatchPtr patch, PatchPtr init_patch);
    void set_processing(PatchPtr ctrl_patch, PatchPtr pre_patch, PatchPtr post_patch);

    void start(int initial_scene, int initial_subscene);

    void switch_scene(int scene, int subscene = -1);

    bool sanitize_event(MidiEvent & ev) const;

    int current_scene() const {
        return _current_scene;
    }
    int current_subscene() const {
        return _current_subscene;
    }
    bool has_scene(int n) const {
        return _scenes.find(n) != _scenes.end();
    }
    bool has_subscene(int n) const {
        return num_subscenes() > n;
    }
    int num_subscenes() const {
        SceneMap::const_iterator i = _scenes.find(_current_scene);
        return i != _scenes.end() ? i->second.size() : 0;
    }

    void output_event(MidiEvent const & ev);

    PythonCaller & python_caller() const { return *_python_caller; }

#ifdef ENABLE_TEST
    std::vector<MidiEvent> process_test(MidiEvent const & ev);
#endif

  private:

    void run_init(int initial_scene, int initial_subscene);
    void run_cycle();
    void run_async();

    void process(Events & buffer, MidiEvent const & ev);
    void process_scene_switch(Events & buffer);


    Patch * get_matching_patch(MidiEvent const & ev);


    EventKey make_notekey(MidiEvent const & ev) const {
        return ev.port | ev.channel << 16 | ev.note.note << 24;
    }
    EventKey make_sustainkey(MidiEvent const & ev) const {
        return ev.port | ev.channel << 16;
    }

    PyObject * _self;
    bool _verbose;

    boost::shared_ptr<Backend::BackendBase> _backend;

    SceneMap _scenes;

    PatchPtr _ctrl_patch;
    PatchPtr _pre_patch;
    PatchPtr _post_patch;
    PatchPtr _sanitize_patch;

    Patch * _current_patch;

    int _current_scene;
    int _current_subscene;

    int _new_scene;
    int _new_subscene;

    NotePatchMap _noteon_patches;
    SustainPatchMap _sustain_patches;

    Events _buffer;

    boost::mutex _process_mutex;

    boost::scoped_ptr<PythonCaller> _python_caller;
};


} // Mididings


#endif // MIDIDINGS_ENGINE_HH
