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
#include <boost/function.hpp>
#include <boost/noncopyable.hpp>

#include "midi_event.hh"


class Backend
  : boost::noncopyable
{
  public:
    struct BackendError
      : public std::runtime_error
    {
        BackendError(std::string const & w)
          : std::runtime_error(w)
        {
        }
    };

    typedef boost::function<void ()> InitFunction;
    typedef boost::function<void ()> CycleFunction;

    Backend() { }
    virtual ~Backend() { }

    virtual void start(InitFunction init, CycleFunction cycle) = 0;

    virtual bool input_event(MidiEvent & ev) = 0;
    virtual void output_event(MidiEvent const & ev) = 0;
    virtual void flush_output() { };

    template <typename IterT>
    void output_events(IterT begin, IterT end)
    {
        for (IterT it = begin; it != end; ++it) {
            output_event(*it);
        }
    }

    virtual std::size_t num_out_ports() const = 0;

  protected:
    static MidiEvent buffer_to_midi_event(unsigned char *data, int port, uint64_t frame);
    static void midi_event_to_buffer(MidiEvent const & ev, unsigned char *data, std::size_t & len, int & port, uint64_t & frame);
};


#endif // _BACKEND_HH
