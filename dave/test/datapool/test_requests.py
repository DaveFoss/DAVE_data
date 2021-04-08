import pytest
import requests


def test_sources_availability():
    """
    Checking the availability of all data sources that DaVe uses via an API
    """
    # check open energy platform
    request_oep = requests.get('http://oep.iks.cs.ovgu.de/')
    assert request_oep.status_code == 200
    # check open street map (overpass api)
    request_oep = requests.get('http://www.overpass-api.de/')
    assert request_oep.status_code == 200


def test_oep_request():
    pass


def test_osm_request():
    pass


if __name__ == '__main__':
    pytest.main([__file__])
