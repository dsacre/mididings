/*
 * mididings
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
    Backend()
    {
    }

    virtual ~Backend()
    {
    }

    virtual void run(class Setup &) = 0;

  protected:
    struct BackendError : public das::string_exception {
        BackendError(const std::string & w)
          : das::string_exception(w) { }
    };
};


#endif
