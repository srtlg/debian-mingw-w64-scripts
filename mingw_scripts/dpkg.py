"""
create a simple binary package

https://www.internalpointers.com/post/build-binary-deb-package-practical-guide

"""
import os
import socket
import shutil
import subprocess
from typing import Union
from pathlib import Path

from . import defaults
from .directory_layout import DirectoryLayout


__all__ = ['DPKG', 'pkgname', 'include_dir', 'lib_dir', 'pkgconfig_dir']


def get_dpkg_architecture():
    link = Path(f'/usr/bin/{defaults.mingw_prefix}-gcc')
    assert link.exists()
    target = link.resolve()
    assert target.exists()
    pkg = subprocess.check_output(['dpkg', '-S', target]).decode('utf-8').split(':')[0]
    if pkg.startswith('gcc-'):
        return pkg[len('gcc-'):]
    else:
        raise RuntimeError('unknown pkgname %s' % pkg)


_architecture = get_dpkg_architecture()


def pkgname(name, dev=False):
    assert name.find('_') == -1
    if dev:
        return f"{name}-{_architecture}-dev"
    else:
        return f"{name}-{_architecture}"


def lib_dir(root=Path('/')):
    path = root / f'usr/{defaults.mingw_prefix}/include'
    if not path.exists():
        os.makedirs(path)
    return path


def include_dir(root=Path('/')):
    path = root / f'usr/{defaults.mingw_prefix}/lib'
    if not path.exists():
        os.makedirs(path)
    return path


def pkgconfig_dir(root=Path('/')):
    path = root / f'usr/{defaults.mingw_prefix}/lib/pkgconfig'
    if not path.exists():
        os.makedirs(path)
    return path


class DPKG:
    def __init__(self, name, version='1.0', release='1', description='TBD', architecture='all', maintainer=None,
                 multi_arch='foreign', depends=tuple()):
        self.name = name
        self.version = version
        self.release = release
        self.description = description
        self.architecture = architecture
        self.multi_arch = multi_arch
        self.depends = depends
        if maintainer is None:
            login_name = os.getlogin()
            fqdn = socket.getfqdn()
            self.maintainer = f"{login_name} <{login_name.replace(' ', '_')}@{fqdn}>"
        else:
            self.maintainer = maintainer
        self.pkg_root = DirectoryLayout.get_pkg_root() / f'{name}_{version}-{release}_{architecture}'
        if self.pkg_root.exists():
            shutil.rmtree(self.pkg_root)
        os.makedirs(self.pkg_root)
        debian_bin = self.pkg_root / 'DEBIAN'
        os.mkdir(debian_bin)
        self.pkg_control = debian_bin / 'control'
        self._write_bin_control()

    def _write_bin_control(self):
        with open(self.pkg_control, 'w') as fout:
            print('Package:', self.name, file=fout)
            print('Version:', self.version, file=fout)
            print('Architecture:', self.architecture, file=fout)
            print('Maintainer:', self.maintainer, file=fout)
            print('Description:', self.description, file=fout)
            print('Priority: optional', file=fout)
            if len(self.depends):
                print('Depends:', ', '.join(self.depends), file=fout)

    def _build(self):
        subprocess.check_call(['dpkg-deb', '--build', '--root-owner-group', self.pkg_root.name],
                              cwd=DirectoryLayout.get_pkg_root())

    def _install(self):
        with open(DirectoryLayout.root / 'install.log', 'a') as fout:
            print(self.name, file=fout)
        subprocess.check_call(['sudo', 'dpkg', '-i', f'{self.pkg_root.name}.deb'],
                              cwd=DirectoryLayout.get_pkg_root())

    def build_and_install(self, name):
        if defaults.BUILD_ONLY is not None and defaults.BUILD_ONLY != name:
            return
        self._build()
        self._install()

    def __call__(self, path: Union[str, Path]) -> Path:
        return self.pkg_root / path

    @classmethod
    def check(cls, package):
        rv = subprocess.run(['dpkg', '-s', package], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            check=False).stdout.decode('utf-8')
        for line in rv.splitlines():
            if line.startswith('Status: '):
                return line.find('not-installed') == -1
        return False

    @classmethod
    def installed(cls, package):
        return cls.check(package) and not (defaults.FORCE_BUILD or defaults.FORCE_CONFIGURATION)
