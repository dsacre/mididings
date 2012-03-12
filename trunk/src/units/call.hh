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

#ifndef MIDIDINGS_UNITS_CALL_HH
#define MIDIDINGS_UNITS_CALL_HH

#include "units/base.hh"

#include <boost/python/object.hpp>


namespace Mididings {
namespace Units {


class Call
  : public UnitEx
{
  public:
    Call(boost::python::object fun, bool async, bool cont)
      : _fun(fun)
      , _async(async)
      , _cont(cont)
    {
    }

    virtual Patch::EventRange process(Patch::Events & buf, Patch::EventIter it)
    {
        PythonCaller & c = TheEngine->python_caller();

        if (_async) {
            return c.call_deferred(buf, it, _fun, _cont);
        } else {
            return c.call_now(buf, it, _fun);
        }
    }

  private:
    boost::python::object _fun;
    bool _async;
    bool _cont;
};


} // Units
} // Mididings


#endif // MIDIDINGS_UNITS_CALL_HH

