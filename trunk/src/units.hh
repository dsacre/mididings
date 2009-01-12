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

#ifndef _UNITS_HH
#define _UNITS_HH

#include "midi_event.hh"
#include "patch.hh"

#include <vector>
#include <boost/shared_ptr.hpp>
#include <boost/python/object.hpp>

#include "util/debug.hh"


class Unit
{
  public:
    Unit() {
        DEBUG_FN();
    }

    virtual ~Unit() {
        DEBUG_FN();
    }

    virtual bool process(MidiEvent & ev) = 0;
};


class UnitEx
{
  public:
    UnitEx() {
        DEBUG_FN();
    }

    virtual ~UnitEx() {
        DEBUG_FN();
    }

    virtual Patch::EventRange process(Patch::Events & buf, Patch::EventIter it) = 0;
};



class Filter
  : public Unit
{
  public:
    Filter(MidiEventTypes types)
      : _types(types)
    {
    }

    virtual bool process(MidiEvent & ev) {
        return match_type(ev);
    }

    MidiEventTypes types() const {
        return _types;
    }

  protected:
    bool match_type(MidiEvent & ev) {
        return (ev.type & _types);
    }

  private:
    const MidiEventTypes _types;
};


class InvertedFilter
  : public Filter
{
  public:
    InvertedFilter(boost::shared_ptr<Filter> filter, bool ignore_types)
      : Filter(MIDI_EVENT_ANY)
      , _filter(filter)
      , _ignore_types(ignore_types)
    {
    }

    virtual bool process(MidiEvent & ev) {
        if (_ignore_types) {
            return !_filter->process(ev);
        } else {
            return !(_filter->types() & ev.type) || !_filter->process(ev);
        }
    }

  private:
    boost::shared_ptr<Filter> _filter;
    bool _ignore_types;
};


class Pass
  : public Unit
{
  public:
    Pass(bool pass)
      : _pass(pass) { }

    virtual bool process(MidiEvent & /*ev*/) {
        return _pass;
    }

  private:
    bool _pass;
};


/*
 * filters
 */

class PortFilter
  : public Filter
{
  public:
    PortFilter(const std::vector<int> & ports)
      : Filter(MIDI_EVENT_ANY), _ports(ports)
    {
    }

    virtual bool process(MidiEvent & ev) {
        for (std::vector<int>::iterator i = _ports.begin(); i != _ports.end(); ++i) {
            if (ev.port == *i) return true;
        }
        return false;
    }

  private:
    std::vector<int> _ports;
};


class ChannelFilter
  : public Filter
{
  public:
    ChannelFilter(const std::vector<int> & channels)
      : Filter(MIDI_EVENT_ANY), _channels(channels)
    {
    }

    virtual bool process(MidiEvent & ev) {
        for (std::vector<int>::iterator i = _channels.begin(); i != _channels.end(); ++i) {
            if (ev.channel == *i) return true;
        }
        return false;
    }

  private:
    std::vector<int> _channels;
};


class KeyFilter
  : public Filter
{
  public:
    KeyFilter(int lower, int upper)
      : Filter(MIDI_EVENT_NOTE),
        _lower(lower), _upper(upper)
    {
    }

    virtual bool process(MidiEvent & ev) {
        if (!match_type(ev)) return true;
        return (ev.note.note >= _lower && ev.note.note <= _upper);
    }

  private:
    int _lower, _upper;
};


class VelocityFilter
  : public Filter
{
  public:
    VelocityFilter(int lower, int upper)
      : Filter(MIDI_EVENT_NOTEON),
        _lower(lower), _upper(upper)
    {
    }

    virtual bool process(MidiEvent & ev) {
        if (!match_type(ev)) return true;
        return (ev.note.velocity >= _lower && ev.note.velocity <= _upper);
    }

  private:
    int _lower, _upper;
};


class CtrlFilter
  : public Filter
{
  public:
    CtrlFilter(const std::vector<int> & ctrls)
      : Filter(MIDI_EVENT_CTRL),
        _ctrls(ctrls)
    {
    }

    virtual bool process(MidiEvent & ev) {
        if (!match_type(ev)) return true;
        for (std::vector<int>::iterator i = _ctrls.begin(); i != _ctrls.end(); ++i) {
            if (ev.ctrl.param == *i) return true;
        }
        return false;
    }

  private:
    std::vector<int> _ctrls;
};


class CtrlValueFilter
  : public Filter
{
  public:
    CtrlValueFilter(int lower, int upper)
      : Filter(MIDI_EVENT_CTRL),
        _lower(lower), _upper(upper)
    {
    }

    virtual bool process(MidiEvent & ev) {
        if (!match_type(ev)) return true;
        return ((ev.ctrl.value >= _lower && ev.ctrl.value <= _upper) || (ev.ctrl.value == _lower && !_upper));
    }

  private:
    int _lower, _upper;
};


class ProgFilter
  : public Filter
{
  public:
    ProgFilter(const std::vector<int> & progs)
      : Filter(MIDI_EVENT_PROGRAM),
        _progs(progs)
    {
    }

    virtual bool process(MidiEvent & ev) {
        if (!match_type(ev)) return true;
        for (std::vector<int>::iterator i = _progs.begin(); i != _progs.end(); ++i) {
            if (ev.ctrl.value == *i) return true;
        }
        return false;
    }

  private:
    std::vector<int> _progs;
};


/*
 * modifiers
 */

class Port
  : public Unit
{
  public:
    Port(int port)
      : _port(port) { }

    virtual bool process(MidiEvent & ev) {
        ev.port = _port;
        return true;
    }

  private:
    int _port;
};


class Channel
  : public Unit
{
  public:
    Channel(int channel)
      : _channel(channel) { }

    virtual bool process(MidiEvent & ev) {
        ev.channel = _channel;
        return true;
    }

  private:
    int _channel;
};


class Transpose
  : public Unit
{
  public:
    Transpose(int offset)
      : _offset(offset) { }

    virtual bool process(MidiEvent & ev) {
        if (ev.type & MIDI_EVENT_NOTE)
            ev.note.note += _offset;
        return true;
    }

  private:
    int _offset;
};



class Velocity
  : public Unit
{
  public:
    Velocity(float value, int mode)
      : _value(value), _mode(mode) { }

    virtual bool process(MidiEvent & ev);

  private:
    float _value;
    int _mode;
};


class VelocityCurve
  : public Unit
{
  public:
    VelocityCurve(float gamma)
      : _gamma(gamma) { }

    virtual bool process(MidiEvent & ev);

  private:
    float _gamma;
};


class VelocityGradient
  : public Unit
{
  public:
    VelocityGradient(int note_lower, int note_upper,
                 float value_lower, float value_upper,
                 int mode)
      : _note_lower(note_lower),
        _note_upper(note_upper),
        _value_lower(value_lower),
        _value_upper(value_upper),
        _mode(mode)
    {
        ASSERT(note_lower < note_upper);
    }

    virtual bool process(MidiEvent & ev);

  private:
    int _note_lower, _note_upper;
    float _value_lower, _value_upper;
    int _mode;
};


class CtrlMap
  : public Unit
{
  public:
    CtrlMap(int ctrl_in, int ctrl_out)
      : _ctrl_in(ctrl_in),
        _ctrl_out(ctrl_out)
    {
    }

    virtual bool process(MidiEvent & ev) {
        if (ev.type == MIDI_EVENT_CTRL && ev.ctrl.param == _ctrl_in) {
            ev.ctrl.param = _ctrl_out;
        }
        return true;
    }

  private:
    int _ctrl_in;
    int _ctrl_out;
};


class CtrlRange
  : public Unit
{
  public:
    CtrlRange(int controller, int out_min, int out_max, int in_min, int in_max)
      : _controller(controller),
        _in_min(in_min), _in_max(in_max),
        _out_min(out_min), _out_max(out_max)
    {
        ASSERT(in_min < in_max);
    }

    virtual bool process(MidiEvent & ev);

  private:
    int _controller;
    int _in_min, _in_max;
    int _out_min, _out_max;
};


/*
 * misc
 */

class GenerateEvent
  : public Unit
{
  public:
    GenerateEvent(int type, int port, int channel, int data1, int data2)
      : _type((MidiEventType)type),
        _port(port),
        _channel(channel),
        _data1(data1),
        _data2(data2)
    {
    }

    virtual bool process(MidiEvent & ev);

  private:
    MidiEventType _type;
    int _port;
    int _channel;
    int _data1;
    int _data2;
};


class Sanitize
  : public Unit
{
  public:
    Sanitize() { }

    virtual bool process(MidiEvent & ev);
};


class PatchSwitch
  : public Unit
{
  public:
    PatchSwitch(int num)
      : _num(num) { }

    virtual bool process(MidiEvent & ev);

  private:
    int _num;
};


class Call
  : public UnitEx
{
  public:
    Call(boost::python::object fun, bool async, bool cont)
      : _fun(fun),
        _async(async),
        _cont(cont)
    {
    }

    virtual Patch::EventRange process(Patch::Events & buf, Patch::EventIter it);

  private:
    boost::python::object _fun;
    bool _async;
    bool _cont;
};



#endif // _UNITS_HH
