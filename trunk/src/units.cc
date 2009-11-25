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

#include "units.hh"
#include "engine.hh"

#include <cmath>


enum VelocityMode {
    VELOCITY_MODE_OFFSET = 1,
    VELOCITY_MODE_MULTIPLY = 2,
    VELOCITY_MODE_FIXED = 3,
    VELOCITY_MODE_GAMMA = 4,
};

static inline int apply_velocity(int velocity, float value, VelocityMode mode)
{
    if (velocity == 0) {
        return 0;
    }

    switch (mode) {
      case VELOCITY_MODE_OFFSET:
        return velocity + (int)value;

      case VELOCITY_MODE_MULTIPLY:
        return (int)(velocity * value);

      case VELOCITY_MODE_FIXED:
        return (int)value;

      case VELOCITY_MODE_GAMMA:
        if (velocity > 0) {
            float x = (float)velocity / 127.0f;
            float y = powf(x, 1.0f / value);
            return (int)rintf(y * 127.0f);
        } else {
            return velocity;
        }
      default:
        return 0;
    }
}


bool Velocity::process(MidiEvent & ev)
{
    if (ev.type == MIDI_EVENT_NOTEON) {
        ev.note.velocity = apply_velocity(ev.note.velocity, _value, (VelocityMode)_mode);
    }
    return true;
}


/*
 * maps the input range [arg_lower ... arg_upper] to the
 * output range [val_lower ... val_upper]
 */
template <typename A, typename V>
static V map_range(A arg, A arg_lower, A arg_upper, V val_lower, V val_upper)
{
    V value;

    if (arg <= arg_lower) {
        value = val_lower;
    } else if (arg >= arg_upper) {
        value = val_upper;
    } else {
        A dx = arg_upper - arg_lower;
        V dy = val_upper - val_lower;
        value = (V)((dy / dx) * (arg - arg_lower) + val_lower);
    }

    return value;
}


bool VelocitySlope::process(MidiEvent & ev)
{
    if (ev.type == MIDI_EVENT_NOTEON) {
        unsigned int n = 0;
        while (n < _notes.size() - 2 && _notes[n + 1] < ev.note.note) ++n;

        ev.note.velocity = apply_velocity(
            ev.note.velocity,
            map_range(ev.note.note, _notes[n], _notes[n + 1], _values[n], _values[n + 1]),
            (VelocityMode)_mode
        );
    }
    return true;
}


bool CtrlRange::process(MidiEvent & ev)
{
    if (ev.type == MIDI_EVENT_CTRL && ev.ctrl.param == _controller) {
        ev.ctrl.value = map_range(ev.ctrl.value, _in_min, _in_max, _out_min, _out_max);
    }
    return true;
}



enum ParameterIndices {
    PARAMETER_PORT = -1,
    PARAMETER_CHANNEL = -2,
    PARAMETER_DATA1 = -3,
    PARAMETER_DATA2 = -4,
};

static inline int get_parameter(int value, MidiEvent const & ev)
{
    if (value >= 0) {
        return value;
    }

    switch (value) {
      case PARAMETER_PORT:
        return ev.port;
      case PARAMETER_CHANNEL:
        return ev.channel;
      case PARAMETER_DATA1:
        return ev.data1;
      case PARAMETER_DATA2:
        return ev.data2;
      default:
        FAIL();
        return 0;
    }
}


bool GenerateEvent::process(MidiEvent & ev)
{
    MidiEvent ev_new;

    ev_new.type = _type;
    ev_new.port = get_parameter(_port, ev);
    ev_new.channel = get_parameter(_channel, ev);
    ev_new.data1 = get_parameter(_data1, ev);
    ev_new.data2 = get_parameter(_data2, ev);
    ev_new.frame = ev.frame;

    ev = ev_new;

    return true;
}


bool GenerateSysEx::process(MidiEvent & ev)
{
    ev.type = MIDI_EVENT_SYSEX;
    ev.port = get_parameter(_port, ev);
    ev.channel = 0;
    ev.data1 = 0;
    ev.data2 = 0;
    ev.sysex.reset(&_sysex, MidiEvent::null_deleter());

    return true;
}


bool Sanitize::process(MidiEvent & ev)
{
    return TheEngine->sanitize_event(ev);
}


bool SceneSwitch::process(MidiEvent & ev)
{
    TheEngine->switch_scene(get_parameter(_num, ev));
    return false;
}


Patch::EventRange Call::process(Patch::Events & buf, Patch::EventIter it)
{
    PythonCaller & c = TheEngine->python_caller();

    if (_async) {
        return c.call_deferred(buf, it, _fun, _cont);
    } else {
        return c.call_now(buf, it, _fun);
    }
}
