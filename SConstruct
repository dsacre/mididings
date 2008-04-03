# -*- python -*-

import os, sys
from distutils import sysconfig
import glob

env = Environment(
    CCFLAGS = [ '-O2', '-W', '-Wall' ],
#    CCFLAGS = [ '-g', '-W', '-Wall' ],
    CPPDEFINES = [
        'ENABLE_DEBUG',
#        'ENABLE_DEBUG_FN',
#        'ENABLE_DEBUG_PRINT',
        'ENABLE_TEST',
    ],
    CPPPATH = ['.'],
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
#      'src/python.cc' ],
#    SHLIBPREFIX='', SHOBJSUFFIX='.o')

env.SharedObject('src/python.o', 'src/python.cc', CCFLAGS = [f for f in env['CCFLAGS'] if f != '-W'])
#env.Ignore('src/python.o', glob.glob('src/*.h'))

env.SharedLibrary('src/_mididings',
    [ 'src/backend_alsa.cc',
      'src/setup.cc', 'src/patch.cc', 'src/units.cc',
      'src/python.o' ],
    SHLIBPREFIX='', SHOBJSUFFIX='.o')
