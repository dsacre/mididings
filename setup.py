#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import platform
import sys

from distutils import sysconfig

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

if sys.version_info >= (3,):
    from subprocess import getstatusoutput
else:
    from commands import getstatusoutput


version = '2015'

status, output = getstatusoutput('git rev-parse --short HEAD')
if not status:
    version = '%s+r%s' % (version, output)

config = {
    'alsa-seq':     (platform.system() == 'Linux'),
    'jack-midi':    True,
    'c++11':        False,
    'debug':        True,
}

include_dirs = []
libraries = []
library_dirs = []
define_macros = []
extra_compile_args = []

define_macros.append(('VERSION', '%s' % version))


# parse and then remove additional custom command line options
for opt in config.keys():
    for arg in sys.argv:
        if arg == '--enable-%s' % opt:
            sys.argv.remove(arg)
            config[opt] = True
        elif arg == '--disable-%s' % opt:
            sys.argv.remove(arg)
            config[opt] = False


# hack to modify the compiler flags from the distutils default
distutils_customize_compiler = sysconfig.customize_compiler

def my_customize_compiler(compiler):
    retval = distutils_customize_compiler(compiler)
    # -Wstrict-prototypes is not valid for C++
    try:
        compiler.compiler_so.remove('-Wstrict-prototypes')
    except ValueError:
        pass

    if not config['debug']:
        try:
            # the -g flag might occur twice in python's compiler flags
            compiler.compiler_so.remove('-g')
            compiler.compiler_so.remove('-g')
        except ValueError:
            pass

    # immediately stop on error
    compiler.compiler_so.append('-Wfatal-errors')
    # some options to reduce the size of the binary
    compiler.compiler_so.append('-fvisibility-inlines-hidden')
    return retval

sysconfig.customize_compiler = my_customize_compiler


def pkgconfig(name):
    """
    Run pkg-config for the given package, and add the required flags to our
    list of build arguments.
    """
    status, output = getstatusoutput('pkg-config --libs --cflags %s' % name)
    if status:
        sys.exit("couldn't find package '%s'" % name)
    for token in output.split():
        opt, val = token[:2], token[2:]
        if opt == '-I':
            include_dirs.append(val)
        elif opt == '-l':
            libraries.append(val)
        elif opt == '-L':
            library_dirs.append(val)


def library_path_dirs():
    library_path = os.environ.get('LIBRARY_PATH')
    return library_path.split(':') if library_path else []


def lib_dirs():
    """
    Attempt to return the compiler's library search paths.

    Also include paths from LIBRARY_PATH environment variable.
    """
    env_libs = library_path_dirs()
    try:
        status, output = getstatusoutput('LC_ALL=C ' +
                    sysconfig.get_config_var('CC') + ' -print-search-dirs')
        for line in output.splitlines():
            if 'libraries: =' in line:
                libdirs = [os.path.normpath(p)
                    for p in line.split('=', 1)[1].split(':')]
                return env_libs + libdirs
        return env_libs
    except Exception:
        return env_libs


def boost_lib_name(name, add_suffixes=[]):
    """
    Try to figure out the correct boost library name (with or without "-mt"
    suffix, or with any of the given additional suffixes).
    """
    for suffix in add_suffixes + ['', '-mt']:
        for libdir in lib_dirs():
            for ext in ['so'] + ['dylib'] * (sys.platform == 'darwin'):
                libname = 'lib%s%s.%s' % (name, suffix, ext)
                if os.path.isfile(os.path.join(libdir, libname)):
                    return name + suffix
    return name


sources = [
    'src/engine.cc',
    'src/patch.cc',
    'src/python_caller.cc',
    'src/send_midi.cc',
    'src/python_module.cc',
    'src/backend/base.cc',
]

include_dirs.append('src')

boost_python_suffixes = ['-py%d%d' % sys.version_info[:2]]
if sys.version_info[0] == 3:
    boost_python_suffixes.append('3')
libraries.append(boost_lib_name('boost_python', boost_python_suffixes))
libraries.append(boost_lib_name('boost_thread'))

library_dirs.extend(library_path_dirs())


if config['alsa-seq']:
    define_macros.append(('ENABLE_ALSA_SEQ', 1))
    sources.append('src/backend/alsa.cc')
    pkgconfig('alsa')

if config['jack-midi']:
    define_macros.append(('ENABLE_JACK_MIDI', 1))
    sources.extend(['src/backend/jack.cc',
                    'src/backend/jack_buffered.cc',
                    'src/backend/jack_realtime.cc'])
    pkgconfig('jack')

if config['c++11']:
    extra_compile_args.append('-std=c++0x')
else:
    pkgconfig('glib-2.0')


setup(
    name = 'mididings',
    version = version,
    author = 'Dominic Sacre',
    author_email = 'dominic.sacre@gmx.de',
    url = 'http://das.nasophon.de/mididings/',
    description = 'a MIDI router/processor',
    license = 'GPL',
    ext_modules = [
        Extension(
            name = '_mididings',
            sources = sources,
            include_dirs = include_dirs,
            library_dirs = library_dirs,
            libraries = libraries,
            define_macros = define_macros,
            extra_compile_args = extra_compile_args,
        ),
    ],
    packages = [
        'mididings',
        'mididings.units',
        'mididings.extra',
        'mididings.live',
    ],
    scripts = [
        'scripts/mididings',
        'scripts/livedings',
        'scripts/send_midi',
    ],
)
