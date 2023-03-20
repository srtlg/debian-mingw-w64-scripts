from .directory_layout import DirectoryLayout
from .dpkg import *
from .cmake_builder import *
from .qt6_base import VERSION, PKGNAME as BASE_PKGNAME, URL as BASE_URL

NAME = 'qt6-declarative'
DESCRIPTION = 'Classes for QML and JavaScript languages (mingw-w64)'
PKGNAME = pkgname(NAME, dev=True)
URL = BASE_URL.replace('qtbase-', 'qtdeclarative-')


def build():
    if not DPKG.check('qt6-declarative-dev'):
        raise RuntimeError('requiring qt6-declarative-dev')
    if not DPKG.check(BASE_PKGNAME):
        raise RuntimeError(f'requiring {BASE_PKGNAME}')
    if DPKG.installed(PKGNAME):
        print('INSTALLED', PKGNAME)
    cache = DirectoryLayout.download(NAME, URL)
    dpkg = DPKG(PKGNAME, version=VERSION, description=DESCRIPTION,
                depends=[BASE_PKGNAME])
    dirs = Directories(source=cache.src_dir, build=DirectoryLayout.get_build_root() / NAME,
                       installation=dpkg.pkg_root)
    builder = CMakeBuilder(
        name=NAME, dirs=dirs,
    )
    builder.build()
    builder.install()
    dpkg.build_and_install(NAME)
