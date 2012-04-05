/*
 * mididings
 *
 * Copyright (C) 2008-2012  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef MIDIDINGS_UNITS_UTIL_HH
#define MIDIDINGS_UNITS_UTIL_HH

#include <cmath>
#include <algorithm>


namespace Mididings {
namespace Units {


enum TransformMode {
    TRANSFORM_MODE_OFFSET = 1,
    TRANSFORM_MODE_MULTIPLY = 2,
    TRANSFORM_MODE_FIXED = 3,
    TRANSFORM_MODE_GAMMA = 4,
    TRANSFORM_MODE_CURVE = 5,
};


enum EventAttribute {
    EVENT_ATTRIBUTE_PORT = -1,
    EVENT_ATTRIBUTE_CHANNEL = -2,
    EVENT_ATTRIBUTE_DATA1 = -3,
    EVENT_ATTRIBUTE_DATA2 = -4,
    EVENT_ATTRIBUTE_NOTE = -3,
    EVENT_ATTRIBUTE_VELOCITY = -4,
    EVENT_ATTRIBUTE_CTRL = -3,
    EVENT_ATTRIBUTE_VALUE = -4,
    EVENT_ATTRIBUTE_PROGRAM = -4,
};


inline int apply_transform(int value, float param, TransformMode mode)
{
    switch (mode) {
      case TRANSFORM_MODE_OFFSET:
        return value + (int)param;

      case TRANSFORM_MODE_MULTIPLY:
        return (int)(value * param);

      case TRANSFORM_MODE_FIXED:
        return (int)param;

      case TRANSFORM_MODE_GAMMA:
        if (value > 0) {
            float a = (float)value / 127.f;
            float b = ::powf(a, 1.f / param);
            return std::max(1, (int)::rintf(b * 127.f));
        } else {
            return value;
        }

      case TRANSFORM_MODE_CURVE:
        if (value > 0) {
            if (param != 0) {
                float p = -param;
                float a = ::expf(p * value / 127.f) - 1;
                float b = ::expf(p) - 1;
                return std::max(1, (int)(127.f * a / b));
            } else {
                return value;
            }
        } else {
            return 0;
        }

      default:
        return 0;
    }
}


/*
 * maps the input range [arg_lower ... arg_upper] to the
 * output range [val_lower ... val_upper]
 */
template <typename A, typename V>
V map_range(A arg, A arg_lower, A arg_upper, V val_lower, V val_upper)
{
    if (arg <= arg_lower) {
        return val_lower;
    } else if (arg >= arg_upper) {
        return val_upper;
    } else {
        float dx = arg_upper - arg_lower;
        float dy = val_upper - val_lower;
        return static_cast<V>((dy / dx) * (arg - arg_lower) + val_lower);
    }
}


inline int get_parameter(int value, MidiEvent const & ev)
{
    if (value >= 0) {
        return value;
    }

    switch (value) {
      case EVENT_ATTRIBUTE_PORT:
        return ev.port;
      case EVENT_ATTRIBUTE_CHANNEL:
        return ev.channel;
      case EVENT_ATTRIBUTE_DATA1:
        return ev.data1;
      case EVENT_ATTRIBUTE_DATA2:
        return ev.data2;
      default:
        FAIL();
        return 0;
    }
}


} // Units
} // Mididings


#endif // MIDIDINGS_UNITS_UTIL_HH
