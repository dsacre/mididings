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

#ifndef _UNITS_H
#define _UNITS_H

#include "midi_event.h"
#include "util.h"

#include <vector>
#include <boost/shared_ptr.hpp>


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


class Filter
  : public Unit
{
  public:
    Filter(MidiEventTypes types = MIDI_EVENT_ANY)
      : _types(types) { }
    MidiEventTypes types() const { return _types; }
  private:
    const MidiEventTypes _types;
};


class Modifier
  : public Unit
{
};


class InvertedFilter
  : public Unit
{
  public:
    // parameter must be a filter, but for efficiency,
    // Filter is not exposed to python
    InvertedFilter(boost::shared_ptr<Unit> filter) {
        _filter = boost::dynamic_pointer_cast<Filter>(filter);
        ASSERT(_filter);
    }

    virtual bool process(MidiEvent & ev) {
        return (!(_filter->types() & ev.type) || !_filter->process(ev));
    }

  private:
    boost::shared_ptr<Filter> _filter;
};


class Pass
  : public Unit
{
  public:
    Pass(bool pass)
      : _pass(pass) { }

    virtual bool process(MidiEvent & ev) {
        return _pass;
    }

  private:
    bool _pass;
};


/**************************************************************************/

class TypeFilter
  : public Filter
{
  public:
    TypeFilter(MidiEventTypes types)
      : _types(types) { }

    virtual bool process(MidiEvent & ev) {
        return (ev.type & _types);
    }

  private:
    MidiEventTypes _types;
};


class PortFilter
  : public Filter
{
  public:
    PortFilter(const std::vector<int> ports) {
        _ports = ports;
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
    ChannelFilter(const std::vector<int> channels) {
        _channels = channels;
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
        _lower(lower), _upper(upper) { }

    virtual bool process(MidiEvent & ev) {
        if (ev.type & MIDI_EVENT_NOTE)
            return (ev.note.note >= _lower && ev.note.note <= _upper);
        else
            return true;
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
        _lower(lower), _upper(upper) { }

    virtual bool process(MidiEvent & ev) {
        if (ev.type == MIDI_EVENT_NOTEON)
            return (ev.note.velocity >= _lower && ev.note.velocity <= _upper);
        else
            return true;
    }

  private:
    int _lower, _upper;
};


class ControllerFilter
  : public Filter
{
  public:
    ControllerFilter(int controller)
      : Filter(MIDI_EVENT_CONTROLLER),
        _controller(controller) { }

    virtual bool process(MidiEvent & ev) {
        return (ev.type != MIDI_EVENT_CONTROLLER || ev.ctrl.param == _controller);
    }

  private:
    int _controller;
};


/**************************************************************************/

class Port
  : public Modifier
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
  : public Modifier
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
  : public Modifier
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
  : public Modifier
{
  public:
    Velocity(float value, int mode)
      : _value(value), _mode(mode) { }

    virtual bool process(MidiEvent & ev);

  private:
    float _value;
    int _mode;
};


class VelocityGradient
  : public Modifier
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


class ControllerRange
  : public Unit
{
  public:
    ControllerRange(int controller, int in_min, int in_max, int out_min, int out_max)
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


/**************************************************************************/

class TriggerEvent
  : public Unit
{
  public:
    TriggerEvent(int type, int port, int channel, int data1, int data2)
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


/**************************************************************************/

class SwitchPatch
  : public Unit
{
  public:
    SwitchPatch(int num)
      : _num(num) { }

    virtual bool process(MidiEvent & ev);

  private:
    int _num;
};


#endif // _UNITS_H
