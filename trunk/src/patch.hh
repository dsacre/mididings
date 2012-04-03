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

#ifndef MIDIDINGS_PATCH_HH
#define MIDIDINGS_PATCH_HH

#include "config.hh"
#include "midi_event.hh"
#include "curious_alloc.hh"

#include <vector>
#include <list>
#include <string>

#include <boost/shared_ptr.hpp>
#include <boost/noncopyable.hpp>

#include "util/iterator_range.hh"
#include "util/counted_objects.hh"
#include "util/debug.hh"


namespace Mididings {

class Engine;

namespace Units {
    class Unit;
    class UnitEx;
}


class Patch
  : boost::noncopyable
  , das::counted_objects<Patch>
{
  private:

    typedef std::list<MidiEvent, curious_alloc<MidiEvent, Config::MAX_EVENTS> > EventListRT;
    typedef std::list<MidiEvent> EventList;

    // deriving from a standard container. get over it.
    template <typename T>
    class EventBufferType
      : public T
      , boost::noncopyable
    {
      public:
        typedef typename T::iterator Iterator;
        typedef das::iterator_range<typename T::iterator> Range;

        EventBufferType(Engine & engine)
          : _engine(engine)
        { }

        Engine & engine() const {
            return _engine;
        }

      private:
        Engine & _engine;
    };


  public:

    /**
     * The buffer type for RT-safe event processing, using a std::list with
     * custom allocator.
     */
    typedef EventBufferType<EventListRT> EventBufferRT;

    /**
     * Basically a regular std::list with some handy typedefs.
     */
    typedef EventBufferType<EventList> EventBuffer;


    typedef boost::shared_ptr<Units::Unit> UnitPtr;
    typedef boost::shared_ptr<Units::UnitEx> UnitExPtr;


    /**
     * The module base class.
     */
    class Module
      : boost::noncopyable
      , das::counted_objects<Module>
    {
      public:
        Module() { }
        virtual ~Module() { }

        virtual void process(EventBufferRT & buffer, EventBufferRT::Range & range) const = 0;
        virtual void process(EventBuffer & buffer, EventBuffer::Range & range) const = 0;
    };

    typedef boost::shared_ptr<Module> ModulePtr;
    typedef std::vector<ModulePtr> ModuleVector;


  private:

    /**
     * The actual base class for each module type, using the CRTP to circumvent
     * C++'s lack of virtual template member functions.
     */
    template <typename Derived>
    class ModuleImpl
      : public Module
    {
      public:
        virtual void process(EventBufferRT & buffer, EventBufferRT::Range & range) const {
            Derived const & d = *static_cast<Derived const*>(this);
            d.template process<EventBufferRT>(buffer, range);
        }

        virtual void process(EventBuffer & buffer, EventBuffer::Range & range) const {
            Derived const & d = *static_cast<Derived const*>(this);
            d.template process<EventBuffer>(buffer, range);
        }
    };


  public:

    /**
     * A chain of units connected in series.
     */
    class Chain
      : public ModuleImpl<Chain>
    {
      public:
        Chain(ModuleVector const & modules)
          : _modules(modules)
        { }

        template <typename B>
        void process(B & buffer, typename B::Range & range) const;

      private:
        ModuleVector const _modules;
    };


    /**
     * A fork, units connected in parallel.
     */
    class Fork
      : public ModuleImpl<Fork>
    {
      public:
        Fork(ModuleVector const & modules, bool remove_duplicates)
          : _modules(modules)
          , _remove_duplicates(remove_duplicates)
        { }

        template <typename B>
        void process(B & buffer, typename B::Range & range) const;

      private:
        ModuleVector const _modules;
        bool const _remove_duplicates;
    };


    /**
     * A single unit.
     */
    class Single
      : public ModuleImpl<Single>
    {
      public:
        Single(UnitPtr const & unit)
          : _unit(unit)
        { }

        template <typename B>
        void process(B & buffer, typename B::Range & range) const;

      private:
        UnitPtr const _unit;
    };


    /**
     * A single extended unit.
     */
    class Extended
      : public ModuleImpl<Extended>
    {
      public:
        Extended(UnitExPtr const & unit)
          : _unit(unit)
        { }

        template <typename B>
        void process(B & buffer, typename B::Range & range) const;

      private:
        UnitExPtr const _unit;
    };


  public:

    /**
     * Creates a new patch.
     *
     * \param module    the root module of the patch
     */
    Patch(ModulePtr const & module)
      : _module(module)
    { }

    /**
     * Processes events.
     *
     * \tparam B                the type of event buffer
     * \param[in,out] buffer    the event buffer
     * \param[in,out] range     the iterator range of events to be processed
     */
    template <typename B>
    void process(B & buffer, typename B::Range & range) const;

    /**
     * Processes all events in the given buffer.
     *
     * \tparam B                the type of event buffer
     * \param[in,out] buffer    the event buffer
     */
    template <typename B>
    void process(B & buffer) const {
        typename B::Range range(buffer.begin(), buffer.end());
        process(buffer, range);
    }


    /**
     * Replaces event with one or more events, returns the range containing the new events.
     */
    template <typename B, typename IterT>
    static inline typename B::Range replace_event(B & buffer, typename B::Iterator it, IterT begin, IterT end) {
        it = buffer.erase(it);

        typename B::Iterator first = buffer.insert(it, *begin);
        buffer.insert(it, ++begin, end);

        return typename B::Range(first, it);
    }

    /**
     * Leaves event unchanged, returns a range containing the single event.
     */
    template <typename B>
    static inline typename B::Range keep_event(B & /*buffer*/, typename B::Iterator it) {
        typename B::Range ret(it, 1);
        return ret;
    }

    /**
     * Removes event, returns empty range.
     */
    template <typename B>
    static inline typename B::Range delete_event(B & buffer, typename B::Iterator it) {
        it = buffer.erase(it);
        return typename B::Range(it);
    }


  private:

    template <typename B>
    static std::string debug_range(std::string const & str, B const & buffer, typename B::Range const & range);


    ModulePtr const _module;
};


} // Mididings


#endif // MIDIDINGS_PATCH_HH
