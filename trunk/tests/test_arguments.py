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

from __future__ import with_statement

try:
    import unittest2 as unittest
except:
    import unittest

from mididings import arguments
from mididings import misc


class ArgumentsTestCase(unittest.TestCase):

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

    def test_isinstance(self):
        @arguments.accept((int, str))
        def foo(a): pass

        foo(123)
        foo('blah')

        with self.assertRaises(TypeError):
            foo()
        with self.assertRaises(TypeError):
            foo(123.456)

    def test_value(self):
        @arguments.accept((True, 42))
        def foo(a): pass

        foo(True)
        foo(42)

        with self.assertRaises(TypeError):
            foo()
        with self.assertRaises(ValueError):
            foo(False)
        with self.assertRaises(ValueError):
            foo(23)
        with self.assertRaises(ValueError):
            foo('blah')

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
            self.assertEqual(a, 123)
            self.assertDictEqual(kwargs, {'b': 'blah', 'c': 123.456})

        bar(123, b='blah', c=123.456)
        bar(a=123, b='blah', c=123.456)

        with self.assertRaises(TypeError):
            bar(123, b=456, c=789)
        with self.assertRaises(TypeError):
            bar(123, b=456, c=789, d=123)

    def test_nullable(self):
        @arguments.accept(arguments.nullable(int))
        def foo(a): pass

        foo(None)
        foo(42)

        with self.assertRaises(TypeError):
            foo()
        with self.assertRaises(TypeError):
            foo(123.456)

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

        @arguments.accept([str])
        def bar(a):
            self.assertTrue(misc.issequenceof(a, str))

        bar([])
        bar(['doo', 'bee', 'doo'])

        with self.assertRaises(TypeError):
            bar()
        with self.assertRaises(TypeError):
            bar('doo', 'bee', 'doo')
        with self.assertRaises(TypeError):
            bar('doo', 'bee', 123)

    def test_tupleof(self):
        @arguments.accept(arguments.tupleof(int, str))
        def foo(a): pass

        foo((123, 'blah'))
        foo([123, 'blah'])

        with self.assertRaises(TypeError):
            foo()
        with self.assertRaises(TypeError):
            foo(123, 'blah')
        with self.assertRaises(TypeError):
            foo((123, 456))
        with self.assertRaises(ValueError):
            foo([123, 'blah', 789])

        @arguments.accept([int, float])
        def bar(a): pass

        bar((123, 456.789))
        bar([123, 456.789])

        with self.assertRaises(TypeError):
            bar()
        with self.assertRaises(TypeError):
            bar(123, 456.789)
        with self.assertRaises(TypeError):
            bar((123, 'blah'))
        with self.assertRaises(ValueError):
            bar([123, 456.789, 'blah'])

    def test_mappingof(self):
        @arguments.accept(arguments.mappingof(int, float))
        def foo(a):
            for k, v in a.items():
                self.assertIsInstance(k, int)
                self.assertIsInstance(v, float)

        foo({})
        foo({23: 12.34, 42: 56.78})

        with self.assertRaises(TypeError):
            foo()
        with self.assertRaises(TypeError):
            foo({23: 12.34, 42: 666})
        with self.assertRaises(TypeError):
            foo({23: 12.34, 123.456: 56.78})

        @arguments.accept({str: int})
        def bar(a):
            for k, v in a.items():
                self.assertIsInstance(k, str)
                self.assertIsInstance(v, int)

        bar({})
        bar({'foo': 23, 'bar': 42})

        with self.assertRaises(TypeError):
            bar()
        with self.assertRaises(TypeError):
            bar({'foo': 23, 'bar': 123.456})
        with self.assertRaises(TypeError):
            bar({'foo': 23, 666: 42})

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

        @arguments.accept(int, [int], with_rest=True)
        def bar(a, b, *rest):
            self.assertEqual(a, 123)
            self.assertTupleEqual(b, (456, 789))

        bar(123, 456, 789)

    def test_flatten(self):
        @arguments.accept(arguments.flatten(int))
        def foo(a):
            self.assertListEqual(a, [123, 456, 789])

        foo([123, 456, 789])
        foo([123, [456, 789]])
        foo([123, [[456], 789]])
        foo([[[123, [[[[456]]], 789]]]])

        with self.assertRaises(TypeError):
            foo([123, ['blah', 789]])

    def test_each(self):
        @arguments.accept(arguments.each(int, arguments.condition(lambda x: x > 0)))
        def foo(a): pass

        foo(1)
        foo(123)

        with self.assertRaises(ValueError):
            foo(0)
        with self.assertRaises(ValueError):
            foo(-456)

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

    def test_condition(self):
        @arguments.accept(arguments.condition(lambda x: x%2 == 0))
        def foo(a): pass

        foo(2)
        foo(42)

        with self.assertRaises(ValueError):
            foo(1)
        with self.assertRaises(ValueError):
            foo(23)

        @arguments.accept(arguments.condition(lambda x: x > 0))
        def bar(a): pass

        bar(1)
        bar(42)

        with self.assertRaises(ValueError):
            bar(0)
        with self.assertRaises(ValueError):
            bar(-23)

    def test_repr(self):
        self.assertEqual(repr(arguments._make_constraint(int)), 'int')
        self.assertEqual(repr(arguments._make_constraint(arguments.nullable(int))), 'nullable(int)')
        self.assertEqual(repr(arguments._make_constraint([int])), '[int]')
        self.assertEqual(repr(arguments._make_constraint((23, 42))), '(23, 42)')
        self.assertEqual(repr(arguments._make_constraint((int, float, str))), '(int, float, str)')
        self.assertEqual(repr(arguments._make_constraint([int, float, str])), '[int, float, str]')
        self.assertEqual(repr(arguments._make_constraint({int: str})), '{int: str}')
        self.assertEqual(repr(arguments._make_constraint(arguments.flatten(int))), 'flatten(int)')
        self.assertEqual(repr(arguments._make_constraint(arguments.each(int, float))), 'each(int, float)')
        self.assertEqual(repr(arguments._make_constraint(arguments.either(int, str))), 'either(int, str)')
        self.assertEqual(repr(arguments._make_constraint(lambda x: x / 2)), 'lambda x: x / 2')
        self.assertEqual(repr(arguments._make_constraint(arguments.condition(lambda x: x < 3))), 'condition(lambda x: x < 3)')

        def foo(x): x

        constraint = arguments.either(
            arguments.each(int, arguments.condition(lambda x: x%2 == 0)),
            arguments.sequenceof(foo),
            str,
        )
        reprs = 'either(each(int, condition(lambda x: x%2 == 0)), [foo], str)'

        self.assertEqual(repr(arguments._make_constraint(constraint)), reprs)
