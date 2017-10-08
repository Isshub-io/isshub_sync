import configparser
from pkg_resources import get_distribution, DistributionNotFound
from pathlib import PurePath

from isshub_sync import _extract_version


def test_extract_version_from_distribution(mocker):
    pytest_distrib = get_distribution('pytest')
    mocker.patch('isshub_sync.get_distribution', return_value=pytest_distrib)
    assert _extract_version() == pytest_distrib.version


def test_extract_version_from_setupcfg(mocker):
    config = configparser.ConfigParser()
    config.read(PurePath(__file__).parent.parent / 'setup.cfg')
    assert config['metadata']['version']

    def get_distribution(dist):
        """Emulate a call to get a distribution that does not exist"""
        raise DistributionNotFound

    mocker.patch('isshub_sync.get_distribution', side_effect=get_distribution)
    assert _extract_version() == config['metadata']['version']
