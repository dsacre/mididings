# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2012  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

try:
    import unittest2 as unittest
except:
    import unittest

import mididings.arguments as arguments
import mididings.misc as misc


class SetupTestCase(unittest.TestCase):

    def test_simple(self):
        @arguments.accept(int)
        def foo(a): pass

        foo(123)

        with self.assertRaises(TypeError):
            foo()
        with self.assertRaises(TypeError):
            foo(123.456)

        @arguments.accept(str, float)
        def bar(a, b): pass

        bar('blah', 123.456)

        with self.assertRaises(TypeError):
            bar()
        with self.assertRaises(TypeError):
            bar('blah')
        with self.assertRaises(TypeError):
            bar('blah', 123)

    def test_varargs(self):
        @arguments.accept(int, int)
        def foo(a, *args): pass

        foo(123)
        foo(123, 456, 789)

        with self.assertRaises(TypeError):
            foo()
        with self.assertRaises(TypeError):
            foo(123, 456, 'blah')

    def test_kwargs(self):
        @arguments.accept(kwargs={'a': int, 'b': str})
        def foo(**kwargs): pass

        foo()
        foo(a=123)
        foo(b='blah')
        foo(a=123, b='blah')

        with self.assertRaises(TypeError):
            foo(a='blah')
        with self.assertRaises(TypeError):
            foo(b=123)
        with self.assertRaises(TypeError):
            foo(c=123)

        @arguments.accept(int, kwargs={'b': str, 'c': float})
        def bar(a, **kwargs):
            self.assertEquals(a, 123)
            self.assertDictEqual(kwargs, {'b': 'blah', 'c': 123.456})

        bar(123, b='blah', c=123.456)
        bar(a=123, b='blah', c=123.456)

        with self.assertRaises(TypeError):
            bar(123, b=456, c=789)
        with self.assertRaises(TypeError):
            bar(123, b=456, c=789, d=123)

    def test_sequenceof(self):
        @arguments.accept(arguments.sequenceof(int))
        def foo(a):
            self.assertTrue(misc.issequenceof(a, int))

        foo([])
        foo([123, 456, 789])

        with self.assertRaises(TypeError):
            foo()
        with self.assertRaises(TypeError):
            foo(123, 456, 789)
        with self.assertRaises(TypeError):
            foo([123, 456, 'blah'])

    def test_with_rest(self):
        @arguments.accept(arguments.sequenceof(int), with_rest=True)
        def foo(a, *rest):
            self.assertTrue(misc.issequenceof(a, int))
            self.assertTupleEqual(rest, ())

        foo(123)
        foo(123, 456, 789)

        with self.assertRaises(TypeError):
            foo()
        with self.assertRaises(TypeError):
            foo(123, 456, 'blah')
        with self.assertRaises(TypeError):
            foo(123, [456, 789])

        @arguments.accept(int, arguments.sequenceof(int), with_rest=True)
        def bar(a, b, *rest):
            self.assertEqual(a, 123)
            self.assertListEqual(b, [456, 789])

        bar(123, 456, 789)

    def test_flatten_sequenceof(self):
        @arguments.accept(arguments.flatten_sequenceof(int))
        def foo(a):
            self.assertListEqual(a, [123, 456, 789])

        foo([123, 456, 789])
        foo([123, [456, 789]])
        foo([123, [[456], 789]])
        foo([[[123, [[[[456]]], 789]]]])

        with self.assertRaises(TypeError):
            foo([123, ['blah', 789]])

    def test_either(self):
        @arguments.accept(arguments.either(int, str))
        def foo(a): pass

        foo(123)
        foo('blah')

        with self.assertRaises(TypeError):
            foo()
        with self.assertRaises(TypeError):
            foo(123.456)

        @arguments.accept(arguments.either(int, arguments.sequenceof(str)))
        def bar(a): pass

        bar(123)
        bar(['doo', 'bee', 'doo'])

        with self.assertRaises(TypeError):
            bar('blah')
        with self.assertRaises(TypeError):
            bar([123, 456, 789])
