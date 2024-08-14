# Copyright (c) 2022-2024 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from dave.settings import dave_settings
from geopandas import GeoDataFrame
from pandas import DataFrame
from requests import get
from shapely.geometry import Point
from shapely.wkb import loads

oep_url = "https://openenergy-platform.org"


def request_to_df(request):
    """
    This function converts requested data into a DataFrame
    """
    if request.status_code == 200:  # 200 is the code of a successful request
        # if request is empty their will be an JSONDecodeError
        try:
            request_data = DataFrame(request.json())
        except:
            request_data = DataFrame()
    else:
        request_data = DataFrame()
    return request_data


def oep_request(
    table, schema=None, where=None, geometry=None, db_update=False
):
    """
    This function is to requesting data from the open energy platform.
    The available data is to find on https://openenergy-platform.org/dataedit/schemas

    INPUT:

        **table** (string) - table name of the searched data

    OPTIONAL:
        **schema** (string, default None) - schema name of the searched data. By default DAVE \
            search for the schema in the settings file via table name
        **where** (string, default None) - filter the table of the searched data
                             example: 'postcode=34225'
        **geometry** (string, default None) - name of the geometry parameter in the OEP dataset
                                to transform it from WKB to WKT
        **db_update** (boolean, default False) - If True in every case the data will be related \
            from the oep

    OUTPUT:
        **requested_data** (DataFrame) - table of the requested data
    """
    if schema is None:
        schema = dave_settings["oep_tables"][table][0]
    # request data directly from oep
    if where:
        request = get(
            "".join(
                [
                    oep_url,
                    "/api/v0/schema/",
                    schema,
                    "/tables/",
                    table,
                    "/rows/?where=",
                    where,
                ]
            )
        )
    elif dave_settings["oep_tables"][table][2] is not None:
        request = get(
            "".join(
                [
                    oep_url,
                    "/api/v0/schema/",
                    schema,
                    "/tables/",
                    table,
                    "/rows/?where=",
                    dave_settings["oep_tables"][table][2],
                ]
            )
        )
    else:
        request = get(
            "".join(
                [
                    oep_url,
                    "/api/v0/schema/",
                    schema,
                    "/tables/",
                    table,
                    "/rows/",
                ]
            )
        )
    # convert data to dataframe
    request_data = request_to_df(request)
    # check for geometry parameter
    if geometry is None:
        geometry = dave_settings["oep_tables"][table][1]
    if geometry is not None:
        # --- convert into geopandas DataFrame with right crs
        # transform WKB to WKT / Geometry
        request_data["geometry"] = request_data[geometry].apply(
            lambda x: loads(x, hex=True)
        )
        # create geoDataFrame
        request_data = GeoDataFrame(
            request_data,
            crs=dave_settings["crs_main"],
            geometry=request_data.geometry,
        )
    # fix some mistakes in the oep data
    if table == "ego_pf_hv_transformer":
        # change geometry to point because in original data the geometry was lines with length 0
        request_data["geometry"] = request_data.geometry.apply(
            lambda x: Point(
                x.geoms[0].coords[:][0][0], x.geoms[0].coords[:][0][1]
            )
        )
    if table == "ego_dp_mvlv_substation":
        # change wrong crs from oep
        request_data.crs = dave_settings["crs_meter"]
        request_data = request_data.to_crs(dave_settings["crs_main"])

    # --- request meta informations for a dataset
    # !!! Todo: seperate option for getting data from DB. When there are no meta data in DB then check OEP Url
    request = get(
        "".join(
            [oep_url, "/api/v0/schema/", schema, "/tables/", table, "/meta/"]
        )
    )
    # convert data to meta dict  # !!! When getting data from database the meta informations should also came from db
    if request.status_code == 200:  # 200 is the code of a successful request
        request_meta = request.json()
        # create dict
        meta_data = {
            "Main": DataFrame(
                {
                    "Titel": request_meta["title"],
                    "Description": request_meta["description"],
                    "Spatial": [request_meta["spatial"]],
                    "Licenses": request_meta["licenses"],
                    "metadata_version": request_meta["metaMetadata"][
                        "metadataVersion"
                    ],
                },
                index=[0],
            ),
            "Sources": DataFrame(request_meta["sources"]),
            "Data": DataFrame(
                request_meta["resources"][0]["schema"]["fields"]
            ),
        }
    else:
        meta_data = {}
    return request_data, meta_data
