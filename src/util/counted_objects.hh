/*
 * Copyright (C) 2012  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef DAS_UTIL_COUNTED_OBJECTS_HH
#define DAS_UTIL_COUNTED_OBJECTS_HH

#include <boost/detail/atomic_count.hpp>


namespace das {


template <typename T>
class counted_objects
{
  protected:
    counted_objects() {
        ++alloc_;
    }

    ~counted_objects() {
        ++dealloc_;
    }

  public:
    static std::size_t allocated() { return alloc_; }
    static std::size_t deallocated() { return dealloc_; }

  private:
    static boost::detail::atomic_count alloc_;
    static boost::detail::atomic_count dealloc_;
};


template <typename T> boost::detail::atomic_count counted_objects<T>::alloc_(0);
template <typename T> boost::detail::atomic_count counted_objects<T>::dealloc_(0);


} // namespace das


#endif // DAS_UTIL_COUNTED_OBJECTS_HH
