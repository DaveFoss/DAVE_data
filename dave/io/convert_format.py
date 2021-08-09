import pandas as pd
import geopandas as gpd
import copy
from shapely.wkb import loads, dumps

from dave.dave_structure import davestructure


def wkb_to_wkt(file, key):
    """
    This function converts geometry data from WKB (hexadecimal string) to WKT (geometric object)
    format for a given dataframe stored in a hdf5 file
    """
    data = file.get(key)
    if (not data.empty) and ('geometry' in data.keys()):
        data['geometry'] = data.geometry.apply(loads)
    data = gpd.GeoDataFrame(data)
    return data


def wkt_to_wkb(data_df):
    """
    This function converts a geometry data from WKT (geometric object) to WKB (hexadecimal string)
    format for a given geodataframe
    """
    data = data_df.copy(deep=True)
    if not data.empty:
        data = pd.DataFrame(data)
        if 'geometry' in data.keys():
            data['geometry'] = data.geometry.apply(dumps)
    else:
        data = pd.DataFrame([])
    return data


def wkt_to_wkb_dataset(grid_data):
    """
    This function converts all geometry data from WKT (geometric object) to WKB (hexadecimal string)
    format for a given DaVe dataset
    """
    for key in grid_data.keys():
        if isinstance(grid_data[key], davestructure):
            for key_sec in grid_data[key].keys():
                if isinstance(grid_data[key][key_sec], davestructure):
                    for key_trd in grid_data[key][key_sec].keys():
                        if isinstance(grid_data[key][key_sec][key_trd], gpd.GeoDataFrame):
                            grid_data[key][key_sec][key_trd] = wkt_to_wkb(
                                grid_data[key][key_sec][key_trd])
                elif isinstance(grid_data[key][key_sec], gpd.GeoDataFrame):
                    grid_data[key][key_sec] = wkt_to_wkb(grid_data[key][key_sec])
        elif isinstance(grid_data[key], gpd.GeoDataFrame):
            grid_data[key] = wkt_to_wkb(grid_data[key])
    return grid_data
