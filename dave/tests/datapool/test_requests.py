# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import pytest
from requests import get

from dave.datapool.oep_request import oep_request
from dave.settings import dave_settings


def test_sources_availability():
    """
    Checking the availability of all data sources that DaVe uses via an API
    """
    # check open energy platform
    oep_url = "http://oep.iks.cs.ovgu.de/"
    request_oep = get("http://oep.iks.cs.ovgu.de/")
    assert request_oep.status_code == 200
    # check open energy platform datasets
    for dataset in dave_settings()["oep_tables"].keys():
        request = get(
            "".join(
                [
                    oep_url,
                    "/api/v0/schema/",
                    dave_settings()["oep_tables"][dataset][0],
                    "/tables/",
                    dataset,
                ]
            )
        )
        assert request.status_code == 200
    # check open street map (overpass api)
    request_oep = get("http://www.overpass-api.de/")
    assert request_oep.status_code == 200


def test_oep_request():
    """
    Checking the request function for the open energy platform
    """
    ehvhv_substations, meta_data = oep_request(
        schema=dave_settings()["oep_tables"]["ego_dp_ehv_substation"][0],
        table="ego_dp_ehv_substation",
        where=dave_settings()["oep_tables"]["ego_dp_ehv_substation"][2],
        geometry=dave_settings()["oep_tables"]["ego_dp_ehv_substation"][1],
    )
    # check if data returns
    assert len(ehvhv_substations) != 0
    assert len(meta_data) == 3


def test_osm_request():
    pass


if __name__ == "__main__":
    pytest.main([__file__])
