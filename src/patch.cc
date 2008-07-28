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

#include "patch.hh"
#include "units.hh"
#include "engine.hh"

#include <algorithm>
#include <iterator>

#include "util/debug.hh"
#include "util/string.hh"


Patch::EventIterRange Patch::Chain::process(Events & buf, EventIterRange r)
{
    DEBUG_PRINT(Patch::debug_range("Chain in", buf, r));

    for (ModuleVector::iterator m = _modules.begin(); m != _modules.end(); ++m)
    {
        if (r.empty()) {
            // nothing to do
            break;
        }

        r = (*m)->process(buf, r);
    }

    DEBUG_PRINT(Patch::debug_range("Chain out", buf, r));

    return r;
}

#if 0

Patch::EventIterRange Patch::Fork::process(Events & buf, EventIterRange r)
{
    DEBUG_PRINT(Patch::debug_range("Fork in", buf, r));

    // make a copy of all incoming events
    Events::size_type in_size = r.size();
    MidiEvent in[r.size()];
    std::copy(r.begin(), r.end(), in);

    EventIterRange q = r;
    r = EventIterRange(r.end(), r.end());

    for (ModuleVector::iterator m = _modules.begin(); m != _modules.end(); ++m)
    {
        q = (*m)->process(buf, q);

        if (r.begin() == r.end() && !q.empty()) {
            // found first event(s) of return range
            r = EventIterRange(q.begin(), q.end());
        }

        if (TheEngine->remove_duplicates()) {
            // find and remove duplicates
            for (EventIter it = q.begin(); it != q.end(); ) {
                if (std::find(r.begin(), q.begin(), *it) == q.begin()) {
                    ++it;
                } else {
                    it = buf.erase(it);
                }
            }
        }

        if (m + 1 != _modules.end()) {
            // insert copies of all incoming events at the end of the list
            EventIter it = buf.insert(r.end(), *in);
            buf.insert(r.end(), in + 1, in + in_size);

            // point q to newly inserted events
            q = EventIterRange(it, r.end());
        }
    }

    DEBUG_PRINT(Patch::debug_range("Fork out", buf, r));

    return r;
}
#else

Patch::EventIterRange Patch::Fork::process(Events & buf, EventIterRange r)
{
    DEBUG_PRINT(Patch::debug_range("Fork in", buf, r));

    // make a copy of all incoming events
    MidiEvent in[r.size()];
    std::copy(r.begin(), r.end(), in);

    // remove all incoming events
    buf.erase(r.begin(), r.end());
    // events to be returned: none so far
    r = EventIterRange(r.end(), r.end());

    for (MidiEvent * ev = in; ev != in + sizeof(in)/sizeof(*in); ++ev)
    {
        EventIterRange q(r.end(), r.end());

        for (ModuleVector::iterator m = _modules.begin(); m != _modules.end(); ++m)
        {
            // insert one event, process it
            EventIter it = buf.insert(q.end(), *ev);
            EventIterRange p = (*m)->process(buf, EventIterRange(it, q.end()));

            if (!p.empty() && q.empty()) {
                // set start of p and q if they're still empty
                if (r.empty()) {
                    r = EventIterRange(p.begin(), p.end());
                }
                q = EventIterRange(p.begin(), p.end());
            }

            if (_remove_duplicates) {
                // for all events in p, look for previous occurrences in q \ p
                for (EventIter it = p.begin(); it != p.end(); ) {
                    if (std::find(q.begin(), p.begin(), *it) == p.begin()) {
                        ++it;
                    } else {
                        it = buf.erase(it);
                    }
                }
            }
        }
    }

    DEBUG_PRINT(Patch::debug_range("Fork out", buf, r));

    return r;
}

#endif

Patch::EventIterRange Patch::Single::process(Events & buf, EventIterRange r)
{
    DEBUG_PRINT(Patch::debug_range("Single in", buf, r));

    for (EventIter it = r.begin(); it != r.end(); )
    {
        if (_unit->process(*it)) {
            // keep event
            ++it;
        } else {
            // remove event
            if (it == r.begin()) {
                // adjust the range to keep it valid
                r = EventIterRange(++r.begin(), r.end());
            }
            it = buf.erase(it);
        }
    }

    DEBUG_PRINT(Patch::debug_range("Single out", buf, r));

    return r;
}



Patch::EventIterRange Patch::process(Events & buf, EventIterRange r)
{
    DEBUG_PRINT(Patch::debug_range("Patch in", buf, r));

    r = _module->process(buf, r);

    DEBUG_PRINT(Patch::debug_range("Patch out", buf, r));

    return r;
}


std::string Patch::debug_range(std::string const & str, Events & buf, EventIterRange r) {
    return das::make_string() << str << ": " << std::distance(buf.begin(), r.begin()) << ", " << r.size();
}
