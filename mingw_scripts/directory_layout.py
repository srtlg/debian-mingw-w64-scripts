import os
import shutil
from pathlib import Path
from contextlib import closing
from tarfile import TarFile
from urllib.parse import urlparse
from urllib.request import urlopen

from .defaults import FORCE_DOWNLOAD

__all__ = ['DirectoryLayout']


class CachedURL:
    def __init__(self, name, url):
        self.name = name
        self.src_dir = (DirectoryLayout.get_src() / name).absolute()
        self.url, self.archive = self._parse_archive_url(url)
        self.cache_path = (DirectoryLayout.get_cache() / self.archive).absolute()

    @staticmethod
    def _parse_archive_url(url: str):
        pos_dcolon = url.find('::')
        if pos_dcolon == -1:
            components = urlparse(url)
            path = Path(components.path)
            return url, path.name
        else:
            archive = url[:pos_dcolon]
            true_url = url[pos_dcolon+2:]
            return true_url, archive

    def extract(self):
        src_root = DirectoryLayout.get_src()
        os.makedirs(src_root, exist_ok=True)
        old_dirs = set(os.listdir(src_root))
        if self.archive.find('.tar') > 0 or self.archive.endswith('.tgz'):
            arc = TarFile.open(self.cache_path, mode='r:*')
        else:
            raise RuntimeError('cannot determine archive reader for %s' % self.archive)
        arc.extractall(path=src_root)
        arc.close()
        new_dirs = set(os.listdir(src_root))
        diff = new_dirs - old_dirs
        assert len(diff) == 1
        new_dir = diff.pop()
        if new_dir != self.name:
            os.rename(src_root / new_dir, self.src_dir)


class DirectoryLayout:
    root = Path.cwd()

    @classmethod
    def get_cache(cls) -> Path:
        return cls.root / 'cache'

    @classmethod
    def get_src(cls) -> Path:
        return cls.root / 'src'

    @classmethod
    def get_pkg_root(cls) -> Path:
        return cls.root / 'dpkg'

    @classmethod
    def get_build_root(cls) -> Path:
        return cls.root / 'build'

    @classmethod
    def download(cls, name, url) -> CachedURL:
        obj = CachedURL(name, url)
        if obj.src_dir.exists():
            if FORCE_DOWNLOAD:
                shutil.rmtree(obj.src_dir)
            else:
                print('EXISTS', name)
                return obj
        if obj.cache_path.exists():
            if FORCE_DOWNLOAD:
                os.unlink(obj.cache_path)
            else:
                print('EXTRACTING', obj.archive)
                obj.extract()
                return obj
        os.makedirs(obj.cache_path.parent, exist_ok=True)
        print('DOWNLOADING', obj.url, flush=True, end='  \b')
        i = 0
        with closing(urlopen(obj.url)) as fin, open(obj.cache_path, 'wb') as fout:
            print(['/', '-', '\\', '-'][i], flush=True, end='\b')
            shutil.copyfileobj(fin, fout)
            i = (i + 1) % 2
        obj.extract()
        return obj
