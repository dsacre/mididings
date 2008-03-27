/*
 * Copyright (C) 2007-2008  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef _DAS_GLOBAL_OBJECT_HH
#define _DAS_GLOBAL_OBJECT_HH

#include <boost/noncopyable.hpp>
#include "util/debug.hh"

namespace das {


template <typename T, T *& pp>
class global_object
  : boost::noncopyable
{
  protected:
    global_object() {
        ASSERT(!pp);
        pp = static_cast<T*>(this);
    }

    ~global_object() {
        ASSERT(pp);
        pp = NULL;
    }
};


} // namespace das

#endif // _DAS_GLOBAL_OBJECT_HH
