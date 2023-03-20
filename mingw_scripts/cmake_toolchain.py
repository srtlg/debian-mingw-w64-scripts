"""
https://aur.archlinux.org/packages/mingw-w64-cmake
"""
import os
from pathlib import Path

from . import defaults
from .dpkg import *

__all__ = ['custom_toolchain_file']


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


def write_cmake(path: Path):
    os.makedirs(path.parent, exist_ok=True)
    with open(path, 'w') as fout:
        fout.write(r'''#!/bin/sh
. /usr/bin/@PREFIX@-env @PREFIX@
mingw_prefix=/usr/@PREFIX@
export PATH=${mingw_prefix}/bin:$PATH
exec cmake \
    -DCMAKE_INSTALL_PREFIX:PATH=${mingw_prefix} \
    -DCMAKE_INSTALL_LIBDIR:PATH=lib \
    -DCMAKE_CXX_IMPLICIT_INCLUDE_DIRECTORIES:PATH=${mingw_prefix}/include \
    -DCMAKE_C_IMPLICIT_INCLUDE_DIRECTORIES:PATH=${mingw_prefix}/include \
    -DBUILD_SHARED_LIBS:BOOL=OFF \
    -DCMAKE_TOOLCHAIN_FILE=/usr/share/mingw-w64/toolchain-@PREFIX@.cmake \
    -DCMAKE_CROSSCOMPILING_EMULATOR=/usr/bin/@PREFIX@-wine \
    "$@"
'''.replace('@PREFIX@', defaults.mingw_prefix))
    path.chmod(0o555)


def write_toolchain(path: Path):
    os.makedirs(path.parent, exist_ok=True)
    with open(path, 'w') as fout:
        fout.write(r'''
set (CMAKE_SYSTEM_NAME Windows)
set (CMAKE_SYSTEM_PROCESSOR @MACHINE@)

# specify the cross compiler
set (CMAKE_C_COMPILER @PREFIX@-gcc)
set (CMAKE_CXX_COMPILER @PREFIX@-g++)

# where is the target environment
set (CMAKE_FIND_ROOT_PATH /usr/@PREFIX@)

# search for programs in the build host directories
set (CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
# for libraries and headers in the target directories
set (CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set (CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set (CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

# Make sure Qt can be detected by CMake (needed for cross-compiling)
set (QT_BINARY_DIR "/usr/@PREFIX@/bin" "/usr/bin")
set (QT_INCLUDE_DIRS_NO_SYSTEM ON)
set (QT_HOST_PATH "/usr")

# set the resource compiler (RHBZ #652435)
set (CMAKE_RC_COMPILER @PREFIX@-windres)
set (CMAKE_MC_COMPILER @PREFIX@-windmc)

# override boost thread component suffix as mingw-w64-boost is compiled with threadapi=win32
# set (Boost_THREADAPI win32)

# These are needed for compiling lapack (RHBZ #753906)
set (CMAKE_Fortran_COMPILER @PREFIX@-gfortran)
set (CMAKE_AR:FILEPATH @PREFIX@-ar)
set (CMAKE_RANLIB:FILEPATH @PREFIX@-ranlib)

file(GLOB toolchain_files "/usr/share/mingw-w64/toolchain-@PREFIX@.d/*.cmake")
foreach(toolchain_file ${toolchain_files})
    include(${toolchain_file})
endforeach()
'''.replace('@MACHINE@', defaults.machine).replace('@PREFIX@', defaults.mingw_prefix))
    path.chmod(0o444)

NAME = 'cmake'
PKGNAME = pkgname(NAME)
DESCRIPTION = 'A cross-platform open-source make system (mingw-w64 toolchain)'


def custom_toolchain_directory():
    return Path(f'usr/share/mingw-w64/toolchain-{defaults.mingw_prefix}.d')


def custom_toolchain_file(name):
    return custom_toolchain_directory() / f'{name}.cmake'


def build():
    if DPKG.installed(PKGNAME):
        print('INSTALLED', PKGNAME)
        return
    dpkg = DPKG(PKGNAME, version='1', description=DESCRIPTION, depends=['cmake'])
    write_env(dpkg(f'usr/bin/{defaults.mingw_prefix}-env'))
    write_cmake(dpkg(f'usr/bin/{defaults.mingw_prefix}-cmake'))
    write_toolchain(dpkg(f'usr/share/mingw-w64/toolchain-{defaults.mingw_prefix}.cmake'))
    os.mkdir(dpkg(custom_toolchain_directory()))
    dpkg.build_and_install(NAME)
