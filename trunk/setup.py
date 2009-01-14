#!/usr/bin/env python

from distutils.core import setup, Extension
from distutils import sysconfig
import sys
import commands


config = {
    'jack-midi': True,
    'smf': False,
}

def check_option(name, arg):
    if arg == '--enable-%s' % name:
        sys.argv.remove(arg)
        config[name] = True
    elif arg == '--disable-%s' % name:
        sys.argv.remove(arg)
        config[name] = False

for arg in sys.argv[1:]:
    check_option('jack-midi', arg)
    check_option('smf', arg)


def pkgconfig(pkg):
    status, output = commands.getstatusoutput('pkg-config --libs --cflags %s' % pkg)
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


sources = [
    'src/backend.cc',
    'src/backend_alsa.cc',
    'src/engine.cc',
    'src/patch.cc',
    'src/units.cc',
    'src/python_caller.cc',
    'src/python_module.cc',
]

include_dirs = []
define_macros = []
libraries = []
library_dirs = []


pkgconfig('alsa')
pkgconfig('jack')
include_dirs.append('src')
libraries.append('boost_python-mt')
libraries.append('boost_thread-mt')


if config['jack-midi']:
    define_macros.append(('ENABLE_JACK_MIDI', 1))
    sources.append('src/backend_jack.cc')

if config['smf']:
    define_macros.append(('ENABLE_SMF', 1))
    sources.append('src/backend_smf.cc')
    pkgconfig('smf')


# hack to remove compiler flags from the distutils default.
# -Wstrict-prototypes is not valid for C++
removals = ['-g', '-Wstrict-prototypes']
cv_opt = sysconfig.get_config_var('CFLAGS')
for removal in removals:
    cv_opt = cv_opt.replace(removal, " ")
sysconfig.get_config_vars()['CFLAGS'] = ' '.join(cv_opt.split())


setup(
    name = 'mididings',
    version = '20090114',
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
            libraries = libraries,
            define_macros = define_macros,
        ),
    ],
    packages = [
        'mididings',
        'mididings.units',
        'mididings.extra',
    ],
)
