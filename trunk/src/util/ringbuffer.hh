/*
 * Copyright (C) 2009  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef DAS_UTIL_RINGBUFFER_HH
#define DAS_UTIL_RINGBUFFER_HH

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
    ringbuffer(std::size_t size)
      : _size(size)
      , _buf_array(new unsigned char[size * sizeof(T)])
      , _buf(reinterpret_cast<T*>(_buf_array))
    {
        reset();
    }

    ~ringbuffer() {
        delete[] _buf_array;
    }

    void reset() {
        g_atomic_int_set(&_write_idx, 0);
        g_atomic_int_set(&_read_idx, 0);
    }

    std::size_t write_space() const {
        std::size_t const w = g_atomic_int_get(&_write_idx);
        std::size_t const r = g_atomic_int_get(&_read_idx);

        if (w > r) {
            return ((r - w + _size) % _size) - 1;
        } else if (w < r) {
            return (r - w) - 1;
        } else {
            return _size - 1;
        }
    }

    std::size_t read_space() const {
        std::size_t const w = g_atomic_int_get(&_write_idx);
        std::size_t const r = g_atomic_int_get(&_read_idx);

        if (w > r) {
            return w - r;
        } else {
            return (w - r + _size) % _size;
        }
    }

    std::size_t capacity() const {
        return _size;
    }

    bool write(T const & src) {
        if (write_space()) {
            std::size_t const priv_write_idx = g_atomic_int_get(&_write_idx);
            void *p = static_cast<void*>(_buf + priv_write_idx);
            new (p) T(src);
            g_atomic_int_set(&_write_idx, (priv_write_idx + 1) % _size);
            return true;
        } else {
            return false;
        }
    }

    bool read(T & dst) {
        if (read_space()) {
            std::size_t const priv_read_idx = g_atomic_int_get(&_read_idx);
            T *p = _buf + priv_read_idx;
            dst = *p;
            p->~T();
            g_atomic_int_set(&_read_idx, (priv_read_idx + 1) % _size);
            return true;
        } else {
            return false;
        }
    }

protected:
    int _write_idx;
    int _read_idx;

    std::size_t _size;
    unsigned char *_buf_array;
    T *_buf;
};


} // namespace das


#endif // DAS_UTIL_RINGBUFFER_HH
