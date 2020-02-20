import geopandas as gpd
import shapely.geometry
from shapely import affinity
import pandas as pd
import copy


def nearest_road(building_centroids, roads):
    """
    This function finds the shortest way between the building centroids and a road via shapely 
    function 
    
    INPUT:
        **building centroids** (GeoDataSeries) - buildings in the target area
        **roads** (GeoDataFrame) - relevant roads in the target area
    
    OUTPUT:
        **building connections** (dict) - 
        
    """
    # create multistring of relevant roads and intersect radial lines with it
    multiline_roads = shapely.ops.cascaded_union(roads.geometry)
    # finding nearest connection between the building centroids and the roads
    nearest_points = gpd.GeoSeries([])
    for centroid in building_centroids:
        # finding nearest point
        point_near = shapely.ops.nearest_points(centroid, multiline_roads)[1]
        building_index = building_centroids[building_centroids==centroid].index[0]
        nearest_points[building_index]=point_near
    building_connections = pd.concat([building_centroids, nearest_points], axis=1)
    building_connections.columns = ['building_centroid', 'nearest_point']  
    return building_connections


def nearest_road_radial(building_centroids, roads, line_length=2E-3, line_ankle=10):
    """ 
    Old function, the nearest_road function is faster. 
    
    This function finds the shortest way between the building centroids and a road. For this the 
    Method uses radial lines which start from the building centroid. From that there are many 
    intersections between the radial lines and the roads. At the last step the intersection point
    with the shortest distance to the building centroid will be searched.
    
    INPUT:
        **building centroids** (GeoDataSeries) - buildings in the target area
        **roads** (GeoDataFrame) - relevant roads in the target area
    
    OPTIONAL:
        **line length** (float, default 2E-3) - defines the length auf the radial lines
        **line amkle** (float, default 10) - defines ankle between the radial lines
    
    OUTPUT:
        **building connections** (DataFrame) - DataFrame includes the shortest connection to a road for each building centroid

        
    """
    # create multistring of relevant roads and intersect radial lines with it
    multiline_roads = shapely.ops.cascaded_union(roads.geometry)
    # finding nearest connection between the building centroids and the roads
    nearest_points = gpd.GeoSeries([])
    for centroid in building_centroids:
        # create radial lines for searching
        line = shapely.geometry.LineString([(centroid.x,centroid.y),
                                            (centroid.x,centroid.y+line_length)])
        line_rad = [affinity.rotate(line, i, (centroid.x,centroid.y)) for i in range(0,360,line_ankle)]
        multiline_rad = shapely.ops.cascaded_union(line_rad)
        points_int = multiline_roads.intersection(multiline_rad)
        if not points_int:
            # if there is no intersection point set it equal the building point
            points_int = centroid
        # finding nearest point
        point_near = shapely.ops.nearest_points(centroid, points_int)[1]
        # write data in  series

        building_index = building_centroids[building_centroids==centroid].index[0]
        nearest_points[building_index]=point_near
    building_connections = pd.concat([building_centroids, nearest_points], axis=1)
    building_connections.columns = ['building_centroid', 'nearest_point']  
    return building_connections

def create_lv_topology(target_area):
    """
    This function creates a dictonary with all relevant geographical informations for the target area

    INPUT:
        **target area** (dict) - all Informations about the target area

    OPTIONAL:

    OUTPUT:
        **grid data** (dict) - expanded target area dictonary with all informations about the grid
    EXAMPLE:
    """
    # copy target area data
    grid_data_lv = copy.copy(target_area)
    
    # shortest way between building centroid and road for relevant buildings (building connections)
    buildings_index = list(target_area['buildings']['for_living'].append(target_area['buildings'] \
                           ['commercial']).index)
    centroids = target_area['buildings']['building_centroids'][target_area['buildings'] \
                            ['building_centroids'].index.isin(buildings_index)]
    building_connections = nearest_road(building_centroids= centroids,
                                              roads= target_area['roads']['roads'])
    grid_data_lv['buildings']['building_connections'] = building_connections
    
    # create lines for building connections
    line_buildings = gpd.GeoSeries([])
    for i, connection in grid_data_lv['buildings']['building_connections'].iterrows():
        line_build = shapely.geometry.LineString([connection['building_centroid'],
                                                  connection['nearest_point']])
        line_buildings[i] = line_build
    grid_data_lv['lines_lv'] = {}
    grid_data_lv['lines_lv']['line_buildings'] = line_buildings

    # --- create line connections to connect lines for buildings and road junctions with each other
    # define relevant nodes
    nearest_buildin_point = gpd.GeoSeries(grid_data_lv['buildings']['building_connections']['nearest_point'])
    road_junctions = grid_data_lv['roads']['road_junctions']
    all_nodes = pd.concat([nearest_buildin_point, road_junctions]).drop_duplicates()
    # search line connections
    line_connections = []
    for i, road in grid_data_lv['roads']['roads'].iterrows():
        road_course = sorted(road.geometry.coords[:])
        grid_nodes = []
        # find nodes wich are on the considered road
        for node in all_nodes:
            if road.geometry.distance(node) < 1E-10:
                grid_nodes.append(node.coords[:][0]) 
        grid_nodes = sorted(grid_nodes)
        # build lines to connect the nodes
        for j in range (0,len(grid_nodes)-1):  
            line_points = []
            # get start point
            line_points.append(grid_nodes[j])
            # get points between start and end point from road course
            for p in range(0, len(road_course)):
                # first filter by lon range
                if grid_nodes[j] < road_course[p] and road_course[p] < grid_nodes[j+1]:
                    line_points.append(road_course[p])
            # get end point
            line_points.append(grid_nodes[j+1])
            # create a lineString and add them to the line connection list
            line_connection = shapely.geometry.LineString(line_points)
            line_connections.append(line_connection)
    line_connections = gpd.GeoSeries(line_connections)
    grid_data_lv['lines_lv']['line_connections'] = line_connections

    """
    Ablauf:
    # 1. suchen der kürzesten verbindung zwischen einem Gebäudemittelpunkt und einer Straße
    # 2. Erstellen eines Endpunktes auf der Straße für diese kürzeste Verbindung

    4. Erstellen der relevanten gebäudeknoten und der Endknoten aus der nähesten straße funktion

    6. Erstellen der weiteren knoten bzw. umspannwerke aus OSM raussuchen
    7. Leitungsinformationen für lv von OSM beziehen
    8. Verbinden der Gebäudestiche miteinander, entlang der Straße
    9. Externes Netz an den Übergabestellen zur mv ebene erstellen
    """
    
    
    return grid_data_lv     #, grid_model
   
  

