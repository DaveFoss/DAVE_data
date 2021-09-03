import pytest
import requests
from pandas import DataFrame

from dave.datapool import oep_request
from dave.settings import dave_settings


def test_sources_availability():
    """
    Checking the availability of all data sources that DaVe uses via an API
    """
    # check open energy platform
    oep_url = "http://oep.iks.cs.ovgu.de/"
    request_oep = requests.get("http://oep.iks.cs.ovgu.de/")
    assert request_oep.status_code == 200
    # check open energy platform datasets
    datasets = DataFrame(
        {
            "schema": ["supply", "supply", "grid", "grid", "grid", "grid", "grid", "grid"],
            "table": [
                "ego_renewable_powerplant",
                "ego_conventional_powerplant",
                "ego_pf_hv_transformer",
                "ego_pf_hv_bus",
                "ego_dp_hvmv_substation",
                "ego_dp_mvlv_substation",
                "ego_dp_ehv_substation",
                "ego_pf_hv_line",
            ],
        }
    )
    for i, dataset in datasets.iterrows():
        request = requests.get(
            "".join([oep_url, "/api/v0/schema/", dataset.schema, "/tables/", dataset.table])
        )
        assert request.status_code == 200
    # check open street map (overpass api)
    request_oep = requests.get("http://www.overpass-api.de/")
    assert request_oep.status_code == 200


def test_oep_request():
    """
    Checking the request function for the open energy platform
    """
    ehvhv_substations, meta_data = oep_request(
        schema="grid",
        table="ego_dp_ehv_substation",
        where=dave_settings()["ehv_sub_ver"],
        geometry="polygon",
    )
    # check if data returns
    assert len(ehvhv_substations) != 0
    assert len(meta_data) == 3


def test_osm_request():
    pass


if __name__ == "__main__":
    pytest.main([__file__])
