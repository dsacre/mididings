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

#include "config.hh"
#include "engine.hh"
#include "patch.hh"
#include "send_midi.hh"
#include "midi_event.hh"
#include "backend/base.hh"
#include "units/base.hh"
#include "units/engine.hh"
#include "units/filters.hh"
#include "units/modifiers.hh"
#include "units/generators.hh"
#include "units/call.hh"
#include "curious_alloc.hh"

#include "util/python.hh"
#include "util/python_sequence_converters.hh"
#include "util/python_bytes_converters.hh"
#include "util/python_dict_converters.hh"
#include "util/counted_objects.hh"

#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python/class.hpp>
#include <boost/python/enum.hpp>
#include <boost/python/scope.hpp>
#include <boost/python/operators.hpp>
#include <boost/python/tuple.hpp>
#include <boost/python/call_method.hpp>
#include <boost/python/return_value_policy.hpp>
#include <boost/python/return_by_value.hpp>

#include <vector>
#include <map>
#include <string>
#include <cstdlib>

#ifdef ENABLE_DEBUG_STATS
#include <iostream>
#include <iomanip>
#include "util/string.hh"
#endif


namespace mididings {


#ifdef ENABLE_DEBUG_STATS

template <typename T>
std::string alloc_stats(std::string const & name) {
    std::size_t allocated = das::counted_objects<T>::allocated();
    std::size_t deallocated = das::counted_objects<T>::deallocated();
    std::size_t leaks = allocated - deallocated;
    return das::make_string() << std::left << std::setw(20) << (name + ":")
                              << std::setw(8) << allocated << " " << leaks;
}

template <typename T>
std::string curious_alloc_stats(std::string const & name) {
    return das::make_string() << std::left << std::setw(20) << (name + ": ")
                              << std::setw(8)
                              << curious_alloc_base<T>::max_utilization()
                              << " "
                              << curious_alloc_base<T>::fallback_count();
}

void unload() {
#ifdef ENABLE_BENCHMARK
    std::cerr << '\n'
              << std::left << std::setw(20) << "number of cycles:"
              << Engine::num_cycles() << '\n'
              << std::left << std::setw(20) << "mean duration:"
              << Engine::cycle_duration_mean() << " µs" << '\n'
              << std::left << std::setw(20) << "max duration:"
              << Engine::cycle_duration_max() << " µs" << std::endl;
#endif

    std::cerr << '\n'
              << alloc_stats<Engine>("Engine") << '\n'
              << alloc_stats<Patch>("Patch") << '\n'
              << alloc_stats<Patch::Module>("Patch::Module") << '\n'
              << alloc_stats<units::Unit>("units::Unit") << '\n'
              << alloc_stats<units::UnitEx>("units::UnitEx") << '\n'
              << alloc_stats<MidiEvent>("MidiEvent") << '\n'
              << alloc_stats<SysExData>("SysExData") << '\n'
              << curious_alloc_stats<MidiEvent>("MidiEvent alloc")
              << std::endl;
}

#endif // ENABLE_DEBUG_STATS


class EngineWrap
  : public Engine
{
  public:
    EngineWrap(PyObject *self,
               std::string const & backend_name,
               std::string const & client_name,
               backend::PortNameVector const & in_ports,
               backend::PortNameVector const & out_ports,
               bool verbose)
      : Engine(backend_name, client_name, in_ports, out_ports, verbose)
      , _self(self)
    { }

    void scene_switch_callback(int scene, int subscene) {
        das::python::scoped_gil_lock gil;
        try {
            boost::python::call_method<void>(_self,
                                "scene_switch_callback", scene, subscene);
        } catch (boost::python::error_already_set &) {
            PyErr_Print();
        }
    }

  private:
    PyObject *_self;
};


MidiEvent buffer_to_midi_event(std::vector<unsigned char> const & buffer,
                               int port, uint64_t frame) {
    return backend::buffer_to_midi_event(
                            &buffer.front(), buffer.size(), port, frame);
}

boost::python::tuple midi_event_to_buffer(MidiEvent const & ev) {
    std::vector<unsigned char> buffer(256, 0);
    std::size_t len = buffer.size();
    int port;
    uint64_t frame;
    backend::midi_event_to_buffer(ev, &buffer.front(), len, port, frame);
    buffer.resize(len);
    return boost::python::make_tuple(buffer, port, frame);
}



BOOST_PYTHON_MODULE(_mididings)
{
    namespace bp = boost::python;
    using bp::class_;
    using bp::bases;
    using bp::init;
    using bp::def;
    using bp::enum_;
    using boost::noncopyable;
    using namespace units;

    PyEval_InitThreads();

#ifdef VERSION
    bp::scope().attr("__version__") = VERSION;
#else
    bp::scope().attr("__version__") = "(unknown)";
#endif


    // list of supported backends
    def("available_backends", &backend::available,
        bp::return_value_policy<bp::return_by_value>());

    def("buffer_to_midi_event", buffer_to_midi_event);
    def("midi_event_to_buffer", midi_event_to_buffer);


    // simple MIDI send function, works with no engine running
    def("send_midi", &send_midi);


    // main engine class, derived from in python
    class_<Engine, EngineWrap, noncopyable>(
        "Engine",
        init<std::string const &, std::string const &,
             std::vector<std::string> const &,
             std::vector<std::string> const &,
             bool>())
        .def("connect_ports", &Engine::connect_ports)
        .def("add_scene", &Engine::add_scene)
        .def("set_processing", &Engine::set_processing)
        .def("start", &Engine::start)
        .def("switch_scene", &Engine::switch_scene)
        .def("current_scene", &Engine::current_scene)
        .def("current_subscene", &Engine::current_subscene)
        .def("process_event", &Engine::process_event)
        .def("output_event", &Engine::output_event)
        .def("time", &Engine::time)
    ;


    // patch class, derived from in python
    {
        bp::scope patch_scope = class_<Patch, noncopyable>(
            "Patch", init<Patch::ModulePtr>());

        class_<Patch::Module, noncopyable>(
            "Module", bp::no_init);
        class_<Patch::Chain, bases<Patch::Module>, noncopyable>(
            "Chain", init<Patch::ModuleVector>());
        class_<Patch::Fork, bases<Patch::Module>, noncopyable>(
            "Fork", init<Patch::ModuleVector, bool>());
        class_<Patch::Single, bases<Patch::Module>, noncopyable>(
            "Single", init<boost::shared_ptr<Unit> >());
        class_<Patch::Extended, bases<Patch::Module>, noncopyable>(
            "Extended", init<boost::shared_ptr<UnitEx> >());
    }


    // midi event type enum
    enum_<MidiEventTypeEnum>("MidiEventType")
        .value("NONE", MIDI_EVENT_NONE)
        .value("NOTEON", MIDI_EVENT_NOTEON)
        .value("NOTEOFF", MIDI_EVENT_NOTEOFF)
        .value("NOTE", MIDI_EVENT_NOTE)
        .value("CTRL", MIDI_EVENT_CTRL)
        .value("PITCHBEND", MIDI_EVENT_PITCHBEND)
        .value("AFTERTOUCH", MIDI_EVENT_AFTERTOUCH)
        .value("POLY_AFTERTOUCH", MIDI_EVENT_POLY_AFTERTOUCH)
        .value("PROGRAM", MIDI_EVENT_PROGRAM)
        .value("SYSEX", MIDI_EVENT_SYSEX)
        .value("SYSCM_QFRAME", MIDI_EVENT_SYSCM_QFRAME)
        .value("SYSCM_SONGPOS", MIDI_EVENT_SYSCM_SONGPOS)
        .value("SYSCM_SONGSEL", MIDI_EVENT_SYSCM_SONGSEL)
        .value("SYSCM_TUNEREQ", MIDI_EVENT_SYSCM_TUNEREQ)
        .value("SYSCM", MIDI_EVENT_SYSCM)
        .value("SYSRT_CLOCK", MIDI_EVENT_SYSRT_CLOCK)
        .value("SYSRT_START", MIDI_EVENT_SYSRT_START)
        .value("SYSRT_CONTINUE", MIDI_EVENT_SYSRT_CONTINUE)
        .value("SYSRT_STOP", MIDI_EVENT_SYSRT_STOP)
        .value("SYSRT_SENSING", MIDI_EVENT_SYSRT_SENSING)
        .value("SYSRT_RESET", MIDI_EVENT_SYSRT_RESET)
        .value("SYSRT", MIDI_EVENT_SYSRT)
        .value("SYSTEM", MIDI_EVENT_SYSTEM)
        .value("DUMMY", MIDI_EVENT_DUMMY)
        .value("ANY", MIDI_EVENT_ANY)
    ;

    // midi event class, derived from in python
    class_<MidiEvent>("MidiEvent")
        .def_readwrite("type_", &MidiEvent::type)
        .def_readwrite("port_", &MidiEvent::port)
        .def_readwrite("channel_", &MidiEvent::channel)
        .def_readwrite("data1", &MidiEvent::data1)
        .def_readwrite("data2", &MidiEvent::data2)
        .def_readwrite("sysex_", &MidiEvent::sysex)
        .def(bp::self == bp::self)
        .def(bp::self != bp::self)
        .enable_pickling()
    ;


    // unit base classes
    class_<Unit, noncopyable>("Unit", bp::no_init);
    class_<UnitEx, noncopyable>("UnitEx", bp::no_init);
    class_<Filter, bases<Unit>, noncopyable>("Filter", bp::no_init);

    // base
    class_<Pass, bases<Unit>, noncopyable>(
        "Pass", init<bool>());
    class_<TypeFilter, bases<Filter>, noncopyable>(
        "TypeFilter", init<MidiEventType>());
    class_<InvertedFilter, bases<Filter>, noncopyable>(
        "InvertedFilter", init<boost::shared_ptr<Filter>, bool>());

    // filters
    class_<PortFilter, bases<Filter>, noncopyable>(
        "PortFilter", init<std::vector<int> const &>());
    class_<ChannelFilter, bases<Filter>, noncopyable>(
        "ChannelFilter", init<std::vector<int> const &>());
    class_<KeyFilter, bases<Filter>, noncopyable>(
        "KeyFilter", init<int, int, std::vector<int> const &>());
    class_<VelocityFilter, bases<Filter>, noncopyable>(
        "VelocityFilter", init<int, int>());
    class_<CtrlFilter, bases<Filter>, noncopyable>(
        "CtrlFilter", init<std::vector<int> const &>());
    class_<CtrlValueFilter, bases<Filter>, noncopyable>(
        "CtrlValueFilter", init<int, int>());
    class_<ProgramFilter, bases<Filter>, noncopyable>(
        "ProgramFilter", init<std::vector<int> const &>());
    class_<SysExFilter, bases<Filter>, noncopyable>(
        "SysExFilter", init<SysExDataConstPtr const &, bool>());

    // modifiers
    class_<Port, bases<Unit>, noncopyable>(
        "Port", init<int>());
    class_<Channel, bases<Unit>, noncopyable>(
        "Channel", init<int>());
    class_<Transpose, bases<Unit>, noncopyable>(
        "Transpose", init<int>());
    class_<Velocity, bases<Unit>, noncopyable>(
        "Velocity", init<float, TransformMode>());
    class_<VelocitySlope, bases<Unit>, noncopyable>(
        "VelocitySlope", init<std::vector<int> const &,
                              std::vector<float> const &, TransformMode>());
    class_<CtrlMap, bases<Unit>, noncopyable>(
        "CtrlMap", init<int, int>());
    class_<CtrlRange, bases<Unit>, noncopyable>(
        "CtrlRange", init<int, int, int, int, int>());
    class_<CtrlCurve, bases<Unit>, noncopyable>(
        "CtrlCurve", init<int, float, TransformMode>());
    class_<PitchbendRange, bases<Unit>, noncopyable>(
        "PitchbendRange", init<int, int, int, int>());

    // generators
    class_<Generator, bases<Unit>, noncopyable>(
        "Generator", init<MidiEventType, int, int, int, int>());
    class_<SysExGenerator, bases<Unit>, noncopyable>(
        "SysExGenerator", init<int, SysExDataConstPtr const &>());

    // engine
    class_<Sanitize, bases<UnitEx>, noncopyable>(
        "Sanitize", init<>());
    class_<SceneSwitch, bases<UnitEx>, noncopyable>(
        "SceneSwitch", init<int, int>());
    class_<SubSceneSwitch, bases<UnitEx>, noncopyable>(
        "SubSceneSwitch", init<int, int, bool>());

    // call
    class_<Call, bases<UnitEx>, noncopyable>(
        "Call", init<bp::object, bool, bool>());


    enum_<TransformMode>("TransformMode")
        .value("OFFSET", TRANSFORM_MODE_OFFSET)
        .value("MULTIPLY", TRANSFORM_MODE_MULTIPLY)
        .value("FIXED", TRANSFORM_MODE_FIXED)
        .value("GAMMA", TRANSFORM_MODE_GAMMA)
        .value("CURVE", TRANSFORM_MODE_CURVE)
    ;

    enum_<EventAttribute>("EventAttribute")
        .value("PORT", EVENT_ATTRIBUTE_PORT)
        .value("CHANNEL", EVENT_ATTRIBUTE_CHANNEL)
        .value("DATA1", EVENT_ATTRIBUTE_DATA1)
        .value("DATA2", EVENT_ATTRIBUTE_DATA2)
        .value("NOTE", EVENT_ATTRIBUTE_NOTE)
        .value("VELOCITY", EVENT_ATTRIBUTE_VELOCITY)
        .value("CTRL", EVENT_ATTRIBUTE_CTRL)
        .value("VALUE", EVENT_ATTRIBUTE_VALUE)
        .value("PROGRAM", EVENT_ATTRIBUTE_PROGRAM)
    ;


    // register to/from-python converters for various types
    das::python::from_sequence_converter<std::vector<int> >();
    das::python::from_sequence_converter<std::vector<float> >();
    das::python::from_sequence_converter<std::vector<unsigned char> >();
    das::python::to_list_converter<std::vector<unsigned char> >();

    das::python::from_sequence_converter<std::vector<std::string> >();
    das::python::to_list_converter<std::vector<std::string> >();

    das::python::from_sequence_converter<std::vector<MidiEvent> >();
    das::python::to_list_converter<std::vector<MidiEvent> >();

    das::python::from_sequence_converter<std::vector<Patch::ModulePtr> >();

    das::python::from_bytearray_converter<SysExData, SysExDataConstPtr>();
    das::python::to_bytearray_converter<SysExData, SysExDataConstPtr>();

    das::python::from_dict_converter<backend::PortConnectionMap>();


#ifdef ENABLE_DEBUG_STATS
    std::atexit(unload);
#endif
}


} // mididings
