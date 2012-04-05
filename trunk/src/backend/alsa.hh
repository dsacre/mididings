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

#ifndef MIDIDINGS_BACKEND_ALSA_HH
#define MIDIDINGS_BACKEND_ALSA_HH

#include "backend/base.hh"

#include <alsa/asoundlib.h>

#include <string>
#include <vector>
#include <map>
#include <boost/scoped_ptr.hpp>
#include <boost/thread/thread.hpp>


namespace Mididings {
namespace Backend {


class ALSABackend
  : public BackendBase
{
  public:
    ALSABackend(std::string const & client_name,
                PortNameVector const & in_port_names,
                PortNameVector const & out_port_names);
    virtual ~ALSABackend();

    virtual void start(InitFunction init, CycleFunction cycle);
    virtual void stop();

    virtual bool input_event(MidiEvent & ev);
    virtual void output_event(MidiEvent const & ev);

    virtual std::size_t num_out_ports() const { return _out_ports.size(); }

    virtual void connect_ports(PortConnectionMap const & in_port_connections,
                               PortConnectionMap const & out_port_connections);

  private:
    struct ClientPortInfo {
        ClientPortInfo(int client_id_, int port_id_, std::string const & client_name_, std::string const & port_name_)
          : client_id(client_id_),
            port_id(port_id_),
            client_name(client_name_),
            port_name(port_name_)
        { }

        int client_id;
        int port_id;
        std::string client_name;
        std::string port_name;
    };

    typedef std::vector<ClientPortInfo> ClientPortInfoVector;

    typedef std::vector<int> PortIdVector;
    typedef std::map<int, int> RevPortIdMap;

    void connect_ports_impl(PortConnectionMap const & port_connections, PortIdVector const & ports, bool out);
    int connect_matching_ports(int port, std::string const & port_name, std::string const & pattern,
                               ClientPortInfoVector const & external_ports, bool out);
    ClientPortInfoVector get_external_ports(bool out);

    void alsa_to_midi_event(MidiEvent & ev, snd_seq_event_t const & alsa_ev);
    void alsa_to_midi_event_sysex(MidiEvent & ev, snd_seq_event_t const & alsa_ev);
    void alsa_to_midi_event_generic(MidiEvent & ev, snd_seq_event_t const & alsa_ev);

    void midi_event_to_alsa(snd_seq_event_t & alsa_ev, MidiEvent const & ev, std::size_t & count);
    void midi_event_to_alsa_sysex(snd_seq_event_t & alsa_ev, MidiEvent const & ev, std::size_t & count);
    void midi_event_to_alsa_generic(snd_seq_event_t & alsa_ev, MidiEvent const & ev);

    snd_seq_t *_seq;

    PortIdVector _in_ports;         // alsa input port IDs
    RevPortIdMap _in_ports_rev;     // reverse mapping (input port ID -> port #)
    PortIdVector _out_ports;        // alsa output port IDs

    snd_midi_event_t *_parser;

    // per-port buffers of incoming sysex data
    std::map<int, SysExDataPtr> _sysex_buffer;

    boost::scoped_ptr<boost::thread> _thread;
};


} // Backend
} // Mididings


#endif // MIDIDINGS_BACKEND_ALSA_HH
