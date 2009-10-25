/*
 * mididings
 *
 * Copyright (C) 2008-2009  Dominic Sacré  <dominic.sacre@gmx.de>
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

#ifdef ENABLE_TEST
    #include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#endif // ENABLE_TEST

#include <vector>
#include <string>

#include "engine.hh"
#include "patch.hh"
#include "units.hh"

static inline int midi_event_get_type(MidiEvent & ev) {
    return (int)ev.type;
}

static inline void midi_event_set_type(MidiEvent & ev, int t) {
    ev.type = (MidiEventType)t;
}


BOOST_PYTHON_MODULE(_mididings)
{
    using boost::python::class_;
    using boost::python::bases;
    using boost::python::init;
    using boost::noncopyable;
    namespace bp = boost::python;

    PyEval_InitThreads();


    class_<Unit, noncopyable>("Unit", bp::no_init);
    class_<UnitEx, noncopyable>("UnitEx", bp::no_init);

    class_<Pass, bases<Unit>, noncopyable>("Pass", init<bool>());
    class_<Filter, bases<Unit>, noncopyable>("Filter", init<int>());
    class_<InvertedFilter, bases<Filter>, noncopyable>("InvertedFilter", init<boost::shared_ptr<Filter>, bool>());

    class_<PortFilter, bases<Filter>, noncopyable>("PortFilter", init<std::vector<int> const &>());
    class_<ChannelFilter, bases<Filter>, noncopyable>("ChannelFilter", init<std::vector<int> const &>());
    class_<KeyFilter, bases<Filter>, noncopyable>("KeyFilter", init<int, int>());
    class_<VelocityFilter, bases<Filter>, noncopyable>("VelocityFilter", init<int, int>());
    class_<CtrlFilter, bases<Filter>, noncopyable>("CtrlFilter", init<std::vector<int> const &>());
    class_<CtrlValueFilter, bases<Filter>, noncopyable>("CtrlValueFilter", init<int, int>());
    class_<ProgFilter, bases<Filter>, noncopyable>("ProgFilter", init<std::vector<int> const &>());

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
    class_<SceneSwitch, bases<Unit>, noncopyable>("SceneSwitch", init<int>());
    class_<Call, bases<UnitEx>, noncopyable>("Call", init<bp::object, bool, bool>());

    class_<Engine, Engine, noncopyable>("Engine", init<std::string const &,
                                                       std::string const &,
                                                       std::vector<std::string> const &,
                                                       std::vector<std::string> const &,
                                                       bool>())
        .def("add_scene", &Engine::add_scene)
        .def("set_processing", &Engine::set_processing)
        .def("start", &Engine::start)
        .def("switch_scene", &Engine::switch_scene)
        .def("current_scene", &Engine::current_scene)
#ifdef ENABLE_TEST
        .def("process", &Engine::process_test)
#endif // ENABLE_TEST
    ;

    {
        bp::scope patch_scope = class_<Patch, noncopyable>("Patch", init<Patch::ModulePtr>());

        class_<Patch::Module, noncopyable>("Module", bp::no_init);

        class_<Patch::ModuleVector, noncopyable>("ModuleVector")
            .def("push_back", &Patch::ModuleVector::push_back)
        ;

        class_<Patch::Chain, bases<Patch::Module>, noncopyable>("Chain", init<Patch::ModuleVector>());
        class_<Patch::Fork, bases<Patch::Module>, noncopyable>("Fork", init<Patch::ModuleVector, bool>());
        class_<Patch::Single, bases<Patch::Module>, noncopyable>("Single", init<boost::shared_ptr<Unit> >());
        class_<Patch::Extended, bases<Patch::Module>, noncopyable>("Extended", init<boost::shared_ptr<UnitEx> >());
    }

    class_<std::vector<int>, noncopyable>("int_vector")
        .def("push_back", &std::vector<int>::push_back)
    ;
    class_<std::vector<std::string>, noncopyable>("string_vector")
        .def("push_back", &std::vector<std::string>::push_back)
    ;

    class_<MidiEvent>("MidiEvent")
        .add_property("type_", &midi_event_get_type, &midi_event_set_type)
        .def_readwrite("port_", &MidiEvent::port)
        .def_readwrite("channel_", &MidiEvent::channel)
        .def_readwrite("data1", &MidiEvent::data1)
        .def_readwrite("data2", &MidiEvent::data2)
        .def(bp::self == bp::self)
    ;

#ifdef ENABLE_TEST
    class_<std::vector<MidiEvent> >("MidiEventVector")
        .def(bp::vector_indexing_suite<std::vector<MidiEvent> >())
    ;
#endif // ENABLE_TEST
}
