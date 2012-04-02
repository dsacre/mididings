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

import mididings.misc as misc

import inspect
import sys
import collections
import functools
if sys.version_info < (2, 6):
    functools.reduce = reduce

import decorator


def accept(*constraints, **kwargs):
    """
    A decorator that applies type checks and other constraints to the arguments
    of the decorated function.

    Constraints must be given in the order of the function's positional
    arguments, one constraint per argument. If the function accepts variable
    arguments, one additional constraint must be specified, and will be applied
    to each of those arguments.

    If the optional keyword argument with_rest is True, all variable arguments
    are instead combined with the last regular positional argument into a
    single list. This list is then passed to the original function as a single
    argument.

    Keyword arguments are accepted if their name is in the kwargs_constraints
    dictionary, and the value from that dictionnary is used as the constraint
    to be applied.
    """
    with_rest = kwargs['with_rest'] if 'with_rest' in kwargs else False
    kwargs_constraints = kwargs['kwargs'] if 'kwargs' in kwargs else {}

    @decorator.decorator
    def constrain_arguments(f, *args, **kwargs):
        argspec = inspect.getargspec(f)
        arg_names = argspec[0]
        have_varargs = (argspec[1] is not None) and not with_rest

        mod_args = []
        mod_kwargs = {}

        assert ((len(constraints) == len(arg_names) and not have_varargs)
             or (len(constraints) == len(arg_names) + 1 and have_varargs))

        for constraint, arg_name, arg in zip(constraints, arg_names, args):
            if with_rest and arg_name == arg_names[-1]:
                # with_rest is True and this is the last argument: combine with varargs
                index = len(arg_names)
                arg = (arg,) + args[index:]

            a = _try_apply_constraint(constraint, arg, f.__name__, arg_name)
            mod_args.append(a)

        if have_varargs:
            index = len(arg_names)
            constraint = constraints[index]

            for arg in args[index:]:
                a = _try_apply_constraint(constraint, arg, f.__name__, None)
                mod_args.append(a)

        for k, v in kwargs.items():
            if k not in kwargs_constraints:
                message = "%s() got an unexpected keyword argument '%s'" % (f.__name__, k)
                raise TypeError(message)
            a = _try_apply_constraint(kwargs_constraints[k], v, f.__name__, k)
            mod_kwargs[k] = a

        return f(*mod_args, **mod_kwargs)

    return constrain_arguments


def _try_apply_constraint(constraint, arg, func_name, arg_name):
    try:
        return _apply_constraint(constraint, arg)
    except (TypeError, ValueError):
        ex = sys.exc_info()[1]
        typestr = "type" if isinstance(ex, TypeError) else "value"
        argstr = ("for parameter '%s'" % arg_name) if arg_name else "in varargs"

        message = "invalid %s %s of %s(): %s" % (typestr, argstr, func_name, str(ex))
        raise type(ex)(message)


def _apply_constraint(constraint, value):
    return _get_constraint(constraint)(value)


def _get_constraint(c):
    if inspect.isclass(c) or isinstance(c, tuple):
        # type or tuple: type or value constraint
        return _type_value_constraint(c)
    elif isinstance(c, list):
        if len(c) == 1:
            # single-item list: sequenceof() constraint
            return sequenceof(c[0])
        else:
            # list: tupleof() constraint
            return tupleof(*c)
    elif isinstance(c, _constraint):
        # contraint object
        return c
    elif isinstance(c, collections.Callable):
        # function or other callable object
        return transform(c)
    else:
        assert False


class _constraint(object):
    pass


class _type_value_constraint(_constraint):
    def __init__(self, constraint):
        self.constraint = constraint

    def __call__(self, arg):
        if inspect.isclass(self.constraint):
            # single type, check if instance
            if not isinstance(arg, self.constraint):
                message = "expected %s, got %s" % (self.constraint.__name__, type(arg).__name__)
                raise TypeError(message)
            return arg
        elif all(inspect.isclass(c) for c in self.constraint):
            # multiple types, check if instance
            if not isinstance(arg, self.constraint):
                types = ", ".join(c.__name__ for c in self.constraint)
                message = "expected one of (%s), got %s" % (types, type(arg).__name__)
                raise TypeError(message)
            return arg
        else:
            # multiple values, check if value is in sequence
            if arg not in self.constraint:
                args = ", ".join(repr(c) for c in self.constraint)
                message = "expected one of (%s), got %r" % (args, arg)
                raise ValueError(message)
            return arg

    def __repr__(self):
        if inspect.isclass(self.constraint):
            return self.constraint.__name__
        else:
            return repr(tuple(map(_type_value_constraint, self.constraint)))


class sequenceof(_constraint):
    """
    Checks that the argument is a sequence, and applies the same constraint to
    each element in that sequence.
    """
    def __init__(self, what):
        self.what = what

    def __call__(self, arg):
        if not misc.issequence(arg):
            raise TypeError("not a sequence")
        try:
            return [_apply_constraint(self.what, value) for value in arg]
        except (TypeError, ValueError):
            ex = sys.exc_info()[1]
            message = "illegal item in sequence: %s" % str(ex)
            raise type(ex)(message)

    def __repr__(self):
        return repr([_get_constraint(self.what)])


class tupleof(_constraint):
    """
    Checks that the argument is a sequence of a fixed length, and applies
    different constraints to each element in that sequence.
    """
    def __init__(self, *what):
        self.what = what

    def __call__(self, arg):
        if not misc.issequence(arg):
            raise TypeError("not a sequence")
        if len(arg) != len(self.what):
            message = "expected sequence of %d items, got %d" % (len(self.what), len(arg))
            raise ValueError(message)
        try:
            return [_apply_constraint(what, value) for what, value in zip(self.what, arg)]
        except (TypeError, ValueError):
            ex = sys.exc_info()[1]
            message = "illegal item in sequence: %s" % str(ex)
            raise type(ex)(message)

    def __repr__(self):
        return repr(list(map(_get_constraint, self.what)))


class flatten(_constraint):
    """
    Flattens all arguments into a single list, and applies a constraint to
    each element in that list.
    """
    def __init__(self, what):
        self.what = what

    def __call__(self, arg):
        try:
            return [_apply_constraint(self.what, value) for value in misc.flatten(arg)]
        except (TypeError, ValueError):
            ex = sys.exc_info()[1]
            message = "illegal item in sequence: %s" % str(ex)
            raise type(ex)(message)

    def __repr__(self):
        return 'flatten(%r)' % _get_constraint(self.what)


class each(_constraint):
    """
    Applies each of the given constraints.
    """
    def __init__(self, *requirements):
        self.requirements = requirements

    def __call__(self, arg):
        for what in self.requirements:
            arg = _apply_constraint(what, arg)
        return arg

    def __repr__(self):
        return 'each(%s)' % (', '.join(repr(_get_constraint(r)) for r in self.requirements))


class either(_constraint):
    """
    Accepts the argument if any of the given constraints can be applied.
    """
    def __init__(self, *alternatives):
        self.alternatives = alternatives

    def __call__(self, arg):
        errors = []
        for n, what in enumerate(self.alternatives):
            try:
                return _apply_constraint(what, arg)
            except (TypeError, ValueError):
                ex = sys.exc_info()[1]
                # 
                exstr = str(ex).replace('\n', '\n    ')
                errors.append("    #%d '%s': %s: %s" % (n + 1, _get_constraint(what), type(ex).__name__, exstr))
        message = "none of the alternatives matched:\n" + '\n'.join(errors)
        raise TypeError(message)

    def __repr__(self):
        return 'either(%s)' % (', '.join(repr(_get_constraint(a)) for a in self.alternatives))


class transform(_constraint):
    """
    Applies a function to its argument.
    """
    def __init__(self, function):
        self.function = function

    def __call__(self, arg):
        return self.function(arg)

    def __repr__(self):
        return _function_repr(self.function)


class condition(_constraint):
    """
    Accepts the argument if the given function returns True.
    """
    def __init__(self, function):
        self.function = function

    def __call__(self, arg):
        if not self.function(arg):
            message = "condition not met: %s" % _function_repr(self.function)
            raise ValueError(message)
        return arg

    def __repr__(self):
        return 'condition(%s)' % _function_repr(self.function)


class reduce_bitmask(_constraint):
    """
    Flattens all arguments and reduces them to a single bitmask.
    """
    def __init__(self, what):
        self.what = what

    def __call__(self, arg):
        seq = _apply_constraint(self.what, misc.flatten(arg))
        return functools.reduce(lambda x, y: x | y, seq)


def _function_repr(f):
    if misc.islambda(f):
        s = inspect.getsource(f).strip()

        # inspect.getsource() returns the entire line of code.
        # try to extract only the actual definition of the lambda function.
        # this will fail if more than one lambda function is defined on
        # the same line (and possibly for several other reasons...)
        start = s.index('lambda')
        end = len(s)
        parens = 0
        for n, c in enumerate(s[start:]):
            if parens == 0 and c in ',)]}':
                end = start + n
                break
            elif c in '([{':
                parens += 1
            elif c in ')]}':
                parens -= 1
        return s[start:end]
    else:
        return f.__name__
