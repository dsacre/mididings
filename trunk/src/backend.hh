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

#ifndef _BACKEND_HH
#define _BACKEND_HH

#include <string>
#include <stdexcept>
#include <boost/noncopyable.hpp>

#include "midi_event.hh"


class Backend
  : boost::noncopyable
{
  public:
    Backend()
    {
    }

    virtual ~Backend()
    {
    }

    virtual void input_event(MidiEvent & ev) = 0;
    virtual void output_event(MidiEvent const & ev) = 0;
    virtual void drop_input() = 0;
    virtual void flush_output() = 0;

    template <typename IterT>
    void output_events(IterT begin, IterT end)
    {
        for (IterT it = begin; it != end; ++it) {
            output_event(*it);
        }
    }

  protected:
    struct BackendError
      : public std::runtime_error
    {
        BackendError(std::string const & w)
          : std::runtime_error(w)
        {
        }
    };
};


#endif // _BACKEND_HH
