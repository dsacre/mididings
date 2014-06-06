/*
 * mididings
 *
 * Copyright (C) 2013-2014  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#include "config.hh"
#include "send_midi.hh"
#include "backend/base.hh"

#include <boost/shared_ptr.hpp>


namespace mididings {


void send_midi(std::string const & backend_name,
               std::string const & dest_port,
               std::vector<MidiEvent> const & events)
{
    backend::PortNameVector in_ports;
    backend::PortNameVector out_ports(1, "output");

    backend::BackendPtr send_backend =
            backend::create(backend_name, "send_midi", in_ports, out_ports);

    backend::PortConnectionMap in_port_connections;
    backend::PortConnectionMap out_port_connections;
    out_port_connections["output"] = std::vector<std::string>(1, dest_port);

    send_backend->connect_ports(in_port_connections, out_port_connections);

    send_backend->output_events(events.begin(), events.end());

    send_backend->finish();
}


} // mididings
