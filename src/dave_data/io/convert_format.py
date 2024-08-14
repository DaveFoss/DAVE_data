# Copyright (c) 2022-2024 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from copy import deepcopy

from geopandas import GeoDataFrame, GeoSeries
from pandas import DataFrame, Series
from shapely.wkb import dumps, loads

from dave_data.dave_structure import davestructure


def wkb_to_wkt(data_df, crs):
    """
    This function converts geometry data from WKB (hexadecimal string) to WKT (geometric object)
    format for a given dataframe and convert it to a geodataframe

    INPUT:
        **data_df** (DataFrame) - Data with geometry data which is in hexadecimal string format
        **crs** (str) - Koordinatereference system for the data

    Output:
        **data_df** (DataFrame) - Data with geometry as shapely objects
    """
    if (not data_df.empty) and ("geometry" in data_df.keys()):
        data_df["geometry"] = data_df.geometry.apply(loads)
    data_df = GeoDataFrame(data_df, crs=crs)
    return data_df


def wkt_to_wkb(data_df):
    """
    This function converts a geometry data from WKT (geometric object) to WKB (hexadecimal string)
    format for a given geodataframe

    INPUT:
        **data_df** (DataFrame) - Data with geometry data as shapely objects

    Output:
        **data_df** (DataFrame) - Data with geometry which is in hexadecimal string format
    """
    data = data_df.copy(deep=True)
    if not data.empty:
        data = DataFrame(data)
        if "geometry" in data.keys():
            data["geometry"] = data.geometry.apply(dumps)
    else:
        data = DataFrame([])
    return data


def wkt_to_wkb_dataset(grid_data):
    """
    This function converts all geometry data from WKT (geometric object) to WKB (hexadecimal string)
    format for a given DaVe dataset

    INPUT:
        **grid_data** (attr Dict) - DAVE Dataset with Data that contains geometry data as shapely \
            objects
    Output:
        **dataset** (attr Dict) - DAVE Dataset with Data that contains geometry in hexadecimal \
            string format
    """
    dataset = deepcopy(grid_data)
    for key in dataset.keys():
        if isinstance(dataset[key], davestructure):
            for key_sec in dataset[key].keys():
                if isinstance(dataset[key][key_sec], davestructure):
                    for key_trd in dataset[key][key_sec].keys():
                        if isinstance(dataset[key][key_sec][key_trd], GeoDataFrame):
                            dataset[key][key_sec][key_trd] = wkt_to_wkb(
                                dataset[key][key_sec][key_trd]
                            )
                elif isinstance(dataset[key][key_sec], GeoDataFrame):
                    dataset[key][key_sec] = wkt_to_wkb(grid_data[key][key_sec])
        elif isinstance(dataset[key], GeoDataFrame):
            dataset[key] = wkt_to_wkb(grid_data[key])
    return dataset


def change_empty_gpd(grid_data):
    """
    This function replaces all empty geopandas objects with empty pandas objects in a DAVE dataset

    INPUT:
        **grid_data** (attr Dict) - DAVE Dataset with empty geopandas objects

    Output:
        **dataset** (attr Dict) - DAVE Dataset with empty pandas objects
    """
    dataset = deepcopy(grid_data)
    for key in dataset.keys():
        if isinstance(dataset[key], davestructure):
            for key_sec in dataset[key].keys():
                if isinstance(dataset[key][key_sec], davestructure):
                    for key_trd in dataset[key][key_sec].keys():
                        if isinstance(dataset[key][key_sec][key_trd], GeoDataFrame):
                            if dataset[key][key_sec][key_trd].empty:
                                dataset[key][key_sec][key_trd] = DataFrame([])
                        elif isinstance(dataset[key][key_sec][key_trd], GeoSeries):
                            if dataset[key][key_sec][key_trd].empty:
                                dataset[key][key_sec][key_trd] = Series([], dtype="object")
                elif isinstance(dataset[key][key_sec], GeoDataFrame):
                    if dataset[key][key_sec].empty:
                        dataset[key][key_sec] = DataFrame([])
                elif isinstance(dataset[key][key_sec], GeoSeries):
                    if dataset[key][key_sec].empty:
                        dataset[key][key_sec] = Series([], dtype="object")
        elif isinstance(dataset[key], GeoDataFrame):
            if dataset[key].empty:
                dataset[key] = DataFrame([])
        elif isinstance(dataset[key], GeoSeries):
            if dataset[key].empty:
                dataset[key] = Series([], dtype="object")
    return dataset
