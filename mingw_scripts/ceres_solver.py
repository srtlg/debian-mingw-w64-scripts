"""
https://aur.archlinux.org/packages/mingw-w64-ceres-solver
"""
from multiprocessing import cpu_count
from .directory_layout import DirectoryLayout
from .dpkg import *
from .cmake_builder import CMakeBuilder, Directories
from .eigen import PKGNAME as EIGEN
from .google_glog import PKGNAME as GLOG

NAME = 'ceres-solver'
DESCRIPTION = 'Solver for nonlinear least squares problems (mingw-w64)'
PKGNAME = pkgname('libceres', dev=True)
VERSION = '2.1.0'
URL = f'http://ceres-solver.org/ceres-solver-{VERSION}.tar.gz'


def _build(glog: bool):
    if not DPKG.check(EIGEN):
        raise RuntimeError(f'requiring {EIGEN}')
    if DPKG.installed(PKGNAME):
        print('INSTALLED', PKGNAME)
        return
    cache = DirectoryLayout.download(NAME, URL)
    depends = [EIGEN]
    if glog:
        depends += [GLOG]
    dpkg = DPKG(PKGNAME, version=VERSION, description=DESCRIPTION,
                depends=depends)
    builder = CMakeBuilder(
        name=NAME,
        dirs=Directories(source=cache.src_dir, build=DirectoryLayout.get_build_root() / NAME,
                         installation=dpkg.pkg_root),
        nproc=cpu_count() // 2,  # 24 cores eats 36GB memory
        cmake_kwargs={
            'BUILD_EXAMPLES:BOOL': 'OFF',
            'BUILD_BENCHMARKS:BOOL': 'OFF',
            'CERES_THREADING_MODEL': 'OPENMP',
            #'CERES_THREADING_MODEL': 'NO_THREADS',
        })
    if glog:
        builder.cmake_kwargs.update({
            'GFLAGS:BOOL': 'ON',
            'MINIGLOG:BOOL': 'OFF'})
    else:
        builder.cmake_kwargs.update({
            'GFLAGS:BOOL': 'OFF',
            'MINIGLOG:BOOL': 'ON'})
    builder.build()
    builder.install()
    dpkg.build_and_install(NAME)


def build_with_glog():
    _build(True)


def build_with_miniglog():
    _build(False)
