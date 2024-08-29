"""
Helper functions to get a polygon of specific regions

License: MIT
"""

from geopandas import read_file
from pandas import concat

from dave_data.datapool.read_data import read_federal_states
from dave_data.datapool.read_data import read_nuts_regions
from dave_data.datapool.read_data import read_postal
from dave_data.settings import dave_data_settings


def postalcode_to_polygon(postalcode):
    """
    Creating a polygon based on postalcodes

    Parameters
    ----------
    postalcode : List(Str)
          Postalcodes areas which define the polygon. It could also be choose ['ALL'] for all postalcode areas in germany

    Returns
    -------
    polygon : Shapely Polygon / MultiPolygon

    Examples
    --------
    from dave_data.area_to_polygon import postalcode_to_polygon
    polygon_postal = postalcode_to_polygon(postalcode=['34225', '34117'])

    >>> from shapely.geometry import Polygon
    >>> isinstance((postalcode_to_polygon(postalcode=['34225'])), Polygon)
    True
    """
    # read postalcode data
    postal, meta_data = read_postal()
    if len(postalcode) == 1 and postalcode[0].lower() == "all":
        # in this case all postalcode areas will be choosen
        postal_filtered = postal
    else:
        postal_filtered = postal[
            postal.postalcode.isin(postalcode)
        ].reset_index(drop=True)
    # create polygon from postalcodes
    polygon = postal_filtered.geometry.union_all()
    return polygon


def town_to_polygon(town):
    """
    Create a polygon based on town names

    Parameters
    ----------
    town : List(Str)
          Town areas which define the polygon. It could also be choose ['ALL'] for all town areas in germany

    Returns
    -------
    polygon : Shapely Polygon / MultiPolygon

    Examples
    --------
    from dave_data.area_to_polygon import town_to_polygon
    polygon_town = town_to_polygon(postalcode=['Kassel'])

    >>> from shapely.geometry import Polygon
    >>> isinstance(town_to_polygon(town=['Kassel']), Polygon)
    True
    """
    postal, meta_data = read_postal()
    if len(town) == 1 and town[0].lower() == "all":
        # in this case all town names will be choosen
        town_filtered = postal
    else:
        # bring town names in right format and filter data
        normalized_town_names = [town_name.lower() for town_name in town]
        normalized_postal_town = postal.town.str.lower()
        indexes = normalized_postal_town.isin(normalized_town_names)
        town_filtered = postal[indexes].reset_index(drop=True)
        if len(town_filtered.town.unique()) != len(town):
            raise ValueError("town name wasn`t found. Please check your input")
    # create polygon from postalcodes
    polygon = town_filtered.geometry.union_all()
    return polygon


def federal_state_to_polygon(federal_state):
    """
    Create a polygon based on federal states

    Parameters
    ----------
    federal_state : List(Str)
          Federal state areas which define the polygon. It could also be choose ['ALL'] for all Federal state areas in germany

    Returns
    -------
    polygon : Shapely Polygon / MultiPolygon

    Examples
    --------
    from dave_data.area_to_polygon import federal_state_to_polygon
    polygon_fed = federal_state_to_polygon(federal_state=['Hessen'])

    >>> from shapely.geometry import Polygon
    >>> isinstance(federal_state_to_polygon(federal_state=['Hessen']), Polygon)
    True
    """
    states, meta_data = read_federal_states()
    # add meta data
    if len(federal_state) == 1 and federal_state[0].lower() == "all":
        # in this case all federal states will be choosen
        federal_state_filtered = states
    else:
        # bring federal state names in right format and filter data
        federal_state = [
            "-".join([part.capitalize() for part in state.split("-")])
            for state in federal_state
        ]

        federal_state_filtered = states[
            states["name"].isin(federal_state)
        ].reset_index(drop=True)
        if len(federal_state_filtered) != len(federal_state):
            raise ValueError(
                "federal state name wasn`t found. Please check your input"
            )
    """
    # convert federal states into postal code areas for target_input
    postal, meta_data = read_postal()
    # filter postal code areas which are within the target area
    postal_intersection = intersection_with_area(
        postal, target, remove_columns=False
    )
    # filter duplicated postal codes
    federal_state_postal = postal_intersection["postalcode"].unique().tolist()
    """
    # create polygon from federal states
    polygon = federal_state_filtered.geometry.union_all()
    return polygon


def nuts_to_polygon(nuts, year=2016):
    """
    Create a polygon based on nuts regions

    Parameters
    ----------
    nuts : List(Str)
          Nuts areas which define the polygon. Diffrent nuts levels can combined. It could also be choose ['ALL'] for all Nuts 3 areas in germany

    year : scalar(INT), optional(default=2016)
          The year which forms the basis of the data set

    Returns
    -------
    polygon : Shapely Polygon / MultiPolygon

    Examples
    --------
    from dave_data.area_to_polygon import nuts_to_polygon
    polygon_nuts = nuts_to_polygon(nuts=['DE1', 'DE22'], year=2013)

    >>> from shapely.geometry import Polygon
    >>> isinstance(federal_state_to_polygon(federal_state=['Hessen']), Polygon)
    True
    """
    # read nuts-3 areas
    nuts_all, meta_data = read_nuts_regions(year=year)
    nuts_3 = nuts_all[nuts_all.LEVL_CODE == 3]
    # filter nuts data
    if len(nuts) == 1 and nuts[0].lower() == "all":
        # in this case all nuts_regions will be choosen
        nuts_filtered = nuts_3
    else:
        # bring NUTS ID in right format
        nuts_regions = [
            "".join(
                [
                    letter.upper() if letter.isalpha() else letter
                    for letter in list(nuts_region)
                ]
            )
            for nuts_region in nuts
        ]
        for region in nuts_regions:
            # get area for the singel nuts region and concat them
            nuts_contains = nuts_3[nuts_3["NUTS_ID"].str.contains(region)]
            nuts_filtered = (
                nuts_contains
                if region == nuts_regions[0]
                else concat([nuts_filtered, nuts_contains], ignore_index=True)
            )
            if nuts_contains.empty:
                raise ValueError(
                    f"nuts name '{region}' wasn`t found. Please check your input"
                )
    # filter duplicates
    nuts_filtered.drop_duplicates(inplace=True)

    """
    # convert nuts regions into postal code areas for target_input
    postal, meta_data = read_postal()
    # filter postal code areas which are within the target area
    postal_intersection = intersection_with_area(
        postal, target, remove_columns=False
    )
    # filter duplicated postal codes
    nuts_region_postal = postal_intersection["postalcode"].unique().tolist()
    """
    # create polygon from nuts regions
    polygon = nuts_filtered.geometry.union_all()
    return polygon


def file_to_polygon(filepath, layer=None):
    """
    Create a polygon based on a file including geographical data

    Parameters
    ----------
    filepath : scalar(Str)
          Absolut Path to a file including geographical data. Possible datatypes are .shp, .gpkg and .geojson

    layer : scalar(Str), optional(default=None)
          The layer name of the data to be considered. Necessary for datatype .gpkg

    Returns
    -------
    polygon : Shapely Polygon / MultiPolygon

    Examples
    --------
    from dave_data.area_to_polygon import file_to_polygon
    polygon = file_to_polygon(filepath)
    """

    """
    This function define the target area by a own area from the user. This could be a shapefile or
    directly a polygon. Furthermore the function filter the postalcode informations for the target area.
    """
    # read file
    if filepath.split(".")[-1] in ["shp", "geojson"]:
        file_data = read_file(filepath)
    elif filepath.split(".")[-1] in ["gpkg"]:
        if layer is None:
            raise ValueError(
                "At .gpkg files a layer specification is necessary"
            )
        file_data = read_file(filepath, layer=layer)
    else:
        raise ValueError("The given file is not in a supported format")
    # check if the given file is empty
    if file_data.empty:
        raise ValueError("The given file includes no data")

    # check crs and project to the right one if needed
    if (file_data.crs) and (file_data.crs != dave_data_settings["crs_main"]):
        file_data = file_data.to_crs(dave_data_settings["crs_main"])
    if "id" in file_data.keys():
        file_data = file_data.drop(columns=["id"])
    """
    # convert own area into postal code areas for target_input
    postal, meta_data = read_postal()
    # filter postal code areas which are within the target area
    postal_intersection = intersection_with_area(
        postal, target, remove_columns=False
    )
    # filter duplicated postal codes
    own_postal = postal_intersection["postalcode"].unique().tolist()
    """
    # create polygon from file data
    polygon = file_data.geometry.union_all()
    return polygon
