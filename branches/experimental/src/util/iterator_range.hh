/*
 * Copyright (C) 2012  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef DAS_UTIL_ITERATOR_RANGE_HH
#define DAS_UTIL_ITERATOR_RANGE_HH


#include <iterator>


namespace das {


template <typename T>
class iterator_range
{
  private:
    typedef typename std::iterator_traits<T>::difference_type difference_type;

  public:
    /**
     * Construction from two iterators.
     */
    iterator_range(T const & begin, T const & end)
      : _begin(begin)
      , _end(end)
    { }

    /**
     * Construction from begin iterator and number of elements.
     */
    iterator_range(T const & iter, difference_type n = 0)
      : _begin(iter)
      , _end(iter)
    {
        advance_end(n);
    }

    T begin() const {
        return _begin;
    }

    T end() const {
        return _end;
    }

    bool empty() const {
        return _begin == _end;
    }

    difference_type size() const {
        return std::distance(_begin, _end);
    }

    bool operator==(iterator_range const & other) {
        return _begin == other.begin() && _end == other.end();
    }

    bool operator!=(iterator_range const & other) {
        return !(*this == other);
    }

    void set_begin(T const & iter) {
        _begin = iter;
    }

    void set_end(T const & iter) {
        _end = iter;
    }

    void advance_begin(difference_type n = 1) {
        std::advance(_begin, n);
    }

    void advance_end(difference_type n = 1) {
        std::advance(_end, n);
    }

  private:
    T _begin;
    T _end;
};


} // namespace das


#endif // DAS_UTIL_ITERATOR_RANGE_HH

