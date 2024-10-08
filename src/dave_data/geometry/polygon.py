from geopandas import read_file

from dave_data.geometry.layers import get_federal_state_layer
from dave_data.geometry.layers import get_nuts_layer
from dave_data.geometry.layers import get_postcode_layer

dave_data_settings = {"crs_main": "EPSG:4326"}


def postalcode_to_polygon(postalcode):
    """
    Creating a polygon based on postalcodes

    Parameters
    ----------
    postalcode : int, str, list of str, list of int
          Postalcodes areas which define the polygon. Use ['ALL'] for all
          postalcode areas in germany

    Returns
    -------
    polygon : Shapely Polygon / MultiPolygon

    Examples
    --------
    >>> from dave_data.geometry.polygon import postalcode_to_polygon
    >>> from shapely.geometry import MultiPolygon, Polygon
    >>> polygon_postal = postalcode_to_polygon(postalcode=['34225', '34117'])
    >>> isinstance(polygon_postal, MultiPolygon)
    True
    >>> polygon_postal = postalcode_to_polygon(postalcode=[34225])
    >>> isinstance(polygon_postal, Polygon)
    True
    """
    # convert single values to list
    if isinstance(postalcode, (int, str)):
        postalcode = [str(postalcode).zfill(5)]

    # convert all values to str and check if string values are valid numbers
    postalcode = [str(int(p)).zfill(5) for p in postalcode]

    # get postcode map
    postal, meta_data = get_postcode_layer()

    # return one polygon containing all postcode polygons
    return postal.loc[postalcode].union_all()


def ags2polygon(ags):
    """
    Returns the polygon of the given region.

    Find the ags-code of any town in Germany:
    https://www.statistikportal.de/de/gemeindeverzeichnis

    Parameters
    ----------
    ags : str or int

    Returns
    -------
    shapely.polygon : Outline of the given region

    """
    raise NotImplementedError("ags2polygon is not implemented so far.")


def town_to_polygon(town):
    """
    Create a polygon based on town names

    Parameters
    ----------
    town : str
        Town areas which define the polygon. Use ['ALL'] for all town areas
        in germany

    Returns
    -------
    polygon : Shapely Polygon / MultiPolygon

    Examples
    --------
    >>> from shapely.geometry import MultiPolygon
    >>> from dave_data.geometry.polygon import town_to_polygon
    >>> polygon_town = town_to_polygon(town='Kassel')
    >>> isinstance(polygon_town, MultiPolygon)
    True
    """
    postal, meta_data = get_postcode_layer()

    town = postal.loc[postal["note"].str.lower().str.find(town.lower()) >= 0]

    return town.union_all()


def federal_state_to_polygon(federal_state):
    """
    Create a polygon based on federal states

    Parameters
    ----------
    federal_state : str
        Federal state areas which define the polygon. Use ['ALL'] for all
        Federal state areas in germany

    Returns
    -------
    polygon : Shapely Polygon / MultiPolygon

    Examples
    --------
    >>> from dave_data.geometry.polygon import federal_state_to_polygon
    >>> from shapely.geometry import MultiPolygon, Polygon
    >>> polygon_fed = federal_state_to_polygon(federal_state='Hessen')
    >>> isinstance(polygon_fed, (MultiPolygon, Polygon))
    True
    """
    states, meta_data = get_federal_state_layer()

    state = states.loc[
        states["name"].str.lower().str.find(federal_state.lower()) >= 0
    ]
    return state.union_all()


def nuts_to_polygon(nuts, year=2016):
    """
    Create a polygon based on nuts regions

    Parameters
    ----------
    nuts : List(Str)
          Nuts areas which define the polygon. Diffrent nuts levels can
          be combined. Use ['ALL'] for all Nuts 3 areas in germany

    year : scalar(INT), optional(default=2016)
          The year which forms the basis of the data set

    Returns
    -------
    polygon : Shapely Polygon / MultiPolygon

    Examples
    --------
    >>> from dave_data.geometry.polygon import nuts_to_polygon
    >>> from shapely.geometry import Polygon
    >>> polygon_nuts = nuts_to_polygon(nuts="DE11B", year=2013)
    >>> isinstance(polygon_nuts, Polygon)
    True
    """
    # read nuts-3 areas
    nuts_all, meta_data = get_nuts_layer(year=year)
    nuts_3 = nuts_all[nuts_all.LEVL_CODE == 3]

    nuts_region = nuts_3.loc[nuts_3["NUTS_ID"].str.lower() == nuts.lower()]

    return nuts_region.union_all()


def file_to_polygon(filepath, layer=None):
    """
    Create a polygon based on a file including geographical data

    Parameters
    ----------
    filepath : scalar(Str)
        Absolut Path to a file including geographical data. Possible datatypes
        are .shp, .gpkg and .geojson

    layer : scalar(Str), optional(default=None)
          The layer name of the data to be considered. Necessary for datatype
          .gpkg

    Returns
    -------
    polygon : Shapely Polygon / MultiPolygon

    """
    file_data = read_file(filepath, layer=layer)
    return file_data.union_all()
