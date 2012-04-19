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


config = {
    'alsa-seq':     (platform.system() == 'Linux'),
    'jack-midi':    True,
    'smf':          False,
}

def check_option(name, argv):
    for arg in argv:
        if arg == '--enable-%s' % name:
            sys.argv.remove(arg)
            config[name] = True
        elif arg == '--disable-%s' % name:
            sys.argv.remove(arg)
            config[name] = False

check_option('alsa-seq', sys.argv[1:])
check_option('jack-midi', sys.argv[1:])
check_option('smf', sys.argv[1:])


def pkgconfig(pkg):
    status, output = getstatusoutput('pkg-config --libs --cflags %s' % pkg)
    if status:
        sys.exit("couldn't find package '%s'" % pkg)
    for token in output.split():
        opt, val = token[:2], token[2:]
        if opt == '-I':
            include_dirs.append(val)
        elif opt == '-l':
            libraries.append(val)
        elif opt == '-L':
            library_dirs.append(val)

def boost_lib_name(lib):
    for libdir in ('/usr/lib', '/usr/local/lib', '/usr/lib64', '/usr/local/lib64'):
        for suffix in ('', '-mt'):
            libname = 'lib%s%s.so' % (lib, suffix)
            if os.path.isfile(os.path.join(libdir, libname)):
                return lib + suffix
    return lib + '-mt'


sources = [
    'src/engine.cc',
    'src/patch.cc',
    'src/python_caller.cc',
    'src/python_module.cc',
    'src/backend/base.cc',
]

include_dirs = []
define_macros = []
libraries = []
library_dirs = []

include_dirs.append('src')

pkgconfig('glib-2.0')

libraries.append(boost_lib_name('boost_python'))
libraries.append(boost_lib_name('boost_thread'))

# uncomment and adapt these to build using a custom install of boost.
# you may also need to comment out the two lines above
#include_dirs.append('/opt/boost1.43/include')
#library_dirs.append('/opt/boost1.43/lib')
#libraries.append('boost_python')
#libraries.append('boost_thread')


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


# hack to modify the compiler flags from the distutils default
distutils_customize_compiler = sysconfig.customize_compiler
def my_customize_compiler(compiler):
    retval = distutils_customize_compiler(compiler)
    try:
        # -Wstrict-prototypes is not valid for C++
        compiler.compiler_so.remove('-Wstrict-prototypes')
        # immediately stop on error
        compiler.compiler_so.append('-Wfatal-errors')
        # some options to reduce the size of the binary
        compiler.compiler_so.remove('-g')
        compiler.compiler_so.append('-finline-functions')
        compiler.compiler_so.append('-fvisibility=hidden')
    except (AttributeError, ValueError):
        pass
    return retval
sysconfig.customize_compiler = my_customize_compiler


setup(
    name = 'mididings',
    version = '20120419',
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
    ],
)
