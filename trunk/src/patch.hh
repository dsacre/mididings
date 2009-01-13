/*
 * mididings
 *
 * Copyright (C) 2008-2009  Dominic Sacré  <dominic.sacre@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 */

#ifndef _PATCH_HH
#define _PATCH_HH

#include "config.hh"
#include "midi_event.hh"
class Unit;
class UnitEx;

#include <vector>
#include <list>
#include <string>

#include <boost/shared_ptr.hpp>
#include <boost/range/iterator_range.hpp>

#include "util/debug.hh"
#include "util/curious_alloc.hh"


class Patch
{
  public:

    typedef std::list<MidiEvent, das::curious_alloc<MidiEvent, Config::MAX_EVENTS> > Events;
    typedef Events::iterator EventIter;
    typedef boost::iterator_range<EventIter> EventRange;

    typedef boost::shared_ptr<Unit> UnitPtr;
    typedef boost::shared_ptr<UnitEx> UnitExPtr;


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


#endif // _PATCH_HH
