/*
 * Copyright (C) 2012  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef DAS_UTIL_IS_SHARED_PTR_HH
#define DAS_UTIL_IS_SHARED_PTR_HH

#include <boost/mpl/bool.hpp>
#include <boost/shared_ptr.hpp>


namespace das {


template <typename T>
struct is_shared_ptr
  : boost::mpl::false_ { };

template <typename T>
struct is_shared_ptr<boost::shared_ptr<T> >
  : boost::mpl::true_ { };


} // namespace das


#endif // DAS_UTIL_IS_SHARED_PTR_HH
