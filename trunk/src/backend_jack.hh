/*
 * mididings
 *
 * Copyright (C) 2008-2009  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef _BACKEND_JACK_HH
#define _BACKEND_JACK_HH

#include "backend.hh"
#include "midi_event.hh"

#include <string>
#include <vector>
#include <boost/scoped_ptr.hpp>

#include <boost/thread/thread.hpp>
#include <boost/thread/condition.hpp>
#include <boost/thread/mutex.hpp>

#include <jack/types.h>
#include <jack/midiport.h>

#include "util/ringbuffer.hh"


/*
 * JACK backend base class
 */
class BackendJack
  : public Backend
{
  public:
    BackendJack(std::string const & client_name,
                std::vector<std::string> const & in_portnames,
                std::vector<std::string> const & out_portnames);
    virtual ~BackendJack();

    virtual std::size_t num_out_ports() const { return _out_ports.size(); }

  protected:
    // this should be pure virtual.
    // it isn't, because the process thread is started within the c'tor
    virtual int process(jack_nframes_t) { return 0; } //= 0;

    void clear_buffers(jack_nframes_t nframes);
    bool read_event_from_buffer(MidiEvent & ev, jack_nframes_t nframes);
    void write_event_to_buffer(MidiEvent const & ev, jack_nframes_t nframes);

    jack_client_t *_client;
    std::vector<jack_port_t *> _in_ports;
    std::vector<jack_port_t *> _out_ports;

    jack_nframes_t _current_frame;

  private:
    static int process_(jack_nframes_t, void *);

    // loop counters used by read_event_from_buffer()
    int _input_port;
    int _input_count;
};


/*
 * buffered JACK backend.
 * all events are written to a ringbuffer and processed in a separate thread.
 */
class BackendJackBuffered
  : public BackendJack
{
  public:
    BackendJackBuffered(std::string const & client_name,
                        std::vector<std::string> const & in_portnames,
                        std::vector<std::string> const & out_portnames);
    virtual ~BackendJackBuffered();

    virtual void start(InitFunction init, CycleFunction cycle);

    virtual bool input_event(MidiEvent & ev);
    virtual void output_event(MidiEvent const & ev);

  private:
    virtual int process(jack_nframes_t);

    das::ringbuffer<MidiEvent> _in_rb;
    das::ringbuffer<MidiEvent> _out_rb;

    boost::scoped_ptr<boost::thread> _thrd;

    boost::condition _cond;
    boost::mutex _mutex;

    volatile bool _quit;
};


/*
 * realtime JACK backend.
 * events are processed inside the JACK callback.
 */
class BackendJackRealtime
  : public BackendJack
{
  public:
    BackendJackRealtime(std::string const & client_name,
                        std::vector<std::string> const & in_portnames,
                        std::vector<std::string> const & out_portnames);
    virtual ~BackendJackRealtime() { }

    virtual void start(InitFunction init, CycleFunction cycle);

    virtual bool input_event(MidiEvent & ev);
    virtual void output_event(MidiEvent const & ev);

  private:
    virtual int process(jack_nframes_t);

    InitFunction _run_init;
    CycleFunction _run_cycle;

    jack_nframes_t _nframes;

    das::ringbuffer<MidiEvent> _out_rb;
};


#endif // _BACKEND_JACK_HH
