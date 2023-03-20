"""
https://aur.archlinux.org/packages/mingw-w64-zlib-static
"""
import shutil

from . import defaults
from .directory_layout import DirectoryLayout
from .dpkg import *
from .cmake_builder import *
from .cmake_toolchain import PKGNAME as CMAKE_PKGNAME

NAME = 'zlib'
DESCRIPTION = 'A compression/decompression Library (mingw-w64)'
PKGNAME = pkgname(NAME, dev=True)
VERSION = '1.2.13'
URL = f'zlib-{VERSION}.tgz::https://github.com/madler/zlib/archive/v{VERSION}.tar.gz'


def build():
    if DPKG.installed(PKGNAME):
        print('INSTALLED', PKGNAME)
        return
    cache = DirectoryLayout.download(NAME, URL)
    dpkg = DPKG(PKGNAME, version=VERSION, description=DESCRIPTION, depends=[CMAKE_PKGNAME])

    def get_cmake_kwargs(build_type, default):
        if build_type != 'Debug':
            return dict(AMD64='OFF', build_target='zlibstatic')
        else:
            return dict(build_target='zlibstatic')

    dirs = Directories(source=cache.src_dir, build=DirectoryLayout.get_build_root() / NAME,
                       installation=dpkg.pkg_root)
    builder = CMakeBuilder(
        name=NAME,
        dirs=dirs,
        get_cmake_kwargs=get_cmake_kwargs)
    builder.build()
    _install(dirs)
    dpkg.build_and_install(NAME)


def _install(dirs: Directories):
    shutil.copy2(dirs.source / 'zlib.h', include_dir(dirs.installation))
    shutil.copy2(dirs.build / 'zconf.h', include_dir(dirs.installation))
    shutil.copy2(dirs.build / 'libzlibstatic.a', lib_dir(dirs.installation))
    with open(pkgconfig_dir(dirs.installation) / 'zlib.pc', 'w') as fout:
        fout.write(r'''
prefix=/usr
exec_prefix=/usr
libdir=/usr/@PREFIX@/lib
sharedlibdir=/usr/@PREFIX@/lib
includedir=/usr/@PREFIX@/include

Name: zlib
Description: zlib compression library
Version: @VERSION@

Requires:
Libs: -L${libdir} -L${sharedlibdir} -lzlibstatic
Cflags: -I${includedir}
'''.replace('@PREFIX@', defaults.mingw_prefix).replace('@VERSION@', VERSION))
