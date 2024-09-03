from collections import namedtuple

import geopandas as gpd

from dave_data.geometry.layers import get_federal_state_layer


def divide_between_federal_states(polygon):
    """
    Get the name and iso code of the underlying federal state for each part of
    the given polygon.

    Parameters
    ----------
    polygon : shapely.geometry
        A valid shapely geometry.

    Returns
    -------
    geopandas.GeoDataFrame

    """
    poly = gpd.GeoDataFrame(index=[0], crs="epsg:4326", geometry=[polygon])
    fs_map = get_federal_state_layer().layer
    return fs_map.clip(poly)
