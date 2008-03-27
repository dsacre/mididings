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

#include "patch.hh"
#include "midi_event.hh"
#include "util/exception.hh"

#include <vector>
#include <string>


class Backend
{
  public:
    Backend()
    {
    }

    virtual ~Backend()
    {
    }

    virtual void run(class Setup &) = 0;

  protected:
    struct BackendError : public das::exception {
        BackendError(const std::string & w)
          : das::exception(w) { }
    };
};


#endif // _BACKEND_HH
