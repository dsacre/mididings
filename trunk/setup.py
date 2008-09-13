#!/usr/bin/env python

from distutils.core import setup, Extension
from distutils import sysconfig
import sys


# hack to remove compiler flags from the distutils default.
# -Wstrict-prototypes is not valid for C++
removals = ['-g', '-Wstrict-prototypes']
cv_opt = sysconfig.get_config_var('CFLAGS')
for removal in removals:
    cv_opt = cv_opt.replace(removal, " ")
sysconfig.get_config_vars()['CFLAGS'] = ' '.join(cv_opt.split())


setup(
    name = 'mididings',
    version = '20080913',
    author = 'Dominic Sacre',
    author_email = 'dominic.sacre@gmx.de',
    url = 'http://das.nasophon.de/mididings',
    description = '',
    license = "GPL",
    ext_modules = [
        Extension(
            '_mididings', [
                'src/backend_alsa.cc',
                'src/backend_jack.cc',
                'src/engine.cc',
                'src/patch.cc',
                'src/units.cc',
                'src/python_caller.cc',
                'src/python_module.cc',
            ],
            include_dirs = [
                'src',
            ],
            libraries = [
                'asound',
                'jack',
                'boost_python-mt',
                'boost_thread-mt',
            ]
        ),
    ],
    packages = [
        'mididings',
        'mididings.units',
        'mididings.extra',
    ],
    scripts = [
        'scripts/mididings',
    ],
)
