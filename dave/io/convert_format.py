import copy
import pandas as pd
import geopandas as gpd
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


def wkb_to_wkt_dataset(grid_data):
    pass
    # hier noch funktion schreiben welche die geometrien zurück in objekte konvertiert
    # dazu auch die normale wkb_to_wkt function verallgemeinern und die from hdf function anpassen


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
    dataset = copy.deepcopy(grid_data)
    for key in dataset.keys():
        if isinstance(dataset[key], davestructure):
            for key_sec in dataset[key].keys():
                if isinstance(dataset[key][key_sec], davestructure):
                    for key_trd in dataset[key][key_sec].keys():
                        if isinstance(dataset[key][key_sec][key_trd], gpd.GeoDataFrame):
                            dataset[key][key_sec][key_trd] = wkt_to_wkb(
                                dataset[key][key_sec][key_trd])
                elif isinstance(dataset[key][key_sec], gpd.GeoDataFrame):
                    dataset[key][key_sec] = wkt_to_wkb(grid_data[key][key_sec])
        elif isinstance(dataset[key], gpd.GeoDataFrame):
            dataset[key] = wkt_to_wkb(grid_data[key])
    return dataset
