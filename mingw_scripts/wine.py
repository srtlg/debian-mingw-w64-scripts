"""
https://aur.archlinux.org/packages/mingw-w64-wine
"""
import os
from pathlib import Path

from . import defaults
from .dpkg import *

def write_env(path: Path):
    os.makedirs(path.parent, exist_ok=True)
    with open(path, 'w') as fout:
        fout.write(r'''#!/bin/sh

_arch=$1

# -D_FORTIFY_SOURCE=2 and snprintf dection in google-glog fails 
default_mingw_pp_flags="-D_GLIBCXX_ASSERTIONS"
default_mingw_compiler_flags="$default_mingw_pp_flags -O2 -pipe -fno-plt -fexceptions --param=ssp-buffer-size=4 -Wformat -Werror=format-security -fcf-protection"
default_mingw_linker_flags="-Wl,-O1,--sort-common,--as-needed -fstack-protector"

export CPPFLAGS="${MINGW_CPPFLAGS:-$default_mingw_pp_flags $CPPFLAGS}"
export CFLAGS="${MINGW_CFLAGS:-$default_mingw_compiler_flags $CFLAGS}"
export CXXFLAGS="${MINGW_CXXFLAGS:-$default_mingw_compiler_flags $CXXFLAGS}"
export LDFLAGS="${MINGW_LDFLAGS:-$default_mingw_linker_flags $LDFLAGS}"

export CC="${MINGW_CC:-$_arch-gcc}"
export CXX="${MINGW_CXX:-$_arch-g++}"

mingw_prefix=/usr/${_arch}
export PKG_CONFIG_SYSROOT_DIR="${mingw_prefix}"
export PKG_CONFIG_LIBDIR="${mingw_prefix}/lib/pkgconfig:${mingw_prefix}/share/pkgconfig"

''')
    path.chmod(0o555)


def write_wine(path: Path):
    os.makedirs(path.parent, exist_ok=True)
    with open(path, 'w') as fout:
        fout.write(r'''#!/bin/sh
set -e

mingw_prefix=/usr/@TRIPLE@

# run it in a custom WINEPREFIX to not mess with default ~/.wine
# also default prefix might be a 32 bits prefix, which will fail to run x86_64 exes
export WINEPREFIX=${HOME}/.wine-@TRIPLE@

# WINEPATH is used to find dlls, otherwise they should lie next to the exe
if test -z ${WINEPATH+x}
then
  export WINEPATH=${mingw_prefix}/bin
fi

if test "@TRIPLE@" = "x86_64-w64-mingw32"
then
  export WINEARCH=win64
else
  export WINEARCH=win32
fi

if test -z ${WINEDLLOVERRIDES+x}
then
  export WINEDLLOVERRIDES="mscoree,mshtml="
fi

if test -z ${WINEDEBUG+x}
then
  export WINEDEBUG=-all
fi

exec /usr/bin/@WINE@-stable "$@"
'''.replace('@TRIPLE@', defaults.mingw_prefix).replace('@WINE@', WINE))
    path.chmod(0o555)


NAME = 'wine'
PKGNAME = pkgname(NAME)
DESCRIPTION = 'Wine wrapper for MinGW (mingw-w64 toolchain)'
if defaults.machine == 'x86_64':
    WINE = 'wine64'
elif defaults.machine == 'i686':
    WINE = 'wine32'


def build():
    if DPKG.installed(PKGNAME):
        print('INSTALLED', PKGNAME)
        return
    dpkg = DPKG(PKGNAME, version='1', description=DESCRIPTION, depends=[WINE])
    write_wine(dpkg(f'usr/bin/{defaults.mingw_prefix}-wine'))
    dpkg.build_and_install(NAME)
