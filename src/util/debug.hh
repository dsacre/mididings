/*
 * Copyright (C) 2007-2008  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef DAS_UTIL_DEBUG_HH
#define DAS_UTIL_DEBUG_HH


#ifndef NDEBUG
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


#endif // DAS_UTIL_DEBUG_HH
