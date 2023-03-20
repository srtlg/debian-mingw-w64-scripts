"""
https://aur.archlinux.org/packages/mingw-w64-google-glog
"""
from .directory_layout import DirectoryLayout
from .dpkg import *
from .cmake_builder import CMakeBuilder, Directories
from .gflags import PKGNAME as GFLAGS

NAME = 'google-glog'
DESCRIPTION = 'Logging library for C++ (mingw-w64)'
PKGNAME = pkgname('libgoogle-glog', dev=True)
VERSION = '0.6.0'
URL = f'google-glog-{VERSION}.tgz::https://github.com/google/glog/archive/refs/tags/v{VERSION}.tar.gz'


def build():
    if DPKG.installed(PKGNAME):
        print('INSTALLED', PKGNAME)
        return
    cache = DirectoryLayout.download(NAME, URL)
    dpkg = DPKG(PKGNAME, version=VERSION, description=DESCRIPTION,
                depends=[GFLAGS])

    builder = CMakeBuilder(
        name=NAME,
        dirs=Directories(source=cache.src_dir, build=DirectoryLayout.get_build_root() / NAME,
                         installation=dpkg.pkg_root))
    builder.build()
    builder.install()
    dpkg.build_and_install(NAME)
