#!/usr/bin/env python
# -*- coding: utf-8 -*-

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


setup (
    name = 'mididings',
    version = '0.0',
    author = 'Dominic Sacre',
    author_email = 'dominic.sacre@gmx.de',
    url = '',
    description = '',
    license = "GPL",
    ext_modules = [
        Extension('_mididings',
                  [ 'src/backend.cc', 'src/backend_alsa.cc',
                    'src/setup.cc', 'src/patch.cc',
                    'src/python_interface.cc' ],
                  libraries = [ 'asound', 'boost_python' ]
        ),
    ],
)
