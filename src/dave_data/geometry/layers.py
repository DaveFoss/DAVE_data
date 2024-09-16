from collections import namedtuple
from pathlib import Path

import geopandas as gpd
import pandas as pd

from dave_data import config as cfg
from dave_data.io.remote import download


def get_layer(name, filename):
    Layer = namedtuple("Layer", ("layer", "meta"))
    fn = Path(cfg.get_base_path("layer"), filename)
    url = cfg.get("url", "owncloud") + filename

    # download file if file does not exist
    download(fn, url)

    return Layer(gpd.read_feather(fn), pd.Series(cfg.get_dict(name)))


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
    name = "federal_states_layer"
    filename = cfg.get(name, "filename")
    return get_layer(name, filename)


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
    name = "postcode_layer"
    filename = cfg.get("postcode_layer", "filename")
    return get_layer(name, filename)


def get_nuts_layer(year=2021):
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
    name = "nuts_layer"
    filename = str(cfg.get("nuts_layer", "filename")).format(year=year)
    return get_layer(name, filename)
