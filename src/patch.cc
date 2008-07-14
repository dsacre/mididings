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
#include "setup.hh"

using namespace std;


void Patch::process(const MidiEvent & ev_in)
{
    MidiEvent ev = ev_in;
    process_recursive(*_start, ev);
}


void Patch::process_recursive(Module & m, MidiEvent & ev)
{
    //cout << typeid(m.unit()).name() << endl;

    bool r = m.unit().process(ev);
    if (!r) return;

    size_t s = m.next().size();

    if (s == 1) {
        // single successor, pass same event on to next module
        process_recursive(*m.next()[0], ev);
    }
    else if (s > 1) {
        // more than one successor, need to work on a copy of the original event
        MidiEvent ev_copy;
        for (vector<ModulePtr>::iterator i = m.next().begin(); i != m.next().end(); ++i) {
            ev_copy = ev;
            process_recursive(**i, ev_copy);
        }
    }
}


bool Patch::Output::process(MidiEvent & ev)
{
    TheSetup->buffer_event(ev);
    // nothing left to do
    return false;
}
