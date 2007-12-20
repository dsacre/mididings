# -*- python -*-

import os, sys
from distutils import sysconfig
import glob

env = Environment(
    CCFLAGS = [ '-O2', '-Wall' ],
#    CCFLAGS = [ '-g', '-Wall' ],
    CPPDEFINES = [ #'ENABLE_DEBUG',
#                   'ENABLE_DEBUG_FN',
                   'ENABLE_DEBUG_PRINT',
#                   'ENABLE_TEST',
    ],
    ENV = os.environ,
    LIBS = [ 'boost_python' ],

)

# hack to remove compiler flags from the distutils default.
# -Wstrict-prototypes is not valid for C++
cv_opt = sysconfig.get_config_var('CFLAGS')
cflags = [ x for x in cv_opt.split() if x not in ['-g', '-O2', '-Wstrict-prototypes', '-DNDEBUG'] ]
env.Append(CCFLAGS = cflags)

env.Append(CPPPATH = [sysconfig.get_python_inc(plat_specific=1)],
           LIBPATH = [sysconfig.get_python_lib(plat_specific=1)])

env.ParseConfig(
    'pkg-config --cflags --libs alsa'
)

#env.SharedLibrary('src/_mididings',
#    [ 'src/backend_alsa.cc',
#      'src/setup.cc', 'src/patch.cc', 'src/units.cc',
#      'src/python_interface.cc' ],
#    SHLIBPREFIX='', SHOBJSUFFIX='.o')

env.SharedObject('src/python_interface.o', 'src/python_interface.cc')
env.Ignore('src/python_interface.o', glob.glob('src/*.h'))

env.SharedLibrary('src/_mididings',
    [ 'src/backend_alsa.cc',
      'src/setup.cc', 'src/patch.cc', 'src/units.cc',
      'src/python_interface.o' ],
    SHLIBPREFIX='', SHOBJSUFFIX='.o')
