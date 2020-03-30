import geopandas as gpd
import shapely.geometry
from shapely import affinity
import pandas as pd


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

def line_connections(grid_data):
    """
    This function creates the line connections between the building lines (Points on the roads)
    and the road junctions
    """
    # define relevant nodes
    nearest_building_point = gpd.GeoSeries(grid_data.lv_data.lv_nodes.building_connections.nearest_point)
    road_junctions = grid_data.roads.road_junctions
    all_nodes = pd.concat([nearest_building_point, road_junctions]).drop_duplicates()
    # search line connections
    line_connections = []
    for i, road in grid_data.roads.roads.iterrows():
        road_course = road.geometry.coords[:]
        # change road direction to become a uniformly road style
        if road_course[0] > road_course[len(road_course)-1]:
            road_course = road_course[::-1]
        road_points = shapely.geometry.MultiPoint(road_course)
        # find nodes wich are on the considered road and sort them
        grid_nodes = []
        for node in all_nodes:
            if road.geometry.distance(node) < 1E-10:
                grid_nodes.append(node.coords[:][0])
        grid_nodes = sorted(grid_nodes)  # sort nodes by their longitude to find start point
        if grid_nodes:  # check if their are grid nodes on the considered road
            # sort nodes by their nearest neighbor
            grid_nodes_sort = [grid_nodes[0]]  # start node
            node_index=0
            while len(grid_nodes)>1:  # sort nodes by their sequenz along the road 
                start_node = shapely.geometry.Point(grid_nodes.pop(node_index))
                grid_nodes_points = shapely.geometry.MultiPoint(grid_nodes)
                next_node = shapely.ops.nearest_points(start_node, grid_nodes_points)[1]
                grid_nodes_sort.append(next_node.coords[:][0])
                node_index = grid_nodes.index(next_node.coords[:][0])
            # build lines to connect the all grid nodes with each other
            for j in range(0, len(grid_nodes_sort)-1):
                line_points = []
                # get considered grid node pair
                start_point = shapely.geometry.Point(grid_nodes_sort[j])
                end_point = shapely.geometry.Point(grid_nodes_sort[j+1])
                # find nearest points to them
                start_nearest = shapely.ops.nearest_points(start_point, road_points)[1]
                end_nearest = shapely.ops.nearest_points(end_point, road_points)[1]
                # find road index
                for point in road_course:
                    if point[0] == start_nearest.x:
                        start_index = road_course.index(point)
                    if point[0] == end_nearest.x:
                        end_index = road_course.index(point)
                # check if start_nearest between start and end point
                if abs(end_point.distance(start_nearest)) > abs(end_point.distance(start_point)):
                    start_index += 1
                # check if end_nearest is between start and end point
                if abs(start_point.distance(end_nearest)) > abs(start_point.distance(end_point)):
                    end_index -= 1
                # add points
                line_points.append(grid_nodes_sort[j])  # start point
                for p in range(start_index, end_index+1):  # points between to follow the road course
                    line_points.append(road_course[p])
                line_points.append(grid_nodes_sort[j+1])  # end point
                # create a lineString and add them to the line connection list
                line_connection = shapely.geometry.LineString(line_points)
                line_connections.append(line_connection)
    line_connections = gpd.GeoSeries(line_connections, crs = 'EPSG:4326')
    # calculate line length
    line_connections_3035 = line_connections.to_crs(epsg=3035)  # project lines to crs with unit in meter
    line_length = line_connections_3035.length
    grid_data.lv_data.lv_lines.line_connections = grid_data.lv_data.lv_lines.line_connections.append(gpd.GeoDataFrame({'geometry':line_connections, 
                                                                                                                       'length_m':line_length}))
    
def create_lv_topology(grid_data):
    """
    This function creates a dictonary with all relevant geographical 
    informations for the target area

    INPUT:
        **grid_data** (attrdict) - all Informations about the grid

    OPTIONAL:

    OUTPUT:

    EXAMPLE:
    """
    # print to inform user
    print('create low voltage network for target area')
    print('------------------------------------------')
    # shortest way between building centroid and road for relevant buildings (building connections)
    buildings_index = list(grid_data.buildings.for_living.append(grid_data.buildings.commercial).index)
    centroids = grid_data.buildings.building_centroids[grid_data.buildings.building_centroids.index.isin(buildings_index)]
    building_connections = nearest_road(building_centroids=centroids,
                                        roads=grid_data.roads.roads)
    grid_data.lv_data.lv_nodes.building_connections = grid_data.lv_data.lv_nodes.building_connections.append(building_connections)

    # --- create lines for building connections
    line_buildings = gpd.GeoSeries([], crs = 'EPSG:4326')
    for i, connection in grid_data.lv_data.lv_nodes.building_connections.iterrows():
        line_build = shapely.geometry.LineString([connection['building_centroid'],
                                                  connection['nearest_point']])
        line_buildings[i] = line_build
    # calculate line length
    line_buildings_3035 = line_buildings.to_crs(epsg=3035)  # project lines to crs with unit in meter
    line_length = line_buildings_3035.length
    # write line informations into grid data
    grid_data.lv_data.lv_lines.line_buildings = grid_data.lv_data.lv_lines.line_buildings.append(gpd.GeoDataFrame({'geometry':line_buildings, 
                                                                                                                   'length_m':line_length}))
    # create line connections to connect lines for buildings and road junctions with each other
    line_connections(grid_data)

   
  

