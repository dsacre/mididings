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

#include "units.h"
#include "setup.h"

#include <iostream>
#include "util.h"

using namespace std;
using namespace das;


enum VelocityMode {
    VELOCITY_MODE_OFFSET = 1,
    VELOCITY_MODE_MULTIPLY = 2,
    VELOCITY_MODE_FIXED = 3,
};

static inline int apply_velocity(int velocity, float value, VelocityMode mode)
{
    if (velocity == 0)
        return 0;

    switch (mode) {
      case VELOCITY_MODE_OFFSET:
        return std::min(127, std::max(1, velocity + (int)value));
      case VELOCITY_MODE_MULTIPLY:
        return std::min(127, (int)(velocity * value));
      case VELOCITY_MODE_FIXED:
        return (int)value;
      default:
        return 0;
    }
}


bool Velocity::process(MidiEvent & ev)
{
    if (ev.type == MIDI_EVENT_NOTEON)
        ev.note.velocity = apply_velocity(ev.note.velocity, _value, (VelocityMode)_mode);
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
            map_range(ev.note.note, _note_first, _note_last, _value_first, _value_last),
            (VelocityMode)_mode);
    }
    return true;
}


bool ControllerRange::process(MidiEvent & ev)
{
    if (ev.type == MIDI_EVENT_CONTROLLER && ev.ctrl.param == _controller) {
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
    if (value >= 0) return value;
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


bool TriggerEvent::process(MidiEvent & ev)
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


bool SwitchPatch::process(MidiEvent & ev)
{
    TheSetup->switch_patch(get_parameter(_num, ev));
    return false;
}


bool Print::process(MidiEvent & ev)
{
    string s;

    switch (ev.type)
    {
      case MIDI_EVENT_NOTEON:
        s = make_string() << "note on: port " << ev.port << ", channel " << ev.channel
                          << ", note " << ev.note.note << ", velocity " << ev.note.velocity;
        break;

      case MIDI_EVENT_NOTEOFF:
        s = make_string() << "note off: port " << ev.port << ", channel " << ev.channel
                          << ", note " << ev.note.note << ", velocity " << ev.note.velocity;
        break;

      case MIDI_EVENT_CONTROLLER:
        s = make_string() << "control change: port " << ev.port << ", channel " << ev.channel
                          << ", param " << ev.ctrl.param << ", value " << ev.ctrl.value;
        break;
      case MIDI_EVENT_PITCHBEND:
        s = make_string() << "pitch bend: port " << ev.port << ", channel " << ev.channel
                          << ", value " << ev.ctrl.value;
        break;
      case MIDI_EVENT_PGMCHANGE:
        s = make_string() << "program change: port " << ev.port << ", channel " << ev.channel
                          << ", value " << ev.ctrl.value;
        break;
      default:
        s = "unknown event type";
    }

    if (_name.length())
        cout << _name << ": " << s << endl;
    else
        cout << s << endl;

    return true;
}
