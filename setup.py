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
    version = '20080713',
    author = 'Dominic Sacre',
    author_email = 'dominic.sacre@gmx.de',
    url = '',
    description = '',
    license = "GPL",
    ext_modules = [
        Extension('_mididings',
                  [ 'src/backend_alsa.cc',
                    'src/setup.cc', 'src/patch.cc', 'src/units.cc',
                    'src/python.cc' ],
                  include_dirs = ['src'],
                  libraries = ['asound', 'boost_python']
        ),
    ],
    packages = ['mididings'],
)
