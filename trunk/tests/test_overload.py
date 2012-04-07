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

from mididings import overload


class OverloadTestCase(unittest.TestCase):

    def setUp(self):
        # yuck!
        self.registry_bak = overload._registry.copy()

    def tearDown(self):
        # yuck!
        overload._registry = self.registry_bak

    def test_call(self):
        funcs = [
            lambda a: 1,
            lambda a, b: 2,
        ]

        self.assertEqual(overload.call([23], {}, funcs), 1)
        self.assertEqual(overload.call([], {'a': 23}, funcs), 1)
        self.assertEqual(overload.call([23, 42], {}, funcs), 2)
        self.assertEqual(overload.call([23], {'b': 42}, funcs), 2)
        self.assertEqual(overload.call([], {'a': 23, 'b': 42}, funcs), 2)

        with self.assertRaises(TypeError):
            overload.call([], {}, funcs)
        with self.assertRaises(TypeError):
            overload.call([23, 42, 69], {}, funcs)
        with self.assertRaises(TypeError):
            overload.call([23, 42], {'c': 69}, funcs)

    def test_mark(self):
        @overload.mark
        def foo(a):
            return 1

        @overload.mark
        def foo(a, b):
            return 2

        self.assertEqual(foo(23), 1)
        self.assertEqual(foo(a=23), 1)
        self.assertEqual(foo(23, 42), 2)
        self.assertEqual(foo(a=23, b=42), 2)

        with self.assertRaises(TypeError):
            foo()
        with self.assertRaises(TypeError):
            foo(23, 42, 69)
        with self.assertRaises(TypeError):
            foo(23, 42, c=69)

    def test_argnames(self):
        @overload.mark
        def foo(a, b):
            return 1

        @overload.mark
        def foo(c, d):
            return 2

        self.assertEqual(foo(23, 42), 1)
        self.assertEqual(foo(23, b=42), 1)
        self.assertEqual(foo(a=23, b=42), 1)
        self.assertEqual(foo(23, d=42), 2)
        self.assertEqual(foo(c=23, d=42), 2)

        with self.assertRaises(TypeError):
            foo(23, e=42)

    def test_defargs(self):
        @overload.mark
        def foo(a=23):
            return 1

        @overload.mark
        def foo(a, b=42):
            return 2

        @overload.mark
        def foo(a, b, c=69):
            return 3

        @overload.mark
        def foo(a, b=42, d=123):
            return 4

        self.assertEqual(foo(), 1)
        self.assertEqual(foo(23), 1)
        self.assertEqual(foo(a=23), 1)
        self.assertEqual(foo(23, 42), 2)
        self.assertEqual(foo(a=23, b=42), 2)
        self.assertEqual(foo(23, 42, 69), 3)
        self.assertEqual(foo(23, 42, c=69), 3)
        self.assertEqual(foo(a=23, b=42, c=69), 3)
        self.assertEqual(foo(23, 42, d=123), 4)
        self.assertEqual(foo(a=23, b=42, d=123), 4)
        self.assertEqual(foo(a=23, d=123), 4)

        with self.assertRaises(TypeError):
            foo(23, c=69)

    def test_varargs(self):
        @overload.mark
        def foo(a):
            return 1

        @overload.mark
        def foo(b, c, d=69):
            return 2

        @overload.mark
        def foo(d, e=42, *args):
            return 3

        self.assertEqual(foo(23), 1)
        self.assertEqual(foo(23, 42), 2)
        self.assertEqual(foo(23, 42, 69), 2)
        self.assertEqual(foo(23, 42, d=69), 2)
        self.assertEqual(foo(23, e=42), 3)
        self.assertEqual(foo(d=23, e=42), 3)
        self.assertEqual(foo(23, 42, 69, 123), 3)

        with self.assertRaises(TypeError):
            foo(e=23)

    def test_partial(self):
        @overload.partial((23,))
        def foo(a, b):
            return a, b

        self.assertEqual(foo(42), (23, 42))
        self.assertEqual(foo(23, 42), (23, 42))
        self.assertEqual(foo(b=42), (23, 42))
        self.assertEqual(foo(a=23, b=42), (23, 42))

        with self.assertRaises(TypeError):
            foo()
        with self.assertRaises(TypeError):
            foo(23, 42, 69)

        @overload.partial((23,))
        def bar(a, b, c=123):
            return a, b, c

        self.assertEqual(bar(42), (23, 42, 123))
        self.assertEqual(bar(23, 42), (23, 42, 123))
        self.assertEqual(bar(42, c=123), (23, 42, 123))
        self.assertEqual(bar(23, 42, 123), (23, 42, 123))

        with self.assertRaises(TypeError):
            bar()
        with self.assertRaises(TypeError):
            bar(23, 42, 69, 123)
