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

#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python/class.hpp>
#include <boost/python/scope.hpp>
#include <boost/python/operators.hpp>
#include <boost/python/tuple.hpp>

#ifdef ENABLE_TEST
    #include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#endif // ENABLE_TEST

#include <vector>
#include <string>

#include "engine.hh"
#include "patch.hh"
#include "units_base.hh"
#include "units_engine.hh"
#include "units_filters.hh"
#include "units_modifiers.hh"
#include "units_generators.hh"
#include "units_call.hh"


// getter/setter functions for MidiEvent.type, to allow MidiEventType <-> int conversion
static inline int midi_event_get_type(MidiEvent & ev) {
    return static_cast<int>(ev.type);
}
static inline void midi_event_set_type(MidiEvent & ev, int t) {
    ev.type = static_cast<MidiEventType>(t);
}

// very primitive pickling support for MidiEvent objects
struct midi_event_pickle_suite
  : boost::python::pickle_suite
{
    static boost::python::tuple getinitargs(const MidiEvent & w) {
        return boost::python::make_tuple(static_cast<int>(w.type), w.port, w.channel, w.data1, w.data2);
    }
};

// simple wrapper for vector types, with no methods other than push_back
template <typename T>
static void vector_wrapper(char const *name) {
    boost::python::class_<std::vector<T>, boost::noncopyable>(name)
        .def("push_back", &std::vector<T>::push_back)
    ;
}


BOOST_PYTHON_MODULE(_mididings)
{
    using boost::python::class_;
    using boost::python::bases;
    using boost::python::init;
    using boost::noncopyable;
    namespace bp = boost::python;

    PyEval_InitThreads();

    // unit base classes
    class_<Unit, noncopyable>("Unit", bp::no_init);
    class_<UnitEx, noncopyable>("UnitEx", bp::no_init);
    class_<Filter, bases<Unit>, noncopyable>("Filter", bp::no_init);

    // base
    class_<Pass, bases<Unit>, noncopyable>("Pass", init<bool>());
    class_<TypeFilter, bases<Filter>, noncopyable>("TypeFilter", init<int>());
    class_<InvertedFilter, bases<Filter>, noncopyable>("InvertedFilter", init<boost::shared_ptr<Filter>, bool>());

    // engine
    class_<Sanitize, bases<Unit>, noncopyable>("Sanitize", init<>());
    class_<SceneSwitch, bases<Unit>, noncopyable>("SceneSwitch", init<int, int>());
    class_<SubSceneSwitch, bases<Unit>, noncopyable>("SubSceneSwitch", init<int, int, bool>());

    // filters
    class_<PortFilter, bases<Filter>, noncopyable>("PortFilter", init<std::vector<int> const &>());
    class_<ChannelFilter, bases<Filter>, noncopyable>("ChannelFilter", init<std::vector<int> const &>());
    class_<KeyFilter, bases<Filter>, noncopyable>("KeyFilter", init<int, int, std::vector<int> const &>());
    class_<VelocityFilter, bases<Filter>, noncopyable>("VelocityFilter", init<int, int>());
    class_<CtrlFilter, bases<Filter>, noncopyable>("CtrlFilter", init<std::vector<int> const &>());
    class_<CtrlValueFilter, bases<Filter>, noncopyable>("CtrlValueFilter", init<int, int>());
    class_<ProgramFilter, bases<Filter>, noncopyable>("ProgramFilter", init<std::vector<int> const &>());
    class_<SysExFilter, bases<Filter>, noncopyable>("SysExFilter", init<std::string const &, bool>());

    // modifiers
    class_<Port, bases<Unit>, noncopyable>("Port", init<int>());
    class_<Channel, bases<Unit>, noncopyable>("Channel", init<int>());
    class_<Transpose, bases<Unit>, noncopyable>("Transpose", init<int>());
    class_<Velocity, bases<Unit>, noncopyable>("Velocity", init<float, int>());
    class_<VelocitySlope, bases<Unit>, noncopyable>("VelocitySlope", init<std::vector<int> const &, std::vector<float> const &, int>());
    class_<CtrlMap, bases<Unit>, noncopyable>("CtrlMap", init<int, int>());
    class_<CtrlRange, bases<Unit>, noncopyable>("CtrlRange", init<int, int, int, int, int>());

    // generators
    class_<Generator, bases<Unit>, noncopyable>("Generator", init<int, int, int, int, int>());
    class_<SysExGenerator, bases<Unit>, noncopyable>("SysExGenerator", init<int, std::string const &>());

    // call
    class_<Call, bases<UnitEx>, noncopyable>("Call", init<bp::object, bool, bool>());

    // main engine class, derived in python
    class_<Engine, Engine, noncopyable>("Engine", init<std::string const &, std::string const &,
                                                       std::vector<std::string> const &, std::vector<std::string> const &, bool>())
        .def("add_scene", &Engine::add_scene)
        .def("set_processing", &Engine::set_processing)
        .def("start", &Engine::start)
        .def("switch_scene", &Engine::switch_scene)
        .def("current_scene", &Engine::current_scene)
        .def("current_subscene", &Engine::current_subscene)
        .def("output_event", &Engine::output_event)
#ifdef ENABLE_TEST
        .def("process", &Engine::process_test)
#endif // ENABLE_TEST
    ;

    // patch class, derived in python
    {
    bp::scope patch_scope = class_<Patch, noncopyable>("Patch", init<Patch::ModulePtr>());

    class_<Patch::Module, noncopyable>("Module", bp::no_init);

    vector_wrapper<Patch::ModulePtr>("ModuleVector");

    class_<Patch::Chain, bases<Patch::Module>, noncopyable>("Chain", init<Patch::ModuleVector>());
    class_<Patch::Fork, bases<Patch::Module>, noncopyable>("Fork", init<Patch::ModuleVector, bool>());
    class_<Patch::Single, bases<Patch::Module>, noncopyable>("Single", init<boost::shared_ptr<Unit> >());
    class_<Patch::Extended, bases<Patch::Module>, noncopyable>("Extended", init<boost::shared_ptr<UnitEx> >());
    }

    // midi event class, derived in python
    class_<MidiEvent>("MidiEvent")
        .add_property("type", &midi_event_get_type, &midi_event_set_type)
        .def_readwrite("port_", &MidiEvent::port)
        .def_readwrite("channel_", &MidiEvent::channel)
        .def_readwrite("data1", &MidiEvent::data1)
        .def_readwrite("data2", &MidiEvent::data2)
        .add_property("sysex", &MidiEvent::get_sysex_data, &MidiEvent::set_sysex_data)
        .def(bp::self == bp::self)
        .def_pickle(midi_event_pickle_suite())
    ;

    vector_wrapper<int>("int_vector");
    vector_wrapper<float>("float_vector");
    vector_wrapper<std::string>("string_vector");

#ifdef ENABLE_TEST
    class_<std::vector<MidiEvent> >("MidiEventVector")
        .def(bp::vector_indexing_suite<std::vector<MidiEvent> >())
    ;
#endif // ENABLE_TEST
}
