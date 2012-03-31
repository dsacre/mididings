#!/usr/bin/env python

import mididings.misc as misc

import inspect
import sys
import functools
if sys.version_info < (2,6):
    functools.reduce = reduce

import decorator


def accept(*constraints, **kwargs):
    with_rest = kwargs['with_rest'] if 'with_rest' in kwargs else False

    def argument_wrapper(f, *orig_args, **kwargs):
        argspec = inspect.getargspec(f)
        arg_names = argspec[0]
        have_varargs = (argspec[1] is not None) and not with_rest

        args = []

        assert ((len(constraints) == len(arg_names) and not have_varargs)
             or (len(constraints) == len(arg_names) + 1 and have_varargs))

        for constraint, arg_name, orig_arg in zip(constraints, arg_names, orig_args):
            if with_rest and arg_name == arg_names[-1]:
                index = len(arg_names)
                orig_arg = (orig_arg,) + orig_args[index:]
            try:
                arg = _apply_constraint(constraint, orig_arg)
                args.append(arg)
            except TypeError:
                # all this ugliness is just for python 2.5
                _, ex, _ = sys.exc_info()
                raise TypeError("invalid type for parameter '%s' of %s(): %s" % (arg_name, f.__name__, str(ex)))
            except ValueError:
                _, ex, _ = sys.exc_info()
                raise ValueError("invalid value for parameter '%s' of %s(): %s" % (arg_name, f.__name__, str(ex)))

        if have_varargs:
            index = len(arg_names)
            constraint = constraints[index]
            try:
                args = _apply_constraint(constraint, orig_args[index:])
                args.extend(args)
            except TypeError:
                _, ex, _ = sys.exc_info()
                raise TypeError("invalid type in varargs of %s(): %s" % (f.__name__, str(ex)))
            except ValueError:
                _, ex, _ = sys.exc_info()
                raise ValueError("invalid value in varargs of %s(): %s" % (f.__name__, str(ex)))

        return f(*args, **kwargs)

    return decorator.decorator(argument_wrapper)


def _apply_constraint(constraint, value):
    if inspect.isclass(constraint):
        if not isinstance(value, constraint):
            raise TypeError("should be %s, got %s" % (constraint.__name__, type(value).__name__))
        return value
    elif misc.issequence(constraint) and all(inspect.isclass(c) for c in constraint):
        if not isinstance(value, constraint):
            raise TypeError("should be one of (%s), got %s" % (", ".join(c.__name__ for c in constraint), type(value).__name__))
        return value
    elif misc.issequence(constraint):
        if value not in constraint:
            raise ValueError("should be one of (%s), got %r" % (", ".join(repr(c) for c in constraint), value))
        return value
    else:
        return constraint(value)


def _constraint(f):
    def apply(constraint):
        return functools.partial(f, constraint)
    return apply


@_constraint
def sequenceof(constraint, seq):
    if not misc.issequence(seq):
        raise TypeError("not a sequence")
    r = []
    for value in seq:
        try:
            r.append(_apply_constraint(constraint, value))
        except (TypeError, ValueError) as ex:
            raise type(ex)("invalid item in sequence: %s" % str(ex))
    return r


@_constraint
def flatten(constraint, arg):
    return [_apply_constraint(constraint, a) for a in misc.flatten(arg)]


@_constraint
def flattened(constraint, arg):
    return _apply_constraint(constraint, misc.flatten(arg))


@_constraint
def reduce_bitmask(constraint, arg):
    # reduce all arguments to a single bitmask
    seq = _apply_constraint(constraint, arg)
    return functools.reduce(lambda x,y: x|y, seq)
