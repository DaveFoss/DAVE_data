from dave_data.datapool.read_data import read_federal_states
from dave_data.datapool.read_data import read_postal


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
    >>> type(postalcode_to_polygon(postalcode=['34225']))
    Polygon
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
    Creating a polygon based on town names

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
    >>> type(town_to_polygon(postalcode=['Kassel']))
    Polygon
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
    Creating a polygon based on federal states

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
    >>> type(federal_state_to_polygon(federal_state=['Hessen']))
    Polygon
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
    # add meta data
    if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
        grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
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
