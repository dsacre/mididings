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
//#include <boost/python/ptr.hpp>

#ifdef ENABLE_TEST
    #include <boost/python/operators.hpp>
    #include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#endif // ENABLE_TEST

#include <vector>
#include <string>

#include "setup.hh"
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
bool operator==(const MidiEvent & lhs, const MidiEvent & rhs) {
    return (lhs.type == rhs.type &&
            lhs.port == rhs.port &&
            lhs.channel == rhs.channel &&
            lhs.data1 == rhs.data1 &&
            lhs.data2 == rhs.data2);
}
#endif // ENABLE_TEST


BOOST_PYTHON_MODULE(_mididings)
{
    class_<Unit, noncopyable>("Unit", no_init);

    class_<Pass, bases<Unit> >("Pass", init<bool>());

    class_<Filter, bases<Unit> >("Filter", init<int>());
    class_<InvertedFilter, bases<Unit> >("InvertedFilter", init<shared_ptr<Filter>, bool>());

    class_<PortFilter, bases<Filter> >("PortFilter", init<const vector<int> &>());
    class_<ChannelFilter, bases<Filter> >("ChannelFilter", init<const vector<int> &>());
    class_<KeyFilter, bases<Filter> >("KeyFilter", init<int, int>());
    class_<VelocityFilter, bases<Filter> >("VelocityFilter", init<int, int>());
    class_<CtrlFilter, bases<Filter> >("CtrlFilter", init<const vector<int> &>());
    class_<CtrlValueFilter, bases<Filter> >("CtrlValueFilter", init<int, int>());
    class_<ProgFilter, bases<Filter> >("ProgFilter", init<const vector<int> &>());

    class_<Port, bases<Unit> >("Port", init<int>());
    class_<Channel, bases<Unit> >("Channel", init<int>());
    class_<Transpose, bases<Unit> >("Transpose", init<int>());
    class_<Velocity, bases<Unit> >("Velocity", init<float, int>());

    class_<VelocityCurve, bases<Unit> >("VelocityCurve", init<float>());
    class_<VelocityGradient, bases<Unit> >("VelocityGradient", init<int, int, float, float, int>());
    class_<CtrlRange, bases<Unit> >("CtrlRange", init<int, int, int, int, int>());

    class_<GenerateEvent, bases<Unit> >("GenerateEvent", init<int, int, int, int, int>());
    class_<Sanitize, bases<Unit> >("Sanitize", init<>());
    class_<PatchSwitch, bases<Unit> >("PatchSwitch", init<int>());
    class_<Call, bases<Unit> >("Call", init<object>());

    class_<Setup, Setup, noncopyable>("Setup", init<const string &, const string &, const vector<string> &, const vector<string> &>())
        .def("add_patch", &Setup::add_patch)
        .def("set_processing", &Setup::set_processing)
        .def("run", &Setup::run)
        .def("switch_patch", &Setup::switch_patch)
#ifdef ENABLE_TEST
        .def("process", &Setup::process, return_value_policy<reference_existing_object>())
#endif // ENABLE_TEST
    ;
    {
        scope p = class_<Patch>("Patch")
            .def("set_start", &Patch::set_start)
        ;

        class_<Patch::Input, bases<Unit> >("Input");
        class_<Patch::Output, bases<Unit> >("Output");

        class_<Patch::Module>("Module", init<shared_ptr<Unit> >())
            .def("attach", &Patch::Module::attach)
        ;
    }

    class_<vector<int> >("int_vector")
        .def("push_back", &vector<int>::push_back)
    ;
    class_<vector<string> >("string_vector")
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
