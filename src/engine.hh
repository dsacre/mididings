/*
 * mididings
 *
 * Copyright (C) 2008-2014  Dominic Sacré  <dominic.sacre@gmx.de>
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

#ifdef ENABLE_BENCHMARK
#include <chrono>
#endif

#include <boost/shared_ptr.hpp>
#include <boost/scoped_ptr.hpp>
#include <boost/noncopyable.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/unordered/unordered_map.hpp>

#include "util/counted_objects.hh"


namespace mididings {


class Engine
  : boost::noncopyable
  , das::counted_objects<Engine>
{
  public:

    typedef boost::shared_ptr<Patch> PatchPtr;

    struct Scene {
        Scene(PatchPtr patch_, PatchPtr init_patch_, PatchPtr exit_patch_)
          : patch(patch_)
          , init_patch(init_patch_)
          , exit_patch(exit_patch_)
        { }

        PatchPtr patch;
        PatchPtr init_patch;
        PatchPtr exit_patch;
    };

    typedef boost::shared_ptr<Scene> ScenePtr;
    typedef std::map<int, std::vector<ScenePtr> > SceneMap;

    typedef unsigned int EventKey;
    typedef boost::unordered_map<EventKey, Patch *> NotePatchMap;
    typedef boost::unordered_map<EventKey, Patch *> SustainPatchMap;


    Engine(backend::BackendPtr backend, bool verbose);

    virtual ~Engine();

    void add_scene(int i, PatchPtr patch,
                   PatchPtr init_patch, PatchPtr exit_patch);
    void set_processing(PatchPtr ctrl_patch,
                        PatchPtr pre_patch, PatchPtr post_patch);

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

    std::vector<MidiEvent> process_event(MidiEvent const & ev);

    void output_event(MidiEvent const & ev);

    double time();

    std::string get_client_name() const { return _backend->get_actual_client_name(); };

    int get_client_id() const { return _backend->get_client_id(); };

    std::string get_client_uuid() const { return _backend->get_client_uuid(); };

    PythonCaller & python_caller() const { return *_python_caller; }

  protected:
    virtual void scene_switch_callback(int scene, int subscene) = 0;

  private:

    void run_init(int initial_scene, int initial_subscene);
    void run_cycle();
    void run_async();

    template <typename B>
    void process(B & buffer, MidiEvent const & ev);

    template <typename B>
    void process_scene_switch(B & buffer);


    Patch * get_matching_patch(MidiEvent const & ev);


    EventKey make_notekey(MidiEvent const & ev) const {
        return ev.port | ev.channel << 16 | ev.note.note << 24;
    }
    EventKey make_sustainkey(MidiEvent const & ev) const {
        return ev.port | ev.channel << 16;
    }

    bool _verbose;

    backend::BackendPtr _backend;

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

    Patch::EventBufferRT _buffer;

    boost::mutex _process_mutex;

    boost::scoped_ptr<PythonCaller> _python_caller;

#ifdef ENABLE_BENCHMARK
  public:
    typedef std::chrono::high_resolution_clock hrclock;

    static int num_cycles() {
        return num_cycles_;
    }

    static int cycle_duration_mean() {
        if (!num_cycles_) return 0;
        return std::chrono::duration_cast<std::chrono::microseconds>(
                                cycles_duration_total_ / num_cycles_).count();
    }

    static int cycle_duration_max() {
        return std::chrono::duration_cast<std::chrono::microseconds>(
                                cycles_duration_max_).count();
    }

  private:
    static hrclock::duration cycles_duration_total_;
    static hrclock::duration cycles_duration_max_;
    static int num_cycles_;
#endif
};


} // mididings


#endif // MIDIDINGS_ENGINE_HH
