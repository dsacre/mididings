/*
 * Copyright (C) 2008  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef _DAS_CURIOUS_ALLOC_HH
#define _DAS_CURIOUS_ALLOC_HH

#include <new>

#include "util/debug.hh"

//#include <iostream> /////


namespace das {

/*
 * constant-time allocation/deallocation from a fixed size pool of N elements.
 * deleted elements are not reclaimed until all (!) elements are deallocated.
 */
template <typename T, std::size_t N>
class curious_alloc
{
  public:
    typedef std::size_t size_type;
    typedef std::ptrdiff_t difference_type;
    typedef T * pointer;
    typedef T const * const_pointer;
    typedef T & reference;
    typedef T const & const_reference;
    typedef T value_type;

    template <class U>
    struct rebind {
        typedef curious_alloc<U, N> other;
    };

    curious_alloc() { }

    template <class U>
    curious_alloc(curious_alloc<U, N> const &) { }

    pointer address(reference x) const { return &x; }
    const_pointer address(const_reference x) const { return &x; }

    pointer allocate(size_type n, void const * /*hint*/ = 0) {
        (void)n;
        ASSERT(n == 1);
        ASSERT(index_ < N);

        if (index_ >= N) {
            throw std::bad_alloc();
        }

//        static std::size_t max_index = 0;
//        if (index_ > max_index) {
//            max_index = index_;
//            std::cout << "max_index: " << max_index << std::endl;
//        }

        ++count_;
        return pool_ + (index_++);
    }

    void deallocate(pointer p, size_type n) {
        deallocate(static_cast<void *>(p), n);
    }
    void deallocate(void * p, size_type n) {
        (void)n;
        ASSERT(n == 1);

        if (p == pool_ + index_ - 1) {
            // removing last element, can be reused
            --index_;
        }
        if (!(--count_)) {
            // no allocations left, start over
            index_ = 0;
        }
    }

    size_type max_size() const throw() {
        return N;
    }

    void construct(pointer p, T const & val) {
        new (static_cast<void *>(p)) T(val);
    }
    void construct(pointer p) {
        new (static_cast<void *>(p)) T();
    }
    void destroy(pointer p) {
        p->~T();
    }

private:
    static T pool_[N];
    static std::size_t count_;
    static std::size_t index_;
};


template <typename T, std::size_t N> T curious_alloc<T, N>::pool_[N];
template <typename T, std::size_t N> std::size_t curious_alloc<T, N>::count_ = 0;
template <typename T, std::size_t N> std::size_t curious_alloc<T, N>::index_ = 0;


} // namespace das

#endif // _DAS_CURIOUS_ALLOC_HH
