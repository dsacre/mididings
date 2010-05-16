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

#ifndef _UNITS_MODIFIERS_HH
#define _UNITS_MODIFIERS_HH

#include "units_base.hh"
#include "units_util.hh"

#include <vector>


class Port
  : public Unit
{
  public:
    Port(int port)
      : _port(port)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
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
      : _channel(channel)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
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
      : _offset(offset)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
        if (ev.type & (MIDI_EVENT_NOTEON | MIDI_EVENT_NOTEOFF))
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
    Velocity(float param, int mode)
      : _param(param)
      , _mode(mode)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
        if (ev.type == MIDI_EVENT_NOTEON && ev.note.velocity > 0) {
            ev.note.velocity = apply_transform(ev.note.velocity, _param, (TransformMode)_mode);
        }
        return true;
    }

  private:
    float _param;
    int _mode;
};


class VelocitySlope
  : public Unit
{
  public:
    VelocitySlope(std::vector<int> notes, std::vector<float> params, int mode)
      : _notes(notes)
      , _params(params)
      , _mode(mode)
    {
        ASSERT(notes.size() == params.size());
        ASSERT(notes.size() > 1);
        for (unsigned int n = 0; n < notes.size() - 1; ++n) {
            ASSERT(notes[n] <= notes[n + 1]);
        }
    }

    virtual bool process(MidiEvent & ev)
    {
        if (ev.type == MIDI_EVENT_NOTEON && ev.note.velocity > 0) {
            unsigned int n = 0;
            while (n < _notes.size() - 2 && _notes[n + 1] < ev.note.note) ++n;

            ev.note.velocity = apply_transform(
                ev.note.velocity,
                map_range(ev.note.note, _notes[n], _notes[n + 1], _params[n], _params[n + 1]),
                (TransformMode)_mode
            );
        }
        return true;
    }

  private:
    std::vector<int> _notes;
    std::vector<float> _params;
    int _mode;
};


class CtrlMap
  : public Unit
{
  public:
    CtrlMap(int ctrl_in, int ctrl_out)
      : _ctrl_in(ctrl_in)
      , _ctrl_out(ctrl_out)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
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
      : _controller(controller)
      , _in_min(in_min), _in_max(in_max)
      , _out_min(out_min), _out_max(out_max)
    {
        ASSERT(in_min < in_max);
    }

    virtual bool process(MidiEvent & ev)
    {
        if (ev.type == MIDI_EVENT_CTRL && ev.ctrl.param == _controller) {
            ev.ctrl.value = map_range(ev.ctrl.value, _in_min, _in_max, _out_min, _out_max);
        }
        return true;
    }

  private:
    int _controller;
    int _in_min, _in_max;
    int _out_min, _out_max;
};


class CtrlCurve
  : public Unit
{
  public:
    CtrlCurve(int controller, float param, int mode)
      : _controller(controller)
      , _param(param)
      , _mode(mode)
    {
    }

    virtual bool process(MidiEvent & ev)
    {
        if (ev.type == MIDI_EVENT_CTRL && ev.ctrl.param == _controller) {
            ev.ctrl.value = apply_transform(ev.ctrl.value, _param, (TransformMode)_mode);
        }
        return true;
    }

  private:
    int _controller;
    float _param;
    int _mode;
};


#endif // _UNITS_MODIFIERS_HH
