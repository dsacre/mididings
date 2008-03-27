/*
 * Copyright (C) 2007-2008  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef _DAS_EXCEPTION_HH
#define _DAS_EXCEPTION_HH

#include <exception>
#include <string>

namespace das {


class exception
  : public std::exception
{
  public:
    exception(const std::string & w)
      : _w(w) { }

    virtual ~exception() throw () { }

    virtual const char *what() const throw() {
        return _w.c_str();
    }

  protected:
    std::string _w;
};


} // namespace das


#endif // _DAS_EXCEPTION_HH
