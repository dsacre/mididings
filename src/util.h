/*
 * Copyright (C) 2007  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef _UTIL_H
#define _UTIL_H

#include <string>
#include <sstream>
#include <exception>
#include <boost/noncopyable.hpp>


#ifdef ENABLE_DEBUG
    #include <assert.h>
    #define ASSERT(f) assert(f)
    #define VERIFY(f) assert(f)
    #define FAIL()    assert(false)
#else
    #define ASSERT(f) ((void)0)
    #define VERIFY(f) ((void)f)
    #define FAIL()    ((void)0)
#endif

#if defined(ENABLE_DEBUG_FN) || defined(ENABLE_DEBUG_PRINT)
    #include <iostream>
#endif

#ifdef ENABLE_DEBUG_FN
    #define DEBUG_FN() std::cout << __PRETTY_FUNCTION__ << std::endl
#else
    #define DEBUG_FN() ((void)0)
#endif

#ifdef ENABLE_DEBUG_PRINT
    #define DEBUG_PRINT(m)  std::cout << m << std::endl
#else
    #define DEBUG_PRINT(m)  ((void)0)
#endif


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


class make_string
{
  public:
    template <typename T>
    make_string & operator<< (T const& t) {
        _stream << t;
        return *this;
    }

    make_string & operator<< (std::ostream & (*pf)(std::ostream &)) {
        pf(_stream);
        return *this;
    }

    operator std::string() {
        return _stream.str();
    }

  private:
    std::ostringstream _stream;
};


class string_exception : public std::exception {
  public:
    string_exception(const std::string & w) : _w(w) { }
    virtual ~string_exception() throw () { }
    virtual const char *what() const throw() { return _w.c_str(); }
  protected:
    std::string _w;
};


} // namespace das

#endif
