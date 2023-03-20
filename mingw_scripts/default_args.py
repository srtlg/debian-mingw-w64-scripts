import argparse

from . import defaults

__all__ = ['process_default_args']


def create_default_args():
    p = argparse.ArgumentParser()
    p.add_argument('module', nargs='?', default=None)
    g = p.add_argument_group()
    g.add_argument('-b', '--force-build', action='store_true', default=False)
    g.add_argument('-c', '--force-configuration', action='store_true', default=False)
    g.add_argument('-t', '--build-type', default='RelWithDebInfo', choices=('RelWithDebInfo', 'Debug'))
    return p


def apply_default_args(opts):
    defaults.FORCE_BUILD = opts.force_build
    defaults.FORCE_CONFIGURATION = opts.force_configuration
    defaults.BUILD_ONLY = opts.module
    defaults.BUILD_TYPE = opts.build_type


def process_default_args():
    p = create_default_args()
    opts = p.parse_args()
    apply_default_args(opts)
