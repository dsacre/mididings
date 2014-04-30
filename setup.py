#!/usr/bin/env python

from distutils.core import setup, Extension
from distutils import sysconfig
import sys
import platform
import os.path

if sys.version_info >= (3,):
    from subprocess import getstatusoutput
else:
    from commands import getstatusoutput


version = '20120419'

config = {
    'alsa-seq':     (platform.system() == 'Linux'),
    'jack-midi':    True,
    'smf':          False,
    'c++11':        False,
    'debug':        True,
}

include_dirs = []
libraries = []
library_dirs = []
define_macros = []
extra_compile_args = []


define_macros.append(('VERSION', '"%s"' % version))


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
    compiler.compiler_so.append('-finline-functions')
    compiler.compiler_so.append('-fvisibility=hidden')
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


def lib_dirs():
    """
    Attempt to return the compiler's library search paths.
    """
    try:
        status, output = getstatusoutput(sysconfig.get_config_var('CC') + ' -print-search-dirs')
        for line in output.splitlines():
            if 'libraries: =' in line:
                libdirs = line.split('=', 1)[1]
                return libdirs.split(':')
        return []
    except Exception:
        return []


def boost_lib_name(name, add_suffixes=[]):
    """
    Try to figure out the correct boost library name (with or without "-mt"
    suffix, or with any of the given additional suffixes).
    """
    libdirs = ['/usr/lib', '/usr/local/lib', '/usr/lib64', '/usr/local/lib64'] + lib_dirs()
    for suffix in add_suffixes + ['', '-mt']:
        for libdir in libdirs:
            libname = 'lib%s%s.so' % (name, suffix)
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

if config['smf']:
    define_macros.append(('ENABLE_SMF', 1))
    sources.append('src/backend/smf.cc')
    pkgconfig('smf')

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
