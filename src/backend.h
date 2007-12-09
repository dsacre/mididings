/*
 * midipatch
 *
 * Copyright (C) 2007  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef _BACKEND_H
#define _BACKEND_H

#include "patch.h"
#include "midi_event.h"
#include "util.h"

#include <vector>
#include <string>


class Backend
{
  public:
    Backend(bool debug)
      : _debug(debug)
    {
    }

    virtual ~Backend()
    {
    }

    virtual void run(class Setup &) = 0;

  protected:
    std::string dump_event(const MidiEvent & ev);

    void dump_incoming_event(const MidiEvent & ev);
    void dump_outgoing_events(const std::vector<MidiEvent> & evs);

    struct BackendError : public string_exception {
        BackendError(const std::string & w)
          : string_exception(w) { }
    };

    bool _debug;
};


#endif
