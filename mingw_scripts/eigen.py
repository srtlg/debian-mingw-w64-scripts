"""
https://github.com/mxe/mxe/blob/master/src/eigen.mk
"""
from .directory_layout import DirectoryLayout
from .dpkg import *
from .cmake_builder import CMakeBuilder, Directories

NAME = 'eigen'
DESCRIPTION = 'A C++ template library for linear algebra (mingw-w64)'
PKGNAME = pkgname('libeigen', dev=True)
VERSION = '3.4.0'
URL = f'https://gitlab.com/libeigen/eigen/-/archive/{VERSION}/eigen-{VERSION}.tar.bz2'


def build():
    gfortran = pkgname('gfortran')
    if not DPKG.check(gfortran):
        raise RuntimeError(f'requiring {gfortran}')
    if DPKG.installed(PKGNAME):
        print('INSTALLED', PKGNAME)
        return
    cache = DirectoryLayout.download(NAME, URL)
    dpkg = DPKG(PKGNAME, version=VERSION, description=DESCRIPTION)

    builder = CMakeBuilder(
        name=NAME,
        dirs=Directories(source=cache.src_dir, build=DirectoryLayout.get_build_root() / NAME,
                         installation=dpkg.pkg_root),
        cmake_kwargs={
            'EIGEN_BUILD_PKGCONFIG:BOOL': 'ON',
            'EIGEN_BUILD_DOC': 'OFF',
        })
    builder.build()
    builder.install()
    dpkg.build_and_install(NAME)
