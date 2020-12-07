import geopandas as gpd
from shapely.ops import cascaded_union


def create_interim_area(areas):
    """
    This function creats a interim area to combine not connected areas
    """
    # check if there are diffrent grid areas
    if len(areas) > 1:
        # check for isolated areas
        areas_iso = []
        for i, area in areas.iterrows():
            # check if the considered area adjoining an other one
            areas_other = areas.drop([i])
            distance = areas_other.geometry.distance(area.geometry)
            if distance.min() > 0:
                area_nearest_idx = distance[distance == distance.min()].index[0]
                areas_iso.append((i, area_nearest_idx))
        # if their are isolated areas, check for a connection on the highest grid level
        if len(areas_iso) > 0:
            for area_iso in areas_iso:
                # filter areas
                geom1 = areas.loc[area_iso[0]].geometry
                geom2 = areas.loc[area_iso[1]].geometry
                # define diffrence area
                combined = cascaded_union([geom1, geom2])
                convex_hull = combined.convex_hull
                difference = convex_hull.difference(geom1)
                difference = difference.difference(geom2)
                # add difference area to areas
                areas = areas.append(gpd.GeoDataFrame({'name': 'interim area',
                                                       'geometry': [difference]}))
                areas = areas.reset_index(drop=True)

    return areas
