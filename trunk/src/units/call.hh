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
  : public UnitExImpl<Call>
{
  public:
    Call(boost::python::object fun, bool async, bool cont)
      : _fun(fun)
      , _async(async)
      , _cont(cont)
    { }

    template <typename B>
    typename B::Range process(B & buffer, typename B::Iterator it) const
    {
        PythonCaller & c = buffer.engine().python_caller();

        if (_async) {
            return c.call_deferred(buffer, it, _fun, _cont);
        } else {
            return c.call_now(buffer, it, _fun);
        }
    }

  private:
    boost::python::object const _fun;
    bool const _async;
    bool const _cont;
};


} // Units
} // Mididings


#endif // MIDIDINGS_UNITS_CALL_HH

