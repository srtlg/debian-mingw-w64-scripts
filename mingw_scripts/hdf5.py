"""

https://aur.archlinux.org/cgit/aur.git/tree/PKGBUILD?h=mingw-w64-hdf5

"""
from .directory_layout import DirectoryLayout
from .dpkg import *
from .cmake_builder import CMakeBuilder, Directories
from .zlib import PKGNAME as ZLIB
from .wine import PKGNAME as WINE

NAME = 'hdf5'
DESCRIPTION = 'General purpose library and file format for storing scientific data (mingw-w64)'
PKGNAME = pkgname('libhdf5', dev=True)
MAJOR = '1.13'
PATCH = '3'
VERSION = f'{MAJOR}.{PATCH}'
URL = f'https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-{MAJOR}/hdf5-{VERSION}/src/hdf5-{VERSION}.tar.gz'


def build():
    if not DPKG.check(WINE):
        raise RuntimeError(f'requring {WINE} for building')
    if DPKG.installed(PKGNAME):
        print('INSTALLED', PKGNAME)
        return
    cache = DirectoryLayout.download(NAME, URL)
    dpkg = DPKG(PKGNAME, version=VERSION, description=DESCRIPTION,
                depends=[ZLIB])
    b = CMakeBuilder(
        name=NAME,
        dirs=Directories(source=cache.src_dir, build=DirectoryLayout.get_build_root() / NAME,
                         installation=dpkg.pkg_root),
        cmake_kwargs={
            'HDF5_INSTALL_CMAKE_DIR': "lib/cmake",
            'HDF5_BUILD_CPP_LIB:BOOL': 'ON',
            'HDF5_BUILD_EXAMPLES:BOOL': 'OFF',
            'HDF5_BUILD_TOOLS:BOOL': 'OFF',
            'HDF5_ENABLE_THREADSAFE:BOOL': 'OFF',

            'HDF5_ENABLE_Z_LIB_SUPPORT:BOOL': 'ON',
            'ZLIB_LIBRARY:PATH': lib_dir() / 'libzlibstatic.a',
            'ZLIB_INCLUDE_DIR:PATH': include_dir(),
        })
    b.build()
    b.install()
    dpkg.build_and_install(NAME)
