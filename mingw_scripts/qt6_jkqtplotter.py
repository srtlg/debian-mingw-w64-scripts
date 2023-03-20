from .directory_layout import DirectoryLayout
from .dpkg import *
from .cmake_builder import *
from .qt6_base import PKGNAME as BASE_PKGNAME
from .qt6_svg import PKGNAME as SVG_PKGNAME

NAME = 'qt6-jkqtplotter'
DESCRIPTION = 'An extensive Qt5 & Qt6 Plotter framework'
PKGNAME = pkgname(NAME, dev=True)
VERSION = '4.0.0'
URL = f'jkqtplotter-{VERSION}.tgz::https://github.com/jkriege2/JKQtPlotter/archive/refs/tags/v{VERSION}.tar.gz'


def build():
    if not DPKG.check(BASE_PKGNAME):
        raise RuntimeError(f'requiring {BASE_PKGNAME}')
    if not DPKG.check(SVG_PKGNAME):
        raise RuntimeError(f'requiring {SVG_PKGNAME}')
    if DPKG.installed(PKGNAME):
        print('INSTALLED', PKGNAME)
        return
    cache = DirectoryLayout.download(NAME, URL)
    dpkg = DPKG(PKGNAME, version=VERSION, description=DESCRIPTION,
                depends=[BASE_PKGNAME, SVG_PKGNAME])
    dirs = Directories(source=cache.src_dir, build=DirectoryLayout.get_build_root() / NAME,
                       installation=dpkg.pkg_root)
    builder = CMakeBuilder(
        name=NAME, dirs=dirs,
        cmake_kwargs={
            'JKQtPlotter_BUILD_SHARED_LIBS': 'OFF',
            'JKQtPlotter_BUILD_STATIC_LIBS': 'ON',
            'JKQtPlotter_BUILD_INCLUDE_XITS_FONTS': 'OFF',
            'JKQtPlotter_BUILD_DECORATE_LIBNAMES_WITH_BUILDTYPE': 'OFF',
            'JKQtPlotter_BUILD_EXAMPLES': 'OFF',
        })
    builder.build()
    builder.install()
    dpkg.build_and_install(NAME)
