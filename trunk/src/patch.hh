/*
 * mididings
 *
 * Copyright (C) 2008-2011  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef MIDIDINGS_PATCH_HH
#define MIDIDINGS_PATCH_HH

#include "config.hh"
#include "midi_event.hh"
#include "curious_alloc.hh"

#include <vector>
#include <list>
#include <string>

#include <boost/shared_ptr.hpp>
#include <boost/range/iterator_range.hpp>

#include "util/debug.hh"


namespace Mididings {

namespace Units {
class Unit;
class UnitEx;
}


class Patch
{
  public:

    typedef std::list<MidiEvent, curious_alloc<MidiEvent, Config::MAX_EVENTS> > Events;
    typedef Events::iterator EventIter;
    typedef boost::iterator_range<EventIter> EventRange;

    typedef boost::shared_ptr<Units::Unit> UnitPtr;
    typedef boost::shared_ptr<Units::UnitEx> UnitExPtr;


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

        virtual void process(Events &, EventRange &) = 0;
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

        virtual void process(Events &, EventRange &);

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

        virtual void process(Events &, EventRange &);

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

        virtual void process(Events &, EventRange &);

      private:
        UnitPtr _unit;
    };


    class Extended
      : public Module
    {
      public:
        Extended(UnitExPtr unit)
          : _unit(unit)
        {
        }

        virtual void process(Events &, EventRange &);

      private:
        UnitExPtr _unit;
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

    void process(Events &, EventRange &);

    void process(Events & buf)
    {
        EventRange r(buf);
        process(buf, r);
    }


  private:

    static std::string debug_range(std::string const & str, Events & buf, EventRange const & r);


    ModulePtr _module;
};


} // Mididings


#endif // MIDIDINGS_PATCH_HH
