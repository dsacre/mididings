/*
 * mididings
 *
 * Copyright (C) 2008-2011  Dominic Sacré  <dominic.sacre@gmx.de>
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
#include <iterator>
#include <sstream>

#include "util/debug.hh"


namespace Mididings {


void Patch::Chain::process(Events & buf, EventRange & r)
{
    DEBUG_PRINT(Patch::debug_range("Chain in", buf, r));

    for (ModuleVector::iterator m = _modules.begin(); m != _modules.end(); ++m)
    {
        if (r.empty()) {
            // nothing to do
            break;
        }

        (*m)->process(buf, r);
    }

    DEBUG_PRINT(Patch::debug_range("Chain out", buf, r));
}


void Patch::Fork::process(Events & buf, EventRange & r)
{
    DEBUG_PRINT(Patch::debug_range("Fork in", buf, r));

    // make a copy of all incoming events
    MidiEvent in[std::distance(r.begin(), r.end())];
    std::copy(r.begin(), r.end(), in);

    // remove all incoming events
    buf.erase(r.begin(), r.end());
    // events to be returned: none so far
    r = EventRange(r.end(), r.end());

    for (MidiEvent * ev = in; ev != in + sizeof(in)/sizeof(*in); ++ev)
    {
        EventRange q(r.end(), r.end());

        for (ModuleVector::iterator m = _modules.begin(); m != _modules.end(); ++m)
        {
            // insert one event, process it
            EventIter it = buf.insert(q.end(), *ev);
            EventRange p(it, q.end());
            (*m)->process(buf, p);

            if (!p.empty() && q.empty()) {
                // set start of r and q if they're still empty
                if (r.empty()) {
                    r = p;
                }
                q = p;
            }

            if (_remove_duplicates) {
                // for all events in p, look for previous occurrences in q \ p
                for (EventIter it = p.begin(); it != p.end(); ) {
                    if (std::find(q.begin(), p.begin(), *it) != p.begin()) {
                        DEBUG_PRINT("Removing duplicate");
                        it = buf.erase(it);
                    } else {
                        ++it;
                    }
                }
            }
        }
    }

    DEBUG_PRINT(Patch::debug_range("Fork out", buf, r));
}


void Patch::Single::process(Events & buf, EventRange & r)
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
}


void Patch::Extended::process(Events & buf, EventRange & r)
{
    DEBUG_PRINT(Patch::debug_range("Extended in", buf, r));

    EventRange p(r);
    r = EventRange(r.end(), r.end());

    for (EventIter it = p.begin(); it != p.end(); )
    {
        EventRange q = _unit->process(buf, it);

        if (r.empty() && !q.empty()) {
            r = EventRange(q.begin(), r.end());
        }

        it = q.end();
    }

    DEBUG_PRINT(Patch::debug_range("Extended out", buf, r));
}



void Patch::process(Events & buf, EventRange & r)
{
    DEBUG_PRINT(debug_range("Patch in", buf, r));

    _module->process(buf, r);

    DEBUG_PRINT(debug_range("Patch out", buf, r));
}


std::string Patch::debug_range(std::string const & str, Events & buf, EventRange const & r)
{
    std::ostringstream os;
    os << str << ": "
       << std::distance(buf.begin(), r.begin()) << " "
       << std::distance(r.begin(), r.end());
    for (EventIter it = r.begin(); it != r.end(); ++it) {
        os << " [" << it->type << " " << it->port << " " << it->channel << " " << it->data1 << " " << it->data2 << "]";
    }
    return os.str();
}


} // Mididings
