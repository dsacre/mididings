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

#include "units.hh"
#include "engine.hh"

#include <cmath>


enum VelocityMode {
    VELOCITY_MODE_OFFSET = 1,
    VELOCITY_MODE_MULTIPLY = 2,
    VELOCITY_MODE_FIXED = 3,
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


bool VelocityCurve::process(MidiEvent & ev)
{
    if (ev.type == MIDI_EVENT_NOTEON) {
        float x = (float)ev.note.velocity / 127.0f;
        float y = powf(x, 1.0f / _gamma);
        ev.note.velocity = (int)rintf(y * 127.0f);
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
        float dx = arg_upper - arg_lower;
        float dy = val_upper - val_lower;
        value = (V)((dy / dx) * (arg - arg_lower) + val_lower);
    }

    return value;
}


bool VelocityGradient::process(MidiEvent & ev)
{
    if (ev.type == MIDI_EVENT_NOTEON) {
        ev.note.velocity = apply_velocity(ev.note.velocity,
                map_range(ev.note.note, _note_lower, _note_upper, _value_lower, _value_upper),
                (VelocityMode)_mode);
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

static inline int get_parameter(int value, const MidiEvent & ev)
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

    ev = ev_new;

    return true;
}


bool Sanitize::process(MidiEvent & ev)
{
    return TheEngine->sanitize_event(ev);
}


bool PatchSwitch::process(MidiEvent & ev)
{
    TheEngine->switch_patch(get_parameter(_num, ev)/*, ev*/);
    return false;
}


bool Call::process(MidiEvent & ev)
{
    if (!_async) {
        return TheEngine->call_now(_fun, ev);
    }
    else {
        TheEngine->call_deferred(_fun, ev);
        return _cont;
    }
}
