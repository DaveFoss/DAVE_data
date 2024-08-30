from os import fsync
from os import path
from pathlib import Path

import requests
from geopandas import GeoDataFrame
from pandas import read_excel
from pandas import read_hdf
from shapely.wkb import loads


dave_data_settings = {
    "dave_data_dir": Path(Path.home(), "dave_data"),
    "crs_main": "EPSG:4326",
}


def get_data_path(filename=None, dirname=None):
    """
    This function returns the full os path for a given directory (and filename)
    """
    data_path = (
        path.join(
            dave_data_settings["dave_data_dir"], "datapool", dirname, filename
        )
        if filename
        else path.join(
            dave_data_settings["dave_data_dir"], "datapool", dirname
        )
    )
    return data_path


def download_data(filename):
    """
    Download data from DAVE_data ownCloud storage
    """
    url = (f"https://owncloud.fraunhofer.de/index.php/s/McrHKZ62ci0FxCN/"
           f"download?path=%2F&files=data/{filename}")
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
    Read postalcode and town name data from datapool for Germany

    Returns
    -------
    postalger : GeoDataFrame
    meta_data : DataFrame

    Examples
    --------
    import dave.datapool as data
    postal = data.read_postal()

    >>> read_postal()[0].empty
    False
    """

    # check if data is existing in datapool otherwise download it
    filename = "postalcodesger.h5"
    if not Path(get_data_path(filename, "data")).is_file():
        download_data(filename)
    # get data from datapool
    postalger = read_hdf(get_data_path("postalcodesger.h5", "data"))
    # convert geometry
    postalger["geometry"] = postalger.geometry.apply(loads)
    postalger = GeoDataFrame(postalger, crs=dave_data_settings["crs_main"])
    # read meta data
    meta_data = read_excel(
        get_data_path("postalcodesger_meta.xlsx", "data"), sheet_name=None
    )
    return postalger, meta_data


def read_federal_states():
    """
    Read federal state data from datapool for Germany

    Returns
    -------
    federalstatesger : GeoDataFrame
    meta_data : DataFrame

    Examples
    --------
    import dave.datapool as data
    postal = data.read_federal_states()

    >>> read_federal_states()[0].empty
    False
    """
    # check if data is existing in datapool otherwise download it
    filename = "federalstatesger.h5"
    if not Path(get_data_path(filename, "data")).is_file():
        download_data(filename)
    # get data from datapool
    federalstatesger = read_hdf(get_data_path("federalstatesger.h5", "data"))
    federalstatesger["geometry"] = federalstatesger.geometry.apply(loads)
    federalstatesger = GeoDataFrame(
        federalstatesger, crs=dave_data_settings["crs_main"]
    )
    # read meta data
    meta_data = read_excel(
        get_data_path("federalstatesger_meta.xlsx", "data"), sheet_name=None
    )
    return federalstatesger, meta_data


def read_nuts_regions(year=2016):
    """
    Read nuts data from datapool for Europe and the years 2013, 2016 and 2021

    Parameters
    ----------
    year : scalar(INT), optional(default=2016)
          The year which forms the basis of the data set

    Returns
    -------
    nuts_regions : GeoDataFrame
    meta_data : DataFrame

    Examples
    --------
    import dave.datapool as data
    postal = data.read_nuts_regions(year=2013)

    >>> read_nuts_regions(year=2013)[0].empty
    False

    >>> read_nuts_regions(year=2016)[0].empty
    False

    >>> read_nuts_regions(year=2021)[0].empty
    False
    """
    # check if data is existing in datapool otherwise download it
    filename = "nuts_regions.h5"
    if not Path(get_data_path(filename, "data")).is_file():
        download_data(filename)
    # collect data
    nuts_regions = read_hdf(
        get_data_path("nuts_regions.h5", "data"), key=f"/nuts_{year}"
    )
    if not nuts_regions.empty:
        nuts_regions["geometry"] = nuts_regions.geometry.apply(loads)
        nuts_regions = GeoDataFrame(
            nuts_regions, crs=dave_data_settings["crs_main"]
        )
    # read meta data
    meta_data = read_excel(
        get_data_path("nuts_regions_meta.xlsx", "data"), sheet_name=None
    )
    return nuts_regions, meta_data
