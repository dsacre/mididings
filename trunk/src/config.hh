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

#ifndef _CONFIG_HH
#define _CONFIG_HH


namespace Config
{
    static int const MAX_EVENTS = 1024;

    static int const MAX_SIMULTANEOUS_NOTES = 64;
    static int const MAX_SUSTAIN_PEDALS = 4;

    static int const MAX_ASYNC_CALLS = 256;
    static int const ASYNC_JOIN_TIMEOUT = 3000;
    static int const ASYNC_CALLBACK_INTERVAL = 50;

    static int const MAX_JACK_EVENTS = 128;
    static int const MAX_EVENT_SIZE = 1024;
}


#endif // _CONFIG_HH
