import geopandas as gpd
import numpy as np
from scipy.spatial import Voronoi
from shapely.geometry import LineString
from shapely.ops import polygonize, cascaded_union


def create_interim_area(areas):
    """
    This function creats a interim area to combine not connected areas.

    INPUT:
        **areas** (GeoDataFrame) - all considered grid areas

    OUTPUT:
        **areas** (GeoDataFrame) - all considered grid areas extended with interim areas
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
                areas.reset_index(drop=True, inplace=True)

    return areas


def voronoi(points):
    """
    This function calculates the voronoi diagram for given points within germany

    INPUT:
        **voronoi_points** (GeoDataFrame) - all nodes for voronoi analysis

    OUTPUT:
        **voronoi polygons** (GeoDataFrame) - all voronoi areas for the given points
    """
    # define points for voronoi centroids
    voronoi_centroids = [[point.x, point.y] for i, point in points.geometry.iteritems()]
    voronoi_points = np.array(voronoi_centroids)
    # define maximum points that lying outside germany
    points_boundary = [[5.58613450984361304, 55.11274402414650808],
                       [15.29889892264705864, 55.11274402414650808],
                       [15.23491496735850248, 47.13557706547874915],
                       [5.60532969643017687, 47.12687113266557759]]
    # append boundary points to avoid infinit polygons with relevant nodes
    voronoi_points = np.append(voronoi_points, points_boundary, axis=0)
    # carry out voronoi analysis
    vor = Voronoi(voronoi_points)
    # select finit lines and create LineStrings
    lines = [LineString(vor.vertices[line])
             for line in vor.ridge_vertices
             if -1 not in line]  # filtering regions with -1 because these are infinit
    # create polygons from the lines
    polygons = np.array(list(polygonize(lines)))
    # create GeoDataFrame with polygons
    voronoi_polygons = gpd.GeoDataFrame(geometry=polygons, crs='EPSG:4326')
    # search voronoi centroids and dave name
    voronoi_polygons['centroid'] = None
    voronoi_polygons['dave_name'] = None
    for i, polygon in voronoi_polygons.iterrows():
        for j, point in points.iterrows():
            if polygon.geometry.contains(point.geometry):
                voronoi_polygons.at[polygon.name, 'centroid'] = point.geometry
                if not points.dave_name.empty:
                    voronoi_polygons.at[polygon.name, 'dave_name'] = point.dave_name
                break
    return voronoi_polygons
