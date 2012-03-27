/*
 * mididings
 *
 * Copyright (C) 2008-2012  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef MIDIDINGS_CURIOUS_ALLOC_HH
#define MIDIDINGS_CURIOUS_ALLOC_HH

#include <new>
#include <memory>
#include <functional>

#include "util/debug.hh"


namespace Mididings {


template <typename R>
class curious_alloc_base
{
  public:
    static std::size_t max_utilization() {
        return max_utilization_;
    }
    static std::size_t fallback_count() {
        return fallback_count_;
    }

  protected:
    static std::size_t max_utilization_;
    static std::size_t fallback_count_;
};


/*
 * Constant-time allocation/deallocation from a fixed-size pool of N elements.
 * deleted elements are not reclaimed until all (!) elements are deallocated.
 *
 * \tparam T    the type to be allocated
 * \tparam N    the size of the data pool
 * \tparam R    the original data type before rebind
 */
template <typename T, std::size_t N, typename R=T>
class curious_alloc
  : public curious_alloc_base<R>
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
        typedef curious_alloc<U, N, R> other;
    };

    curious_alloc() { }
    curious_alloc(curious_alloc<T, N, R> const &) { }
    template <class U>
    curious_alloc(curious_alloc<U, N, R> const &) { }

    ~curious_alloc() { }

    bool operator==(curious_alloc<T, N, R> const &) {
        return true;
    }
    bool operator!=(curious_alloc<T, N, R> const &) {
        return false;
    }

    pointer address(reference x) const { return &x; }
    const_pointer address(const_reference x) const { return &x; }

    pointer allocate(size_type n, void const * hint = 0) {
        (void)n;
        ASSERT(n == 1);

        if (index_ >= N) {
            // can't allocate from pool, use fallback allocator
            ++this->fallback_count_;
            return fallback_.allocate(n, hint);
        }
        ++count_;

        if (index_ >= this->max_utilization_) {
            this->max_utilization_ = index_ + 1;
        }
        return pool_ + (index_++);
    }

    void deallocate(pointer p, size_type n) {
        (void)n;
        ASSERT(n == 1);

        if (std::less<T*>()(p, pool_) || std::greater_equal<T*>()(p, pool_ + N)) {
            // address is not within pool address range, must have been
            // allocated using fallback allocator
            fallback_.deallocate(p, n);
            return;
        }

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
        return 1;
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
    static unsigned char pool_array_[N * sizeof(T)];
    static T* pool_;
    static std::size_t count_;
    static std::size_t index_;

    // fallback allocator in case this one runs out of space
    static std::allocator<T> fallback_;
};


template <typename R> std::size_t curious_alloc_base<R>::max_utilization_ = 0;
template <typename R> std::size_t curious_alloc_base<R>::fallback_count_ = 0;

template <typename T, std::size_t N, typename R> unsigned char curious_alloc<T, N, R>::pool_array_[N * sizeof(T)];
template <typename T, std::size_t N, typename R> T* curious_alloc<T, N, R>::pool_ = reinterpret_cast<T*>(&curious_alloc<T, N, R>::pool_array_);
template <typename T, std::size_t N, typename R> std::size_t curious_alloc<T, N, R>::count_ = 0;
template <typename T, std::size_t N, typename R> std::size_t curious_alloc<T, N, R>::index_ = 0;

template <typename T, std::size_t N, typename R> std::allocator<T> curious_alloc<T, N, R>::fallback_ = std::allocator<T>();


} // Mididings


#endif // MIDIDINGS_CURIOUS_ALLOC_HH
