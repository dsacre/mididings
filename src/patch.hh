/*
 * mididings
 *
 * Copyright (C) 2008  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef _PATCH_HH
#define _PATCH_HH

#include "midi_event.hh"
class Unit;

#include <vector>
#include <list>
#include <string>

#include <boost/shared_ptr.hpp>
#include <boost/range/iterator_range.hpp>

#include "util/debug.hh"


class Patch
{
  public:

    typedef std::list<MidiEvent> Events;
    typedef Events::iterator EventIter;
    typedef boost::iterator_range<EventIter> EventIterRange;

    typedef boost::shared_ptr<Unit> UnitPtr;


    class Module
    {
      public:
        Module()
        {
            DEBUG_FN();
        }

        virtual ~Module()
        {
            DEBUG_FN();
        }

        virtual EventIterRange process(Events &, EventIterRange) = 0;
    };

    typedef boost::shared_ptr<Module> ModulePtr;
    typedef std::vector<ModulePtr> ModuleVector;


    class Chain
      : public Module
    {
      public:
        Chain(ModuleVector m)
          : _modules(m)
        {
        }

        virtual EventIterRange process(Events &, EventIterRange);

      private:
        ModuleVector _modules;
    };


    class Fork
      : public Module
    {
      public:
        Fork(ModuleVector m, bool remove_duplicates)
          : _modules(m)
          , _remove_duplicates(remove_duplicates)
        {
        }

        virtual EventIterRange process(Events &, EventIterRange);

      private:
        ModuleVector _modules;
        bool _remove_duplicates;
    };


    class Single
      : public Module
    {
      public:
        Single(UnitPtr unit)
          : _unit(unit)
        {
        }

        virtual EventIterRange process(Events &, EventIterRange);

      private:
        UnitPtr _unit;
    };


  public:

    Patch(ModulePtr m)
      : _module(m)
    {
        DEBUG_FN();
    }

    ~Patch()
    {
        DEBUG_FN();
    }

    EventIterRange process(Events &, EventIterRange);


  private:

    static std::string debug_range(std::string const & str, Events & buf, EventIterRange r);


    ModulePtr _module;
};



#endif // _PATCH_HH
