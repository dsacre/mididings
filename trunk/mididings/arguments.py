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
    if inspect.isclass(constraint):
        # single type, check if instance
        if not isinstance(value, constraint):
            message = "expected %s, got %s" % (constraint.__name__, type(value).__name__)
            raise TypeError(message)
        return value
    elif misc.issequence(constraint) and all(inspect.isclass(c) for c in constraint):
        # multiple types, check if instance
        if not isinstance(value, constraint):
            types = ", ".join(c.__name__ for c in constraint)
            message = "expected one of (%s), got %s" % (types, type(value).__name__)
            raise TypeError(message)
        return value
    elif misc.issequence(constraint):
        # multiple values, check if value is in sequence
        if value not in constraint:
            values = ", ".join(repr(c) for c in constraint)
            message = "expected one of (%s), got %r" % (values, value)
            raise ValueError(message)
        return value
    elif isinstance(constraint, collections.Callable):
        # callable
        return constraint(value)
    else:
        assert False


class sequenceof(object):
    """
    Checks that the argument is a sequence, and applies a constraint to each
    element in that sequence.
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


class flatten_sequenceof(object):
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


class each(object):
    """
    Applies each of the given constraints.
    """
    def __init__(self, *requirements):
        self.requirements = requirements

    def __call__(self, arg):
        for what in self.requirements:
            arg = _apply_constraint(what, arg)
        return arg


class either(object):
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
                errors.append("error %d: %s: %s" % (n + 1, type(ex).__name__, str(ex)))
        message = "none of the alternatives matched:\n" + '\n'.join(errors)
        raise TypeError(message)


class reduce_bitmask(object):
    """
    Flattens all arguments and reduces them to a single bitmask.
    """
    def __init__(self, what):
        self.what = what

    def __call__(self, arg):
        seq = _apply_constraint(self.what, misc.flatten(arg))
        return functools.reduce(lambda x, y: x | y, seq)


class greater_equal(object):
    """
    Raises an exception if the argument is not greater or equal to the
    given value.
    """
    def __init__(self, than_what):
        self.than_what = than_what

    def __call__(self, arg):
        if arg < self.than_what:
            message = "must be greater or equal to %r" % self.than_what
            raise ValueError(message)
        return arg
