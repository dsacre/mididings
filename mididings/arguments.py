# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2014  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

from mididings import misc

import inspect
import collections.abc as collections
import types
import functools

import decorator


class accept(object):
    """
    A decorator that applies type checks and other constraints to the
    arguments of the decorated function.

    Constraints must be given in the order of the function's positional
    arguments, one constraint per argument. If the function accepts
    variable arguments, one additional constraint must be specified, and
    will be applied to each of those arguments.

    If the optional keyword argument add_varargs is True, the decorated
    function will accept variable arguments, which are combined with the
    last regular positional argument into a single tuple. This tuple is
    then passed to the original function as a single argument.

    The kwargs dictionary, itself passed as an optional keyword argument,
    maps keyword arguments to the corresponding constraints. None can be
    used as a key in this dictionary to specify constraints for keyword
    arguments with any name.
    """
    def __init__(self, *constraints, **kwargs):
        self.add_varargs = (kwargs['add_varargs']
                            if 'add_varargs' in kwargs else False)
        kwargs_constraints = kwargs['kwargs'] if 'kwargs' in kwargs else {}

        # build all constraints
        self.constraints = [_make_constraint(c) for c in constraints]
        self.kwargs_constraints = dict((k, _make_constraint(v))
                                        for k, v in kwargs_constraints.items())

    def __call__(self, f):
        argspec = misc.getargspec(f)
        self.arg_names = argspec[0]
        self.have_varargs = (argspec[1] is not None) and not self.add_varargs

        assert ((len(self.constraints) == len(self.arg_names)
                    and not self.have_varargs)
             or (len(self.constraints) == len(self.arg_names) + 1
                    and self.have_varargs))

        if self.add_varargs:
            # add varargs to the signature and use decorator.FunctionMaker
            # directly to create the decorated function
            orig_signature = inspect.getargspec(f)
            assert orig_signature.varargs is None
            signature = orig_signature._replace(varargs='args')
            evaldict = self.wrapper.__globals__.copy()
            evaldict['_call_'] = self.wrapper
            evaldict['_func_'] = f
            return decorator.FunctionMaker.create(
                '%s%s' % (f.__name__, inspect.formatargspec(*signature)),
                'return _call_(_func_, %(shortsignature)s)',
                evaldict, undecorated=f, __wrapped__=f, doc=f.__doc__)
        else:
            return decorator.decorator(self.wrapper, f)

    def wrapper(self, f, *args, **kwargs):
        mod_args = []
        mod_kwargs = {}

        for constraint, arg_name, arg in zip(self.constraints,
                                             self.arg_names, args):
            if self.add_varargs and arg_name == self.arg_names[-1]:
                # add_varargs is True and this is the last argument:
                # combine with varargs
                index = len(self.arg_names)
                if isinstance(arg, types.GeneratorType):
                    arg = tuple(arg) + args[index:]
                else:
                    arg = (arg,) + args[index:]

            a = _apply_constraint(constraint, arg, f.__name__, arg_name)
            mod_args.append(a)

        if self.have_varargs:
            index = len(self.arg_names)
            constraint = self.constraints[index]

            for arg in args[index:]:
                a = _apply_constraint(constraint, arg, f.__name__, None)
                mod_args.append(a)

        for k, v in kwargs.items():
            if k in self.kwargs_constraints:
                a = _apply_constraint(self.kwargs_constraints[k],
                                      v, f.__name__, k)
            elif None in self.kwargs_constraints:
                a = _apply_constraint(self.kwargs_constraints[None],
                                      v, f.__name__, k)
            else:
                raise TypeError(
                        "%s() got an unexpected keyword argument '%s'" %
                        (f.__name__, k))
            mod_kwargs[k] = a

        return f(*mod_args, **mod_kwargs)


def _apply_constraint(constraint, arg, func_name, arg_name):
    try:
        return constraint(arg)
    except (TypeError, ValueError) as ex:
        typestr = "type" if isinstance(ex, TypeError) else "value"
        argstr = (("for parameter '%s'" % arg_name)
                        if arg_name else "in varargs")

        raise type(ex)("invalid %s %s of function %s():\n%s" %
                       (typestr, argstr, func_name, str(ex)))


def _make_constraint(c):
    if c is None:
        return _any()
    elif isinstance(c, list):
        if len(c) == 1:
            # single-item list: sequenceof() constraint
            return sequenceof(c[0])
        else:
            # list: tupleof() constraint
            return tupleof(*c)
    elif isinstance(c, dict):
        assert len(c) == 1
        # single-item dict: mappingof() constraint
        return mappingof(list(c.keys())[0], list(c.values())[0])
    elif isinstance(c, tuple):
        if all(inspect.isclass(cc) for cc in c):
            # multiple types: type constraint
            return _type_constraint(c, True)
        else:
            # any other tuple: value constraint
            return _value_constraint(c)
    elif inspect.isclass(c):
        # single type: type constraint
        return _type_constraint(c)
    elif isinstance(c, _constraint):
        # constraint object
        return c
    elif isinstance(c, collections.Callable):
        # function or other callable object
        return transform(c)
    else:
        assert False



class _constraint(object):
    pass


class _any(_constraint):
    def __call__(self, arg):
        return arg


class _type_constraint(_constraint):
    def __init__(self, types, multiple=False):
        self.types = types
        self.multiple = multiple

    def __call__(self, arg):
        if not self.multiple:
            # single type, check if instance
            if not isinstance(arg, self.types):
                raise TypeError("expected %s, got %s" %
                                (self.types.__name__, type(arg).__name__))
            return arg
        else:
            # multiple types, check if instance
            if not isinstance(arg, self.types):
                argtypes = ", ".join(c.__name__ for c in self.types)
                raise TypeError("expected one of (%s), got %s" %
                                (argtypes, type(arg).__name__))
            return arg

    def __repr__(self):
        if not self.multiple:
            return self.types.__name__
        else:
            return repr(tuple(map(_type_constraint, self.types)))


class _value_constraint(_constraint):
    def __init__(self, values):
        self.values = values

    def __call__(self, arg):
        if arg not in self.values:
            args = ", ".join(repr(c) for c in self.values)
            raise ValueError("expected one of (%s), got %r" % (args, arg))
        return arg

    def __repr__(self):
        return repr(tuple(self.values))


class nullable(_constraint):
    """
    Allows the argument to be None, instead of matching any other constraint.
    """
    def __init__(self, what):
        self.what = _make_constraint(what)

    def __call__(self, arg):
        if arg is None:
            return None
        return self.what(arg)

    def __repr__(self):
        return 'nullable(%r)' % self.what


class sequenceof(_constraint):
    """
    Checks that the argument is a sequence, and applies the same constraint to
    each element in that sequence.
    """
    def __init__(self, what):
        self.what = _make_constraint(what)

    def __call__(self, arg):
        if not misc.issequence(arg):
            raise TypeError("not a sequence")
        try:
            t = type(arg) if not isinstance(arg, types.GeneratorType) else list
            return t(self.what(value) for value in arg)
        except (TypeError, ValueError) as ex:
            raise type(ex)("illegal item in sequence: %s" % str(ex))

    def __repr__(self):
        return repr([self.what])


class tupleof(_constraint):
    """
    Checks that the argument is a sequence of a fixed length, and applies
    different constraints to each element in that sequence.
    """
    def __init__(self, *what):
        self.what = [_make_constraint(c) for c in what]

    def __call__(self, arg):
        if not misc.issequence(arg):
            raise TypeError("not a sequence")
        if len(arg) != len(self.what):
            raise ValueError("expected sequence of %d items, got %d" %
                             (len(self.what), len(arg)))
        try:
            t = type(arg) if not isinstance(arg, types.GeneratorType) else list
            return t(what(value) for what, value in zip(self.what, arg))
        except (TypeError, ValueError) as ex:
            raise type(ex)("illegal item in sequence: %s" % str(ex))

    def __repr__(self):
        return repr(self.what)


class mappingof(_constraint):
    """
    Checks that the argument is a dictionary, and applies constraints to each
    key and each value.
    """
    def __init__(self, fromwhat, towhat):
        self.fromwhat = _make_constraint(fromwhat)
        self.towhat = _make_constraint(towhat)

    def __call__(self, arg):
        if not isinstance(arg, dict):
            raise TypeError("not a dictionary")
        try:
            keys = (self.fromwhat(key) for key in arg.keys())
        except (TypeError, ValueError) as ex:
            raise type(ex)("illegal key in dictionary: %s" % str(ex))
        try:
            values = (self.towhat(value) for value in arg.values())
        except (TypeError, ValueError) as ex:
            raise type(ex)("illegal value in dictionary: %s" % str(ex))
        return dict(zip(keys, values))

    def __repr__(self):
        return repr({self.fromwhat: self.towhat})


class flatten(_constraint):
    """
    Flattens all arguments into a single list, and applies a constraint to
    each element in that list.
    """
    def __init__(self, what, return_type=None):
        self.what = _make_constraint(what)
        self.return_type = return_type

    def __call__(self, arg):
        try:
            r = [self.what(value) for value in misc.flatten(arg)]
            return r if self.return_type is None else self.return_type(r)
        except (TypeError, ValueError) as ex:
            raise type(ex)("illegal item in sequence: %s" % str(ex))

    def __repr__(self):
        return 'flatten(%r)' % self.what


class each(_constraint):
    """
    Applies each of the given constraints.
    """
    def __init__(self, *requirements):
        self.requirements = [_make_constraint(c) for c in requirements]

    def __call__(self, arg):
        for what in self.requirements:
            arg = what(arg)
        return arg

    def __repr__(self):
        return 'each(%s)' % (', '.join(repr(c) for c in self.requirements))


class either(_constraint):
    """
    Accepts the argument if any of the given constraints can be applied.
    """
    def __init__(self, *alternatives):
        self.alternatives = [_make_constraint(c) for c in alternatives]

    def __call__(self, arg):
        errors = []
        for n, what in enumerate(self.alternatives):
            try:
                return what(arg)
            except (TypeError, ValueError) as ex:
                exstr = str(ex).replace('\n', '\n    ')
                errors.append("    #%d %s: %s: %s" %
                                (n + 1, what, type(ex).__name__, exstr))
        raise TypeError("none of the alternatives matched:\n" +
                        '\n'.join(errors))

    def __repr__(self):
        return 'either(%s)' % (', '.join(repr(c) for c in self.alternatives))


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
            raise ValueError("condition not met: %s" %
                             _function_repr(self.function))
        return arg

    def __repr__(self):
        return 'condition(%s)' % _function_repr(self.function)


class reduce_bitmask(_constraint):
    """
    Flattens all arguments and reduces them to a single bitmask.
    """
    def __init__(self, what):
        self.what = _make_constraint(what)

    def __call__(self, arg):
        seq = self.what(misc.flatten(arg))
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
