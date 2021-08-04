import copy
import pandas as pd
import geopandas as gpd
from shapely.wkb import loads, dumps


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


def wkt_to_wkb(data_key):
    """
    This function converts a geometry data from WKT (geometric object) to WKB (hexadecimal string)
    format for a given dataframe stored in a hdf5 file
    """
    data = copy.deepcopy(data_key)
    if not data.empty:
        data = pd.DataFrame(data)
        if 'geometry' in data.keys():
            data['geometry'] = data.geometry.apply(dumps)
    else:
        data = pd.DataFrame([])
    return data
