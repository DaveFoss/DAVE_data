from os import fsync
from os import path
from pathlib import Path

import requests
from geopandas import GeoDataFrame
from pandas import read_excel
from pandas import read_hdf
from shapely.wkb import loads

from dave_data.settings import dave_settings


def get_data_path(filename=None, dirname=None):
    """
    This function returns the full os path for a given directory (and filename)
    """
    data_path = (
        path.join(dave_settings["dave_dir"], "datapool", dirname, filename)
        if filename
        else path.join(dave_settings["dave_dir"], "datapool", dirname)
    )
    return data_path


def download_data(filename):
    """
    Download data from DAVE_data ownCloud storage
    """
    url = f"https://owncloud.fraunhofer.de/index.php/s/McrHKZ62ci0FxCN/download?path=%2F&files={filename}"
    file_path = path.join(get_data_path(dirname="data"), filename)
    r = requests.get(url, stream=True, timeout=10)
    if r.ok:
        with Path(file_path).open("wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    fsync(f.fileno())
    else:
        print(f"Download failed: status code {r.status_code}\n{r.text}")


def read_postal():
    """
    This data includes the town name, the area, the population and the
    geometry for all german postalcode areas

    OUTPUT:
         **postal areas** (GeodataFrame) - all german postalcode areas

    EXAMPLE:
         import dave.datapool as data

         postal = data.read_postal()
    """
    # check if data is existing in datapool otherwise download it
    filename = "postalcodesger.h5"
    if not Path(get_data_path(filename, "data")).is_file():
        download_data(filename)
    # get data from datapool
    postalger = read_hdf(get_data_path("postalcodesger.h5", "data"))
    # convert geometry
    postalger["geometry"] = postalger.geometry.apply(loads)
    postalger = GeoDataFrame(postalger, crs=dave_settings["crs_main"])
    # read meta data
    meta_data = read_excel(
        get_data_path("postalcodesger_meta.xlsx", "data"), sheet_name=None
    )
    return postalger, meta_data


def read_federal_states():
    """
    This data includes the name, the length, the area, the population and the
    geometry for all german federal states

    OUTPUT:
         **federal_statess** (GeodataFrame) - all german federal states

    EXAMPLE:
         import dave.datapool as data

         federal = data.read_federal_states()
    """
    # check if data is existing in datapool otherwise download it
    filename = "federalstatesger.h5"
    if not Path(get_data_path(filename, "data")).is_file():
        download_data(filename)
    # get data from datapool
    federalstatesger = read_hdf(get_data_path("federalstatesger.h5", "data"))
    federalstatesger["geometry"] = federalstatesger.geometry.apply(loads)
    federalstatesger = GeoDataFrame(
        federalstatesger, crs=dave_settings["crs_main"]
    )
    # read meta data
    meta_data = read_excel(
        get_data_path("federalstatesger_meta.xlsx", "data"), sheet_name=None
    )
    return federalstatesger, meta_data


def read_nuts_regions(year):
    """
    This data includes the name and the geometry for the nuts regions of the years 2013, 2016 and 2021

    OUTPUT:
         **nuts_regions** (GeodataFrame) - nuts regions of the years 2013, 2016 and 2021

    EXAMPLE:
         import dave.datapool as data

         nuts = data.read_nuts_regions()
    """
    # check if data is existing in datapool otherwise download it
    filename = "nuts_regions.h5"
    if not Path(get_data_path(filename, "data")).is_file():
        download_data(filename)
    if year == "2013":
        nuts_regions = read_hdf(
            get_data_path("nuts_regions.h5", "data"), key="/nuts_2013"
        )
        nuts_regions["geometry"] = nuts_regions.geometry.apply(loads)
        nuts_regions = GeoDataFrame(
            nuts_regions, crs=dave_settings["crs_main"]
        )
    elif year == "2016":
        nuts_regions = read_hdf(
            get_data_path("nuts_regions.h5", "data"), key="/nuts_2016"
        )
        nuts_regions["geometry"] = nuts_regions.geometry.apply(loads)
        nuts_regions = GeoDataFrame(
            nuts_regions, crs=dave_settings["crs_main"]
        )
    elif year == "2021":
        nuts_regions = read_hdf(
            get_data_path("nuts_regions.h5", "data"), key="/nuts_2021"
        )
        nuts_regions["geometry"] = nuts_regions.geometry.apply(loads)
        nuts_regions = GeoDataFrame(
            nuts_regions, crs=dave_settings["crs_main"]
        )
    # read meta data
    meta_data = read_excel(
        get_data_path("nuts_regions_meta.xlsx", "data"), sheet_name=None
    )
    return nuts_regions, meta_data
