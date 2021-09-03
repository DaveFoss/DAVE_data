from copy import deepcopy
import pandas as pd
import geopandas as gpd
from shapely.wkb import loads, dumps


from dave.dave_structure import davestructure


def wkb_to_wkt(data_df, crs):
    """
    This function converts geometry data from WKB (hexadecimal string) to WKT (geometric object)
    format for a given dataframe and convert it to a geodataframe

    Input pandas dataframe
    Output geodataframe
    """
    if (not data_df.empty) and ("geometry" in data_df.keys()):
        data_df["geometry"] = data_df.geometry.apply(loads)
    data_df = gpd.GeoDataFrame(data_df, crs=crs)
    return data_df


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
        if "geometry" in data.keys():
            data["geometry"] = data.geometry.apply(dumps)
    else:
        data = pd.DataFrame([])
    return data


def wkt_to_wkb_dataset(grid_data):
    """
    This function converts all geometry data from WKT (geometric object) to WKB (hexadecimal string)
    format for a given DaVe dataset
    """
    dataset = deepcopy(grid_data)
    for key in dataset.keys():
        if isinstance(dataset[key], davestructure):
            for key_sec in dataset[key].keys():
                if isinstance(dataset[key][key_sec], davestructure):
                    for key_trd in dataset[key][key_sec].keys():
                        if isinstance(dataset[key][key_sec][key_trd], gpd.GeoDataFrame):
                            dataset[key][key_sec][key_trd] = wkt_to_wkb(
                                dataset[key][key_sec][key_trd]
                            )
                elif isinstance(dataset[key][key_sec], gpd.GeoDataFrame):
                    dataset[key][key_sec] = wkt_to_wkb(grid_data[key][key_sec])
        elif isinstance(dataset[key], gpd.GeoDataFrame):
            dataset[key] = wkt_to_wkb(grid_data[key])
    return dataset


def change_empty_gpd(grid_data):
    """
    This function replaces all empty geopandas objects with empty empty pandas objects
    """
    dataset = deepcopy(grid_data)
    for key in dataset.keys():
        if isinstance(dataset[key], davestructure):
            for key_sec in dataset[key].keys():
                if isinstance(dataset[key][key_sec], davestructure):
                    for key_trd in dataset[key][key_sec].keys():
                        if isinstance(dataset[key][key_sec][key_trd], gpd.GeoDataFrame):
                            if dataset[key][key_sec][key_trd].empty:
                                dataset[key][key_sec][key_trd] = pd.DataFrame([])
                        elif isinstance(dataset[key][key_sec][key_trd], gpd.GeoSeries):
                            if dataset[key][key_sec][key_trd].empty:
                                dataset[key][key_sec][key_trd] = pd.Series([], dtype="object")
                elif isinstance(dataset[key][key_sec], gpd.GeoDataFrame):
                    if dataset[key][key_sec].empty:
                        dataset[key][key_sec] = pd.DataFrame([])
                elif isinstance(dataset[key][key_sec], gpd.GeoSeries):
                    if dataset[key][key_sec].empty:
                        dataset[key][key_sec] = pd.Series([], dtype="object")
        elif isinstance(dataset[key], gpd.GeoDataFrame):
            if dataset[key].empty:
                dataset[key] = pd.DataFrame([])
        elif isinstance(dataset[key], gpd.GeoSeries):
            if dataset[key].empty:
                dataset[key] = pd.Series([], dtype="object")
    return dataset
