"""Library to sync data between repository hosts and Isshub."""

from pathlib import PurePath
from pkg_resources import get_distribution, DistributionNotFound
from setuptools.config import read_configuration


def _extract_version() -> str:
    """Return the current version of the package.

    Returns
    -------
    str
        The version as defined in setup.cfg

    """

    try:
        return get_distribution('isshub_sync').version
    except DistributionNotFound:
        conf = read_configuration(PurePath(__file__).parent.parent / 'setup.cfg')
        return conf['metadata']['version']


__version__ = _extract_version()
