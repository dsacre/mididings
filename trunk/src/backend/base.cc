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

#include "config.hh"
#include "backend/base.hh"
#ifdef ENABLE_ALSA_SEQ
  #include "backend/alsa.hh"
#endif
#ifdef ENABLE_JACK_MIDI
  #include "backend/jack_buffered.hh"
  #include "backend/jack_realtime.hh"
#endif
#ifdef ENABLE_SMF
  #include "backend/smf.hh"
#endif

#include <algorithm>


namespace Mididings {
namespace Backend {


namespace {
    std::vector<std::string> AVAILABLE;

    bool init_available() {
#ifdef ENABLE_ALSA_SEQ
        AVAILABLE.push_back("alsa");
#endif
#ifdef ENABLE_JACK_MIDI
        AVAILABLE.push_back("jack");
        AVAILABLE.push_back("jack-rt");
#endif
        return false;
    }

    bool throwaway = init_available();
}


std::vector<std::string> const & available()
{
    return AVAILABLE;
}


boost::shared_ptr<BackendBase> create(std::string const & backend_name,
                                      std::string const & client_name,
                                      PortNameVector const & in_ports,
                                      PortNameVector const & out_ports)
{
    if (backend_name == "dummy") {
        // return empty shared pointer
        return boost::shared_ptr<BackendBase>();
    }
#ifdef ENABLE_ALSA_SEQ
    else if (backend_name == "alsa") {
        return boost::shared_ptr<BackendBase>(new ALSABackend(client_name, in_ports, out_ports));
    }
#endif
#ifdef ENABLE_JACK_MIDI
    else if (backend_name == "jack") {
        return boost::shared_ptr<BackendBase>(new JACKBufferedBackend(client_name, in_ports, out_ports));
    }
    else if (backend_name == "jack-rt") {
        return boost::shared_ptr<BackendBase>(new JACKRealtimeBackend(client_name, in_ports, out_ports));
    }
#endif
#ifdef ENABLE_SMF
    else if (backend_name == "smf") {
        return boost::shared_ptr<BackendBase>(new SMFBackend(in_ports[0], out_ports[0]));
    }
#endif
    else {
        throw Error("invalid backend selected: " + backend_name);
    }
}


MidiEvent BackendBase::buffer_to_midi_event(unsigned char *data, std::size_t len, int port, uint64_t frame)
{
    MidiEvent ev;

    ev.frame = frame;
    ev.port = port;

    if ((data[0] & 0xf0) != 0xf0)
    {
        ev.channel = data[0] & 0x0f;

        switch (data[0] & 0xf0)
        {
          case 0x90:
            ev.type = data[2] ? MIDI_EVENT_NOTEON : MIDI_EVENT_NOTEOFF;
            ev.note.note = data[1];
            ev.note.velocity = data[2];
            break;
          case 0x80:
            ev.type = MIDI_EVENT_NOTEOFF;
            ev.note.note = data[1];
            ev.note.velocity = data[2];
            break;
          case 0xb0:
            ev.type = MIDI_EVENT_CTRL;
            ev.ctrl.param = data[1];
            ev.ctrl.value = data[2];
            break;
          case 0xe0:
            ev.type = MIDI_EVENT_PITCHBEND;
            ev.ctrl.param = 0;
            ev.ctrl.value = (data[2] << 7 | data[1]) - 8192;
            break;
          case 0xd0:
            ev.type = MIDI_EVENT_AFTERTOUCH;
            ev.ctrl.param = 0;
            ev.ctrl.value = data[1];
            break;
          case 0xa0:
            ev.type = MIDI_EVENT_POLY_AFTERTOUCH;
            ev.ctrl.param = data[1];
            ev.ctrl.value = data[2];
            break;
          case 0xc0:
            ev.type = MIDI_EVENT_PROGRAM;
            ev.ctrl.param = 0;
            ev.ctrl.value = data[1];
            break;
          default:
            ev.type = MIDI_EVENT_NONE;
            break;
        }
    }
    else
    {
        ev.channel = 0;

        switch (data[0])
        {
          case 0xf0:
            ev.type = MIDI_EVENT_SYSEX;
            // FIXME: come up with a realtime-safe way to do this
            ev.sysex.reset(new SysExData(data, data + len));
            break;
          case 0xf1:
            ev.type = MIDI_EVENT_SYSCM_QFRAME;
            ev.data1 = data[1];
            break;
          case 0xf2:
            ev.type = MIDI_EVENT_SYSCM_SONGPOS;
            ev.data1 = data[1];
            ev.data2 = data[2];
            break;
          case 0xf3:
            ev.type = MIDI_EVENT_SYSCM_SONGSEL;
            ev.data1 = data[1];
            break;
          case 0xf6:
            ev.type = MIDI_EVENT_SYSCM_TUNEREQ;
            break;
          case 0xf8:
            ev.type = MIDI_EVENT_SYSRT_CLOCK;
            break;
          case 0xfa:
            ev.type = MIDI_EVENT_SYSRT_START;
            break;
          case 0xfb:
            ev.type = MIDI_EVENT_SYSRT_CONTINUE;
            break;
          case 0xfc:
            ev.type = MIDI_EVENT_SYSRT_STOP;
            break;
          case 0xfe:
            ev.type = MIDI_EVENT_SYSRT_SENSING;
            break;
          case 0xff:
            ev.type = MIDI_EVENT_SYSRT_RESET;
            break;
          default:
            ev.type = MIDI_EVENT_NONE;
            break;
        }
    }

    return ev;
}


std::size_t BackendBase::midi_event_to_buffer(MidiEvent const & ev, unsigned char *data, std::size_t & len, int & port, uint64_t & frame)
{
    frame = ev.frame;
    port = ev.port;
    data[0] = ev.channel;

    switch (ev.type)
    {
      case MIDI_EVENT_NOTEON:
        len = 3;
        data[0] |= 0x90;
        data[1] = ev.note.note;
        data[2] = ev.note.velocity;
        break;
      case MIDI_EVENT_NOTEOFF:
        len = 3;
        data[0] |= 0x80;
        data[1] = ev.note.note;
        data[2] = ev.note.velocity;
        break;
      case MIDI_EVENT_CTRL:
        len = 3;
        data[0] |= 0xb0;
        data[1] = ev.ctrl.param;
        data[2] = ev.ctrl.value;
        break;
      case MIDI_EVENT_PITCHBEND:
        len = 3;
        data[0] |= 0xe0;
        data[1] = (ev.ctrl.value + 8192) % 128;
        data[2] = (ev.ctrl.value + 8192) / 128;
        break;
      case MIDI_EVENT_AFTERTOUCH:
        len = 2;
        data[0] |= 0xd0;
        data[1] = ev.ctrl.value;
        break;
      case MIDI_EVENT_POLY_AFTERTOUCH:
        len = 3;
        data[0] |= 0xa0;
        data[1] = ev.ctrl.param;
        data[2] = ev.ctrl.value;
        break;
      case MIDI_EVENT_PROGRAM:
        len = 2;
        data[0] |= 0xc0;
        data[1] = ev.ctrl.value;
        break;
      case MIDI_EVENT_SYSEX:
        if (ev.sysex->size() <= len) {
            len = ev.sysex->size();
            std::copy(ev.sysex->begin(), ev.sysex->end(), data);
        } else {
            // sysex too long, drop it
            len = 0;
        }
        break;
      case MIDI_EVENT_SYSCM_QFRAME:
        len = 2;
        data[0] = 0xf1;
        data[1] = ev.data1;
        break;
      case MIDI_EVENT_SYSCM_SONGPOS:
        len = 3;
        data[0] = 0xf2;
        data[1] = ev.data1;
        data[2] = ev.data2;
        break;
      case MIDI_EVENT_SYSCM_SONGSEL:
        len = 2;
        data[0] = 0xf3;
        data[1] = ev.data1;
        break;
      case MIDI_EVENT_SYSCM_TUNEREQ:
        len = 1;
        data[0] = 0xf6;
        break;
      case MIDI_EVENT_SYSRT_CLOCK:
        len = 1;
        data[0] = 0xf8;
        break;
      case MIDI_EVENT_SYSRT_START:
        len = 1;
        data[0] = 0xfa;
        break;
      case MIDI_EVENT_SYSRT_CONTINUE:
        len = 1;
        data[0] = 0xfb;
        break;
      case MIDI_EVENT_SYSRT_STOP:
        len = 1;
        data[0] = 0xfc;
        break;
      case MIDI_EVENT_SYSRT_SENSING:
        len = 1;
        data[0] = 0xfe;
        break;
      case MIDI_EVENT_SYSRT_RESET:
        len = 1;
        data[0] = 0xff;
        break;
      default:
        len = 0;
    }

    return len;
}


} // Backend
} // Mididings
