import os
import shutil
import subprocess
from pathlib import Path
from typing import NamedTuple, Optional

from . import defaults

DEFAULT_CMAKE_KWARGS = {
    'BUILD_TESTING:BOOL': 'OFF',
    'BUILD_SHARED_LIBS:BOOL': 'OFF',
}

__all__ = ['Directories', 'CMakeBuilder']


class Directories(NamedTuple):
    source: Path  # the source directory
    build: Path   # the build directory
    installation: Path  # the installation prefix


def cmake_build(dirs: Directories, nproc=None, **kwargs):
    assert dirs.installation.is_dir()
    assert dirs.source.is_dir()
    kwargs.update(DEFAULT_CMAKE_KWARGS)
    kwargs['CMAKE_BUILD_TYPE'] = defaults.BUILD_TYPE
    if dirs.build.exists() and defaults.FORCE_BUILD:
        shutil.rmtree(dirs.build)
    if not dirs.build.exists():
        os.makedirs(dirs.build)
    cmake = [defaults.CMAKE, '-B', str(dirs.build), '-S', str(dirs.source), '-G', 'Ninja']
    cmake += [f'-D{key}={value}' for key, value in kwargs.items()]
    if not (dirs.build / 'build.ninja').exists() or defaults.FORCE_CONFIGURATION:
        subprocess.check_call(cmake)
    ninja = ['ninja']
    if nproc:
        ninja += ['-j', str(nproc)]
    subprocess.check_call(ninja, cwd=dirs.build)


class CMakeBuilder(object):
    def __init__(self, **kwargs):
        self.name = None
        self.dirs: Optional[Directories] = None
        self.cmake_kwargs = {}
        self.nproc = None
        self.__dict__.update(kwargs)

    def _build(self):
        kwargs = self.get_cmake_kwargs(defaults.BUILD_TYPE, self.cmake_kwargs)
        cmake_build(self.dirs, nproc=self.nproc, **kwargs)

    @staticmethod
    def get_cmake_kwargs(build_type, default):
        return default

    def build(self):
        if defaults.BUILD_ONLY is not None and defaults.BUILD_ONLY != self.name:
            return
        self._build()

    def install(self):
        if defaults.BUILD_ONLY is not None and defaults.BUILD_ONLY != self.name:
            return
        env = os.environ.copy()
        env['DESTDIR'] = self.dirs.installation
        subprocess.check_call(['ninja', 'install'], env=env, cwd=self.dirs.build)
