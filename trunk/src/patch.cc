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

#include "patch.hh"
#include "units/base.hh"
#include "engine.hh"

#include <algorithm>
#include <sstream>
#include <alloca.h>

#include "util/debug.hh"


namespace Mididings {


template <typename B>
void Patch::Chain::process(B & buf, typename B::Range & range) const
{
    DEBUG_PRINT(Patch::debug_range("Chain in", buf, range));

    // iterate over all modules in this chain
    for (ModuleVector::const_iterator module = _modules.begin(); module != _modules.end(); ++module)
    {
        // run all events through the next module in the chain
        (*module)->process(buf, range);

        if (range.empty()) {
            // the event range became empty, there's nothing left for us to do
            break;
        }
    }

    DEBUG_PRINT(Patch::debug_range("Chain out", buf, range));
}


template <typename B>
void Patch::Fork::process(B & buffer, typename B::Range & range) const
{
    DEBUG_PRINT(Patch::debug_range("Fork in", buffer, range));

    // make a copy of all incoming events, allocated on the stack
    std::size_t num_events = range.size();
    MidiEvent *in_events = static_cast<MidiEvent*>(::alloca(num_events * sizeof(MidiEvent)));
    MidiEvent *p = in_events;
    for (typename B::iterator it = range.begin(); it != range.end(); ++it, ++p) {
        new (p) MidiEvent(*it);
    }

    // remove all incoming events from the buffer
    buffer.erase(range.begin(), range.end());

    // clear range, no events to return so far
    range.set_begin(range.end());

    // iterate over all input events
    for (MidiEvent *ev = in_events; ev != in_events + num_events; ++ev)
    {
        // the range of events returned for the current input event,
        // empty so far
        typename B::Range ev_range(range.end());

        // iterate over all modules in this fork
        for (ModuleVector::const_iterator module = _modules.begin(); module != _modules.end(); ++module)
        {
            // insert one event
            typename B::Iterator it = buffer.insert(ev_range.end(), *ev);
            // the single-event range to be processed in this iteration
            typename B::Range proc_range(it, 1);
            // process event
            (*module)->process(buffer, proc_range);

            if (!proc_range.empty() && ev_range.empty()) {
                // at least one event was returned, we can now set the
                // beginning of range and ev_range if they were empty so far
                if (range.empty()) {
                    range.set_begin(proc_range.begin());
                }
                ev_range.set_begin(proc_range.begin());
            }

            if (_remove_duplicates) {
                // for all events returned in this iteration...
                for (typename B::Iterator it = proc_range.begin(); it != proc_range.end(); ) {
                    // look for previous occurrences that were returned for the
                    // same input event, but from a different module
                    if (std::find(ev_range.begin(), proc_range.begin(), *it) != proc_range.begin()) {
                        // found previous identical event, remove the latest one
                        it = buffer.erase(it);
                    } else {
                        ++it;
                    }
                }
            }
        }

        // destroy the event that was previously placement-constructed
        // on the stack
        ev->~MidiEvent();
    }

    DEBUG_PRINT(Patch::debug_range("Fork out", buffer, range));
}


template <typename B>
void Patch::Single::process(B & buffer, typename B::Range & range) const
{
    DEBUG_PRINT(Patch::debug_range("Single in", buffer, range));

    // iterate over all events in the input range
    for (typename B::Iterator it = range.begin(); it != range.end(); )
    {
        // process event
        if (_unit->process(*it)) {
            // keep this event, continue with next one
            ++it;
        } else {
            if (it == range.begin()) {
                // we're going to erase at the beginning of the event range,
                // so we need to adjust the range to keep it valid
                range.advance_begin(1);
            }
            // remove this event
            it = buffer.erase(it);
        }
    }

    DEBUG_PRINT(Patch::debug_range("Single out", buffer, range));
}


template <typename B>
void Patch::Extended::process(B & buffer, typename B::Range & range) const
{
    DEBUG_PRINT(Patch::debug_range("Extended in", buffer, range));

    // make a copy of the input range
    typename B::Range in_range(range);
    // clear range, no events to return so far
    range.set_begin(range.end());

    // iterate over all events in the input range
    for (typename B::Iterator it = in_range.begin(); it != in_range.end(); )
    {
        // process event
        typename B::Range ret_range = _unit->process(buffer, it);

        if (range.empty() && !ret_range.empty()) {
            // the first event returned marks the beginning of our output range
            range.set_begin(ret_range.begin());
        }

        // the next event to be processed is adjacent to those we just got back
        it = ret_range.end();
    }

    DEBUG_PRINT(Patch::debug_range("Extended out", buffer, range));
}



template <typename B>
void Patch::process(B & buffer, typename B::Range & range) const
{
    DEBUG_PRINT(debug_range("Patch in", buffer, range));

    _module->process(buffer, range);

    DEBUG_PRINT(debug_range("Patch out", buffer, range));
}


template <typename B>
std::string Patch::debug_range(std::string const & str, B const & buffer, typename B::Range const & range)
{
    std::ostringstream os;
    os << str << ": "
       << std::distance(buffer.begin(), range.begin()) << " "
       << std::distance(range.begin(), range.end());
    for (typename B::Iterator it = range.begin(); it != range.end(); ++it) {
        os << " [" << it->type << " " << it->port << " " << it->channel << " " << it->data1 << " " << it->data2 << "]";
    }
    return os.str();
}



// force template instantiations
template void Patch::Chain::process<Patch::EventBufferRT>(EventBufferRT &, EventBufferRT::Range &) const;
template void Patch::Chain::process<Patch::EventBuffer>(EventBuffer &, EventBuffer::Range &) const;
template void Patch::Fork::process<Patch::EventBufferRT>(EventBufferRT &, EventBufferRT::Range &) const;
template void Patch::Fork::process<Patch::EventBuffer>(EventBuffer &, EventBuffer::Range &) const;
template void Patch::Single::process<Patch::EventBufferRT>(EventBufferRT &, EventBufferRT::Range &) const;
template void Patch::Single::process<Patch::EventBuffer>(EventBuffer &, EventBuffer::Range &) const;
template void Patch::Extended::process<Patch::EventBufferRT>(EventBufferRT &, EventBufferRT::Range &) const;
template void Patch::Extended::process<Patch::EventBuffer>(EventBuffer &, EventBuffer::Range &) const;

template void Patch::process(EventBufferRT &, EventBufferRT::Range &) const;
template void Patch::process(EventBuffer &, EventBuffer::Range &) const;


} // Mididings
