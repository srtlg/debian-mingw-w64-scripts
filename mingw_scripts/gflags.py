"""
https://aur.archlinux.org/packages/mingw-w64-gflags
"""
from .directory_layout import DirectoryLayout
from .dpkg import *
from .cmake_builder import CMakeBuilder, Directories

NAME = 'gflags'
DESCRIPTION = 'C++ Library for commandline flag processing (mingw-w64)'
PKGNAME = pkgname('libgflags', dev=True)
VERSION = '2.2.2'
URL = f'gflags-{VERSION}.tgz::https://github.com/schuhschuh/gflags/archive/v{VERSION}.tar.gz'


def build():
    if DPKG.installed(PKGNAME):
        print('INSTALLED', PKGNAME)
        return
    cache = DirectoryLayout.download(NAME, URL)
    dpkg = DPKG(PKGNAME, version=VERSION, description=DESCRIPTION)

    builder = CMakeBuilder(
        name=NAME,
        dirs=Directories(source=cache.src_dir, build=DirectoryLayout.get_build_root() / NAME,
                         installation=dpkg.pkg_root))
    builder.build()
    builder.install()
    dpkg.build_and_install(NAME)
