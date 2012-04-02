/*
 * Copyright (C) 2007-2008  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef DAS_UTIL_STRING_HH
#define DAS_UTIL_STRING_HH

#include <string>
#include <sstream>
#include <vector>
#include <stdexcept>

#include <boost/shared_ptr.hpp>
#include <boost/noncopyable.hpp>

#include <regex.h>


namespace das {


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


class regex
  : boost::noncopyable
{
  public:
    struct compile_error
      : public std::runtime_error
    {
        compile_error(std::string const & w)
          : std::runtime_error(w)
        {
        }
    };

    regex(std::string const & pattern, bool complete=false) {
        std::string p = complete ? ("^" + pattern + "$") : pattern;

        int error = ::regcomp(&_preg, p.c_str(), REG_EXTENDED | REG_NOSUB);
        _freer.reset(&_preg, ::regfree);

        if (error) {
            std::size_t bufsize = ::regerror(error, &_preg, NULL, 0);
            std::vector<char> buf(bufsize);
            ::regerror(error, &_preg, &(*buf.begin()), bufsize);

            throw compile_error(&*buf.begin());
        }
    }

    bool match(std::string const & str) {
        return ::regexec(&_preg, str.c_str(), 0, NULL, 0) == 0;
    }

  private:
    ::regex_t _preg;
    boost::shared_ptr<void> _freer;
};


} // namespace das

#endif // DAS_UTIL_STRING_HH
