/*
 * mididings
 *
 * Copyright (C) 2007  Dominic Sacré  <dominic.sacre@gmx.de>
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
#include <boost/python/ptr.hpp>

#ifdef ENABLE_TEST
#include <boost/python/enum.hpp>
#include <boost/python/operators.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#endif // ENABLE_TEST

#include <vector>
#include <string>

#include "setup.h"
#include "patch.h"
#include "units.h"

using namespace boost::python;
using namespace boost;
using namespace std;


class PythonCall
  : public Call
{
  public:
    PythonCall(object fun)
      : _fun(fun)
    {
    }

    bool process(MidiEvent & ev) {
        //cout << ev.type << endl;
        _fun(ptr(&ev));
        //cout << ev.type << endl;
        return true;
    }

  private:
    object _fun;
};


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
    class_<InvertedFilter, bases<Unit> >("InvertedFilter", init<shared_ptr<Unit> >());

    class_<TypeFilter, bases<Unit> >("TypeFilter", init<int>());

    class_<PortFilter, bases<Unit> >("PortFilter", init<const vector<int> &>());
    class_<ChannelFilter, bases<Unit> >("ChannelFilter", init<const vector<int> &>());
    class_<KeyFilter, bases<Unit> >("KeyFilter", init<int, int>());
    class_<VelocityFilter, bases<Unit> >("VelocityFilter", init<int, int>());
    class_<ControllerFilter, bases<Unit> >("ControllerFilter", init<int>());

    class_<Port, bases<Unit> >("Port", init<int>());
    class_<Channel, bases<Unit> >("Channel", init<int>());
    class_<Transpose, bases<Unit> >("Transpose", init<int>());
    class_<Velocity, bases<Unit> >("Velocity", init<float, int>());

    class_<VelocityGradient, bases<Unit> >("VelocityGradient", init<int, int, float, float, int>());
    class_<ControllerRange, bases<Unit> >("ControllerRange", init<int, int, int, int, int>());

    class_<TriggerEvent, bases<Unit> >("TriggerEvent", init<int, int, int, int, int>());
    class_<SwitchPatch, bases<Unit> >("SwitchPatch", init<int>());
    class_<Print, bases<Unit> >("Print", init<string>());
    class_<PythonCall, bases<Unit> >("Call", init<object>());

    class_<Setup, noncopyable>("Setup", init<string, string, int, int, vector<string>, vector<string> >())
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

#ifdef ENABLE_TEST
    enum_<MidiEventType>("MidiEventType")
        .value("NONE", MIDI_EVENT_NONE)
        .value("NOTEON", MIDI_EVENT_NOTEON)
        .value("NOTEOFF", MIDI_EVENT_NOTEOFF)
        .value("NOTE", MIDI_EVENT_NOTE)
        .value("CONTROLLER", MIDI_EVENT_CONTROLLER)
        .value("PITCHBEND", MIDI_EVENT_PITCHBEND)
        .value("PGMCHANGE", MIDI_EVENT_PGMCHANGE)
        .value("ANY", MIDI_EVENT_ANY)
    ;
#endif // ENABLE_TEST
    class_<MidiEvent>("MidiEvent")
//        .def_readwrite("type", &MidiEvent::type)
        .add_property("type", &midi_event_get_type, &midi_event_set_type)
        .def_readwrite("port", &MidiEvent::port)
        .def_readwrite("channel", &MidiEvent::channel)
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
