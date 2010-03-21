/*
 * Copyright (C) 2009  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef _DAS_RINGBUFFER_HH
#define _DAS_RINGBUFFER_HH

#include <boost/noncopyable.hpp>
#include <glib.h>


namespace das {

/*
 * lock-free ring buffer, supports storing C++ objects.
 * inspired by and partly copied from Raul::RingBuffer by Dave Robillard.
 */
template <typename T>
class ringbuffer : boost::noncopyable
{
  public:
    ringbuffer(size_t size)
      : _size(size)
      , _buf(new T[size])
    {
        reset();
    }

    virtual ~ringbuffer() {
        delete[] _buf;
    }

    void reset() {
        g_atomic_int_set(&_write_ptr, 0);
        g_atomic_int_set(&_read_ptr, 0);
    }

    size_t write_space() const {
        const size_t w = g_atomic_int_get(&_write_ptr);
        const size_t r = g_atomic_int_get(&_read_ptr);

        if (w > r) {
            return ((r - w + _size) % _size) - 1;
        } else if (w < r) {
            return (r - w) - 1;
        } else {
            return _size - 1;
        }
    }

    size_t read_space() const {
        const size_t w = g_atomic_int_get(&_write_ptr);
        const size_t r = g_atomic_int_get(&_read_ptr);

        if (w > r) {
            return w - r;
        } else {
            return (w - r + _size) % _size;
        }
    }

    size_t capacity() const {
        return _size;
    }

    bool read(T & dst) {
        if (read_space()) {
            const size_t priv_read_ptr = g_atomic_int_get(&_read_ptr);
            dst = _buf[priv_read_ptr];
            g_atomic_int_set(&_read_ptr, (priv_read_ptr + 1) % _size);
            return true;
        } else {
            return false;
        }
    }

    bool write(const T & src) {
        if (write_space()) {
            const size_t priv_write_ptr = g_atomic_int_get(&_write_ptr);
            _buf[priv_write_ptr] = src;
            g_atomic_int_set(&_write_ptr, (priv_write_ptr + 1) % _size);
            return true;
        } else {
            return false;
        }
    }

protected:
    mutable int _write_ptr;
    mutable int _read_ptr;

    size_t _size;
    T*     _buf;
};


} // namespace das


#endif // _DAS_RINGBUFFER_HH
