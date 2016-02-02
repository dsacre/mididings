/*
 * mididings
 *
 * Copyright (C) 2008-2014  Dominic Sacré  <dominic.sacre@gmx.de>
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


namespace mididings {
namespace backend {


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

    virtual void finish() {
        // nothing to do
    }

    virtual std::size_t num_out_ports() const {
        return _out_ports.size();
    }

    /**
     * Connect our own input and output ports according to the regular
     * expressions specified.
     */
    virtual void connect_ports(PortConnectionMap const & in_port_connections,
                               PortConnectionMap const & out_port_connections);

    virtual std::string get_actual_client_name();

    virtual int get_client_id();

  private:
    /**
     * Name and id of an ALSA port, including its client name/id.
     */
    struct ClientPortInfo {
        ClientPortInfo(int client_id,
                       int port_id,
                       std::string const & client_name,
                       std::string const & port_name)
          : client_id(client_id),
            port_id(port_id),
            client_name(client_name),
            port_name(port_name)
        { }

        int client_id;
        int port_id;
        std::string client_name;
        std::string port_name;
    };

    typedef std::vector<ClientPortInfo> ClientPortInfoVector;

    typedef std::vector<int> PortIdVector;
    typedef std::map<int, int> RevPortIdMap;

    void connect_ports_impl(
            PortConnectionMap const & port_connections,
            PortIdVector const & port_ids,
            bool out);

    int connect_matching_ports(
            ClientPortInfo const & own_port,
            ClientPortInfoVector const & ext_ports,
            std::string const & pattern,
            bool out);

    bool connect_single_port(
            ClientPortInfo const & own_port,
            ClientPortInfo const & ext_port,
            bool out);

    ClientPortInfoVector get_external_ports(bool out);

    void process_thread(InitFunction init, CycleFunction cycle);

    void alsa_to_midi_event(MidiEvent & ev,
                            snd_seq_event_t const & alsa_ev);
    void alsa_to_midi_event_sysex(MidiEvent & ev,
                            snd_seq_event_t const & alsa_ev);
    void alsa_to_midi_event_generic(MidiEvent & ev,
                            snd_seq_event_t const & alsa_ev);

    void midi_event_to_alsa(snd_seq_event_t & alsa_ev,
                            MidiEvent const & ev, std::size_t & count);
    void midi_event_to_alsa_sysex(snd_seq_event_t & alsa_ev,
                            MidiEvent const & ev, std::size_t & count);
    void midi_event_to_alsa_generic(snd_seq_event_t & alsa_ev,
                            MidiEvent const & ev);

    snd_seq_t *_seq;

    PortIdVector _in_ports;     // alsa input port IDs
    RevPortIdMap _in_ports_rev; // reverse mapping (input port ID -> port #)
    PortIdVector _out_ports;    // alsa output port IDs

    snd_midi_event_t *_parser;

    // per-port buffers of incoming sysex data
    std::map<int, SysExDataPtr> _sysex_buffer;

    boost::scoped_ptr<boost::thread> _thread;
};


} // backend
} // mididings


#endif // MIDIDINGS_BACKEND_ALSA_HH
