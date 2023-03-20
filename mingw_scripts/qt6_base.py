"""
https://aur.archlinux.org/packages/mingw-w64-qt6-base-static-nosql
"""
import os

from . import defaults
from .directory_layout import DirectoryLayout
from .dpkg import *
from .cmake_builder import *
from .cmake_toolchain import custom_toolchain_file
from .zlib import PKGNAME as ZLIB_PKGNAME

NAME = 'qt6-base'
DESCRIPTION = 'A cross-platform application and UI framework (mingw-w64)'
PKGNAME = pkgname(NAME, dev=True)
MAJOR = '6.2'
PATCH = '4'
VERSION = f'{MAJOR}.{PATCH}'
URL = f'https://download.qt.io/official_releases/qt/{MAJOR}/{VERSION}/submodules/qtbase-everywhere-src-{VERSION}.tar.xz'

BASE_KWARGS = {
            'QT_HOST_PATH_CMAKE_DIR:PATH': '/usr/lib/x86_64-linux-gnu/cmake',
            'ZLIB_LIBRARY:PATH': lib_dir() / 'libzlibstatic.a',
            'ZLIB_INCLUDE_DIR:PATH': include_dir(),
        }


def add_custom_toolchain(path):
    os.makedirs(path.parent)
    with open(path, 'w') as fout:
        for k, v in BASE_KWARGS.items():
            fout.write(f'set({k.split(":")[0]} "{v}")\n')


def build():
    if not DPKG.check('qt6-tools-dev'):
        raise RuntimeError('requiring qt6-tools-dev')
    if DPKG.installed(PKGNAME):
        print('INSTALLED', PKGNAME)
        return
    cache = DirectoryLayout.download(NAME, URL)
    dpkg = DPKG(PKGNAME, version=VERSION, description=DESCRIPTION,
                depends=[ZLIB_PKGNAME, 'qt6-tools-dev'])
    dirs = Directories(source=cache.src_dir, build=DirectoryLayout.get_build_root() / NAME,
                       installation=dpkg.pkg_root)
    builder = CMakeBuilder(
        name=NAME, dirs=dirs,
        cmake_kwargs={
            'FEATURE_static_runtime': 'ON',
            'FEATURE_pkg_config': 'ON',
            'FEATURE_icu': 'OFF',
            'FEATURE_openssl': 'OFF',
            'FEATURE_glib': 'OFF',
            'FEATURE_dbus': 'OFF',
            'FEATURE_gif': 'OFF',
            'FEATURE_cups': 'OFF',
            'QT_QMAKE_TARGET_MKSPEC': 'win32-g++',

            # 'CMAKE_INTERPROCEDURAL_OPTIMIZATION': 'ON',

            'QT_FEATURE_sql': 'OFF',
            'QT_FEATURE_jpeg': 'OFF',

            'TEST_X86SIMD_rdrnd': 'OFF',
            'TEST_X86SIMD_aesni': 'OFF',
            'TEST_X86SIMD_shani': 'OFF',
            'TEST_X86SIMD_avx': 'OFF',
            'TEST_X86SIMD_avx2': 'OFF',
            'FEATURE_sse4': 'OFF',
            'FEATURE_sse4_1': 'OFF',
            'FEATURE_sse4_2': 'OFF',

            'QT_BUILD_EXAMPLES': 'OFF',
            'QT_BUILD_TESTS': 'OFF',

            'FEATURE_system_zlib': 'ON',

            'FEATURE_cxx20': 'ON',
        }
    )
    builder.cmake_kwargs.update(BASE_KWARGS)
    builder.build()
    builder.install()
    add_custom_toolchain(dpkg(custom_toolchain_file(NAME)))
    dpkg.build_and_install(NAME)
