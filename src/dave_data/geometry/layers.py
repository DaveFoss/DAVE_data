from collections import namedtuple
from pathlib import Path

import geopandas as gpd
import pandas as pd
from geopandas import GeoDataFrame
from pandas import read_hdf
from shapely.wkb import loads

from dave_data import config as cfg
from dave_data.io.remote import download


def get_federal_state_layer():
    """
    Get a polygon layer with all federal states in Germany.

    Returns
    -------
    namedtuple : The feder state layer (layer) and the metadata (meta)

    Examples
    --------
    >>> from dave_data.geometry.layers import get_federal_state_layer
    >>> postal = get_federal_state_layer()
    >>> sorted(postal.layer["iso"])[:5]
    ['BB', 'BE', 'BW', 'BY', 'HB']
    """
    Layer = namedtuple("FederalStateLayer", ("layer", "meta"))
    layer_path = Path(cfg.get_base_path("layer"))
    filename = cfg.get("file", "federal_states_layer")
    fn = Path(layer_path, filename)
    url = cfg.get("url", "owncloud") + filename
    download(fn, url)
    meta = {}
    return Layer(gpd.read_file(fn), meta)


def get_postcode_layer():
    """
    Read postalcode and town name data from datapool for Germany

    Returns
    -------
    namedtuple : The postcode layer (layer) and the metadata (meta)

    Examples
    --------
    >>> from dave_data.geometry.layers import get_postcode_layer
    >>> postal = get_postcode_layer()
    >>> postal.layer.loc["34225"]["note"]
    '34225 Baunatal'

    >>> get_postcode_layer()[0].empty
    False
    """
    Layer = namedtuple("PostcodeLayer", ("layer", "meta"))
    filename = "plz-5stellig.feather"
    fn = Path(cfg.get_base_path("layer"), filename)
    url = cfg.get("url", "owncloud") + filename

    # download file if file does not exist
    download(fn, url)

    return Layer(
        gpd.read_feather(fn), pd.Series(cfg.get_dict("postcode_layer"))
    )


def get_nuts_layer(year=2016):
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
    >>> get_nuts_layer(year=2013)[0].empty
    False

    >>> get_nuts_layer(year=2016)[0].empty
    False

    >>> get_nuts_layer(year=2021)[0].empty
    False
    """
    # check if data is existing in datapool otherwise download it
    filename = "nuts_regions.h5"
    url = cfg.get("url", "owncloud") + filename
    fn = Path(cfg.get_base_path("layer"), filename)
    download(fn, url)
    # collect data
    nuts_regions = read_hdf(fn, key=f"/nuts_{year}")
    nuts_regions["geometry"] = nuts_regions.geometry.apply(loads)
    nuts_regions = GeoDataFrame(nuts_regions, crs=cfg.get("crs", "main"))
    # read meta data
    meta_data = {}
    return nuts_regions, meta_data
