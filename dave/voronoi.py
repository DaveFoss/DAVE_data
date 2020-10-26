from scipy.spatial import Voronoi
from shapely.geometry import LineString
from shapely.ops import polygonize
import geopandas as gpd
import numpy as np


def voronoi(points):
    """
    This function calculates the voronoi diagram for given points within germany

    INPUT:
        **voronoi_points** (GeoDataFrame) - all nodes for voronoi analysis

    OUTPUT:
        **voronoi polygons** (GeoDataFrame) - all voronoi areas for the given points

    EXAMPLE:
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




# Evt. noch eine weitere Funktion zur voronoi Analyse schreiben, die die Landnutzung mit einbezieht. 
# Da ich aber nicht immer die LAndnutzung mit drin haben möchte, bleibt die bisherige funktion drin
# LAndnutzung wäre relevant wenn man Einwohnerzahlen behandelt/ die Wohnfläche eines Gebiets benötigt