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
    meta_data : DataFrame

    Examples # !!! todo
    --------
    from dave_data.area_to_polygon import postalcode_to_polygon
    polygon_postal = postalcode_to_polygon(postalcode=['34225', '34117'])

    >>> type(postalcode_to_polygon(postalcode=['34225'])[0])
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
    polygon = postal_filtered.geometry.unary_union
    return polygon, meta_data
