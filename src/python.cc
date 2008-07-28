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

#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python/class.hpp>
#include <boost/python/scope.hpp>

#ifdef ENABLE_TEST
    #include <boost/python/operators.hpp>
    #include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#endif // ENABLE_TEST

#include <vector>
#include <string>

#include "engine.hh"
#include "patch.hh"
#include "units.hh"

using namespace boost::python;
using namespace boost;
using namespace std;


static inline int midi_event_get_type(MidiEvent & ev) {
    return (int)ev.type;
}

static inline void midi_event_set_type(MidiEvent & ev, int t) {
    ev.type = (MidiEventType)t;
}

#ifdef ENABLE_TEST

vector<MidiEvent> engine_process_test(Engine * this_, MidiEvent const & ev)
{
    vector<MidiEvent> v;
    Patch::Events buffer;

    this_->process(buffer, ev);

    v.insert(v.end(), buffer.begin(), buffer.end());
    return v;
}

#endif // ENABLE_TEST



BOOST_PYTHON_MODULE(_mididings)
{
    PyEval_InitThreads();

    class_<Unit, noncopyable>("Unit", no_init);

    class_<Pass, bases<Unit>, noncopyable>("Pass", init<bool>());
    class_<Filter, bases<Unit>, noncopyable>("Filter", init<int>());
    class_<InvertedFilter, bases<Unit>, noncopyable>("InvertedFilter", init<shared_ptr<Filter>, bool>());

    class_<PortFilter, bases<Filter>, noncopyable>("PortFilter", init<const vector<int> &>());
    class_<ChannelFilter, bases<Filter>, noncopyable>("ChannelFilter", init<const vector<int> &>());
    class_<KeyFilter, bases<Filter>, noncopyable>("KeyFilter", init<int, int>());
    class_<VelocityFilter, bases<Filter>, noncopyable>("VelocityFilter", init<int, int>());
    class_<CtrlFilter, bases<Filter>, noncopyable>("CtrlFilter", init<const vector<int> &>());
    class_<CtrlValueFilter, bases<Filter>, noncopyable>("CtrlValueFilter", init<int, int>());
    class_<ProgFilter, bases<Filter>, noncopyable>("ProgFilter", init<const vector<int> &>());

    class_<Port, bases<Unit>, noncopyable>("Port", init<int>());
    class_<Channel, bases<Unit>, noncopyable>("Channel", init<int>());
    class_<Transpose, bases<Unit>, noncopyable>("Transpose", init<int>());
    class_<Velocity, bases<Unit>, noncopyable>("Velocity", init<float, int>());
    class_<VelocityCurve, bases<Unit>, noncopyable>("VelocityCurve", init<float>());
    class_<VelocityGradient, bases<Unit>, noncopyable>("VelocityGradient", init<int, int, float, float, int>());
    class_<CtrlMap, bases<Unit>, noncopyable>("CtrlMap", init<int, int>());
    class_<CtrlRange, bases<Unit>, noncopyable>("CtrlRange", init<int, int, int, int, int>());

    class_<GenerateEvent, bases<Unit>, noncopyable>("GenerateEvent", init<int, int, int, int, int>());
    class_<Sanitize, bases<Unit>, noncopyable>("Sanitize", init<>());
    class_<PatchSwitch, bases<Unit>, noncopyable>("PatchSwitch", init<int>());
    class_<Call, bases<Unit>, noncopyable>("Call", init<object, bool, bool>());

    class_<Engine, Engine, noncopyable>("Engine", init<const string &, const string &,
                                                       const vector<string> &, const vector<string> &,
                                                       bool, bool>())
        .def("add_patch", &Engine::add_patch)
        .def("set_processing", &Engine::set_processing)
        .def("run", &Engine::run)
        .def("switch_patch", &Engine::switch_patch)
#ifdef ENABLE_TEST
        .def("process", &engine_process_test)
#endif // ENABLE_TEST
    ;

    {
        scope patch_scope = class_<Patch, noncopyable>("Patch", init<Patch::ModulePtr>());

        class_<Patch::Module, noncopyable>("Module", no_init);

        class_<Patch::ModuleVector, noncopyable>("ModuleVector")
            .def("push_back", &Patch::ModuleVector::push_back)
        ;

        class_<Patch::Chain, bases<Patch::Module>, noncopyable>("Chain", init<Patch::ModuleVector>());
        class_<Patch::Fork, bases<Patch::Module>, noncopyable>("Fork", init<Patch::ModuleVector, bool>());
        class_<Patch::Single, bases<Patch::Module>, noncopyable>("Single", init<shared_ptr<Unit> >());
    }

    class_<vector<int>, noncopyable>("int_vector")
        .def("push_back", &vector<int>::push_back)
    ;
    class_<vector<string>, noncopyable>("string_vector")
        .def("push_back", &vector<string>::push_back)
    ;

    class_<MidiEvent>("MidiEvent")
        .add_property("type_", &midi_event_get_type, &midi_event_set_type)
        .def_readwrite("port_", &MidiEvent::port)
        .def_readwrite("channel_", &MidiEvent::channel)
        .def_readwrite("data1", &MidiEvent::data1)
        .def_readwrite("data2", &MidiEvent::data2)
#ifdef ENABLE_TEST
        .def(self == self)
#endif // ENABLE_TEST
    ;

#ifdef ENABLE_TEST
    class_<vector<MidiEvent> >("MidiEventVector")
        .def(vector_indexing_suite<vector<MidiEvent> >())
    ;
#endif // ENABLE_TEST
}
