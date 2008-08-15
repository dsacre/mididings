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

#include <boost/foreach.hpp>

#include "util/debug.hh"
#include "util/string.hh"


Patch::EventIterRange Patch::Chain::process(Events & buf, EventIterRange r)
{
    DEBUG_PRINT(Patch::debug_range("Chain in", buf, r));

    BOOST_FOREACH (ModulePtr m, _modules)
    {
        if (r.empty()) {
            // nothing to do
            break;
        }

        r = m->process(buf, r);
    }

    DEBUG_PRINT(Patch::debug_range("Chain out", buf, r));

    return r;
}


Patch::EventIterRange Patch::Fork::process(Events & buf, EventIterRange r)
{
    DEBUG_PRINT(Patch::debug_range("Fork in", buf, r));

    // make a copy of all incoming events
    MidiEvent in[std::distance(r.begin(), r.end())];
    std::copy(r.begin(), r.end(), in);

    // remove all incoming events
    buf.erase(r.begin(), r.end());
    // events to be returned: none so far
    r = EventIterRange(r.end(), r.end());

    for (MidiEvent * ev = in; ev != in + sizeof(in)/sizeof(*in); ++ev)
    {
        EventIterRange q(r);

        BOOST_FOREACH (ModulePtr m, _modules)
        {
            // insert one event, process it
            EventIter it = buf.insert(q.end(), *ev);
            EventIterRange p = m->process(buf, EventIterRange(it, q.end()));

            if (!p.empty() && q.empty()) {
                // set start of p and q if they're still empty
                if (r.empty()) {
                    r = p;
                }
                q = p;
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
                r.advance_begin(1);
            }
            it = buf.erase(it);
        }
    }

    DEBUG_PRINT(Patch::debug_range("Single out", buf, r));

    return r;
}



Patch::EventIterRange Patch::process(Events & buf, EventIterRange r)
{
    DEBUG_PRINT(debug_range("Patch in", buf, r));

    r = _module->process(buf, r);

    DEBUG_PRINT(debug_range("Patch out", buf, r));

    return r;
}


std::string Patch::debug_range(std::string const & str, Events & buf, EventIterRange r)
{
    return das::make_string() << str << ": " << std::distance(buf.begin(), r.begin()) << ", " << std::distance(r.begin(), r.end());
}
