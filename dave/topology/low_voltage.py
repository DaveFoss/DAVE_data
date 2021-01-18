import geopandas as gpd
from shapely.geometry import Point, LineString, MultiPoint
from shapely.ops import nearest_points, cascaded_union
import pandas as pd

from dave.settings import dave_settings


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
    multiline_roads = cascaded_union(roads.geometry)
    # finding nearest connection between the building centroids and the roads
    near_points = gpd.GeoSeries([])
    for centroid in building_centroids:
        # finding nearest point
        building_index = building_centroids[building_centroids == centroid].index[0]
        near_points[building_index] = nearest_points(centroid, multiline_roads)[1]
    building_connections = pd.concat([building_centroids, near_points], axis=1)
    building_connections.columns = ['building_centroid', 'nearest_point']
    return building_connections


def line_connections(grid_data):
    """
    This function creates the line connections between the building lines (Points on the roads)
    and the road junctions
    """
    # define relevant nodes
    nearest_building_point = gpd.GeoSeries(grid_data.lv_data.lv_nodes[
        grid_data.lv_data.lv_nodes.node_type == 'nearest_point'].geometry)
    all_nodes = pd.concat([nearest_building_point,
                           grid_data.roads.road_junctions]).drop_duplicates()
    # search line connections
    line_connect = []
    for i, road in grid_data.roads.roads.iterrows():
        road_course = road.geometry.coords[:]
        # change road direction to become a uniformly road style
        if road_course[0] > road_course[len(road_course)-1]:
            road_course = road_course[::-1]
        road_points = MultiPoint(road_course)
        # find nodes wich are on the considered road and sort them
        grid_nodes = []
        for node in all_nodes:
            if road.geometry.distance(node) < 1E-10:
                grid_nodes.append(node.coords[:][0])
        grid_nodes = sorted(grid_nodes)  # sort nodes by their longitude to find start point
        if grid_nodes:  # check if their are grid nodes on the considered road
            # sort nodes by their nearest neighbor
            grid_nodes_sort = [grid_nodes[0]]  # start node
            node_index = 0
            while len(grid_nodes) > 1:  # sort nodes by their sequenz along the road
                start_node = Point(grid_nodes.pop(node_index))
                grid_nodes_points = MultiPoint(grid_nodes)
                next_node = nearest_points(start_node, grid_nodes_points)[1]
                grid_nodes_sort.append(next_node.coords[:][0])
                node_index = grid_nodes.index(next_node.coords[:][0])
            # build lines to connect the all grid nodes with each other
            for j in range(0, len(grid_nodes_sort)-1):
                line_points = []
                # get considered grid node pair
                start_point = Point(grid_nodes_sort[j])
                end_point = Point(grid_nodes_sort[j+1])
                # find nearest points to them
                start_nearest = nearest_points(start_point, road_points)[1]
                end_nearest = nearest_points(end_point, road_points)[1]
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
                for p in range(start_index, end_index+1):  # points to follow the road course
                    line_points.append(road_course[p])
                line_points.append(grid_nodes_sort[j+1])  # end point
                # create a lineString and add them to the line connection list
                line_connect.append(LineString(line_points))
    line_connect = gpd.GeoSeries(line_connect, crs=dave_settings()['crs_main'])
    # calculate line length
    line_connections_3035 = line_connect.to_crs(dave_settings()['crs_meter'])
    line_length = line_connections_3035.length
    lines_gdf = gpd.GeoDataFrame({'geometry': line_connect,
                                  'line_type': 'line_connections',
                                  'length_km': line_length/1000,
                                  'voltage_kv': 0.4,
                                  'voltage_level': 7,
                                  'source': 'dave internal'})
    grid_data.lv_data.lv_lines = grid_data.lv_data.lv_lines.append(lines_gdf)


def create_lv_topology(grid_data):
    """
    This function creates a dictonary with all relevant geographical
    informations for the target area

    INPUT:
        **grid_data** (attrdict) - all Informations about the grid

    OUTPUT:
        Writes data in the DaVe dataset
    """
    # print to inform user
    print('create low voltage network for target area')
    print('------------------------------------------')
    # --- create lv nodes
    # shortest way between building centroid and road for relevant buildings (building connections)
    buildings_rel = grid_data.buildings.for_living.append(grid_data.buildings.commercial)
    centroids = buildings_rel.reset_index(drop=True).centroid
    building_connections = nearest_road(building_centroids=centroids,
                                        roads=grid_data.roads.roads)
    # delet duplicates in nearest road points
    building_nearest = gpd.GeoSeries(building_connections.nearest_point)
    building_nearest.drop_duplicates(inplace=True)
    # add lv nodes to grid data
    building_nodes_df = gpd.GeoDataFrame({'geometry': building_connections.building_centroid,
                                          'node_type': 'building_centroid',
                                          'voltage_level': 7,
                                          'voltage_kv': 0.4,
                                          'source': 'dave internal'})
    building_nodes_df = building_nodes_df.append(gpd.GeoDataFrame({'geometry': building_nearest,
                                                                   'node_type': 'nearest_point',
                                                                   'voltage_level': 7,
                                                                   'voltage_kv': 0.4,
                                                                   'source': 'dave internal'}))
    # add dave name
    building_nodes_df.reset_index(drop=True, inplace=True)
    name = pd.Series(list(map(lambda x: f'node_7_{x}', building_nodes_df.index)))
    building_nodes_df.insert(0, 'dave_name', name)
    # add lv nodes to grid data
    grid_data.lv_data.lv_nodes = grid_data.lv_data.lv_nodes.append(building_nodes_df)
    grid_data.lv_data.lv_nodes.crs = dave_settings()['crs_main']
    # --- create lines for building connections
    line_buildings = gpd.GeoSeries(list(map(lambda x, y: LineString([x, y]),
                                            building_connections['building_centroid'],
                                            building_connections['nearest_point'])),
                                   crs='EPSG:4326')
    # calculate line length
    line_buildings = line_buildings.set_crs(dave_settings()['crs_main'])
    line_buildings_3035 = line_buildings.to_crs(dave_settings()['crs_meter'])
    line_gdf = gpd.GeoDataFrame({'geometry': line_buildings,
                                 'line_type': 'line_buildings',
                                 'length_km': line_buildings_3035.length/1000,
                                 'voltage_kv': 0.4,
                                 'voltage_level': 7,
                                 'source': 'dave internal'})
    # write line informations into grid data
    grid_data.lv_data.lv_lines = grid_data.lv_data.lv_lines.append(line_gdf)
    # set crs
    grid_data.lv_data.lv_lines.crs = dave_settings()['crs_main']
    # create line connections to connect lines for buildings and road junctions with each other
    line_connections(grid_data)
    # add dave name for lv_lines
    grid_data.lv_data.lv_lines.reset_index(drop=True, inplace=True)
    name = pd.Series(list(map(lambda x: f'line_7_{x}', grid_data.lv_data.lv_lines.index)))
    grid_data.lv_data.lv_lines.insert(0, 'dave_name', name)
    # get line bus names for each line and add to line data
    lv_nodes = grid_data.lv_data.lv_nodes
    for i, line in grid_data.lv_data.lv_lines.iterrows():
        line_coords_from = line.geometry.coords[:][0]
        line_coords_to = line.geometry.coords[:][len(line.geometry.coords[:])-1]
        from_bus = lv_nodes[lv_nodes.geometry.x == line_coords_from[0]]
        road_junctions_grid = grid_data.lv_data.lv_nodes[
            grid_data.lv_data.lv_nodes.node_type == 'road_junction']
        road_junctions_origin = grid_data.roads.road_junctions
        if len(from_bus) > 1:
            from_bus = from_bus[from_bus.geometry.y == line_coords_from[1]]
        to_bus = lv_nodes[lv_nodes.geometry.x == line_coords_to[0]]
        if len(to_bus) > 1:
            to_bus = to_bus[to_bus.geometry.y == line_coords_to[1]]
        if not from_bus.empty:
            grid_data.lv_data.lv_lines.at[line.name, 'from_bus'] = from_bus.iloc[0].dave_name
        else:
            if not road_junctions_grid.empty:
                # check if there is a suitable road junction in grid data
                distance = road_junctions_grid.geometry.distance(Point(line_coords_from))
                if distance.min() < 1E-04:
                    # road junction node was found
                    dave_name = road_junctions_grid.loc[
                        distance[distance == distance.min()].index[0]].dave_name
                else:
                    # no road junction was found, create it from road junction data
                    distance = road_junctions_origin.geometry.distance(Point(line_coords_from))
                    if distance.min() < 1E-04:
                        road_junction_geom = road_junctions_origin.loc[
                            distance[distance == distance.min()].index[0]]
                        # create lv_point for relevant road junction
                        dave_number = int(grid_data.lv_data.lv_nodes.dave_name.tail(1).iloc[
                            0].replace('node_7_', ''))
                        dave_name = 'node_7_' + str(dave_number+1)
                        junction_point_gdf = gpd.GeoDataFrame(
                            {'geometry': [road_junction_geom],
                             'dave_name': dave_name,
                             'node_type': 'road_junction',
                             'voltage_level': 7,
                             'voltage_kv': 0.4,
                             'source': 'dave internal'})
                        grid_data.lv_data.lv_nodes = grid_data.lv_data.lv_nodes.append(
                            junction_point_gdf)
            else:
                distance = road_junctions_origin.geometry.distance(Point(line_coords_from))
                if distance.min() < 1E-04:
                    road_junction_geom = road_junctions_origin.loc[
                        distance[distance == distance.min()].index[0]]
                    # create lv_point for relevant road junction
                    dave_number = int(grid_data.lv_data.lv_nodes.dave_name.tail(1).iloc[
                        0].replace('node_7_', ''))
                    dave_name = 'node_7_' + str(dave_number+1)
                    junction_point_gdf = gpd.GeoDataFrame(
                        {'geometry': [road_junction_geom],
                         'dave_name': dave_name,
                         'node_type': 'road_junction',
                         'voltage_level': 7,
                         'voltage_kv': 0.4,
                         'source': 'dave internal'})
                    grid_data.lv_data.lv_nodes = grid_data.lv_data.lv_nodes.append(
                        junction_point_gdf)
            grid_data.lv_data.lv_lines.at[line.name, 'from_bus'] = dave_name
        grid_data.lv_data.lv_nodes.reset_index(drop=True, inplace=True)
        road_junctions_grid = grid_data.lv_data.lv_nodes[
            grid_data.lv_data.lv_nodes.node_type == 'road_junction']
        if not to_bus.empty:
            grid_data.lv_data.lv_lines.at[line.name, 'to_bus'] = to_bus.iloc[0].dave_name
        else:
            if not road_junctions_grid.empty:
                # check if there is a suitable road junction in grid data
                distance = road_junctions_grid.geometry.distance(Point(line_coords_to))
                if distance.min() < 1E-04:
                    # road junction node was found
                    dave_name = road_junctions_grid.loc[
                        distance[distance == distance.min()].index[0]].dave_name
                else:
                    # no road junction was found, create it from road junction data
                    distance = road_junctions_origin.geometry.distance(Point(line_coords_to))
                    if distance.min() < 1E-04:
                        road_junction_geom = road_junctions_origin.loc[
                            distance[distance == distance.min()].index[0]]
                        # create lv_point for relevant road junction
                        dave_number = int(grid_data.lv_data.lv_nodes.dave_name.tail(1).iloc[
                            0].replace('node_7_', ''))
                        dave_name = 'node_7_' + str(dave_number+1)
                        junction_point_gdf = gpd.GeoDataFrame(
                            {'geometry': [road_junction_geom],
                             'dave_name': dave_name,
                             'node_type': 'road_junction',
                             'voltage_level': 7,
                             'voltage_kv': 0.4,
                             'source': 'dave internal'})
                        grid_data.lv_data.lv_nodes = grid_data.lv_data.lv_nodes.append(
                            junction_point_gdf)
            else:
                distance = road_junctions_origin.geometry.distance(Point(line_coords_to))
                if distance.min() < 1E-04:
                    road_junction_geom = road_junctions_origin.loc[
                        distance[distance == distance.min()].index[0]]
                    # create lv_point for relevant road junction
                    dave_number = int(grid_data.lv_data.lv_nodes.dave_name.tail(1).iloc[
                        0].replace('node_7_', ''))
                    dave_name = 'node_7_' + str(dave_number+1)
                    junction_point_gdf = gpd.GeoDataFrame(
                        {'geometry': [road_junction_geom],
                         'dave_name': dave_name,
                         'node_type': 'road_junction',
                         'voltage_level': 7,
                         'voltage_kv': 0.4,
                         'source': 'dave internal'})
                    grid_data.lv_data.lv_nodes = grid_data.lv_data.lv_nodes.append(
                        junction_point_gdf)
            grid_data.lv_data.lv_lines.at[line.name, 'to_bus'] = dave_name
        grid_data.lv_data.lv_nodes.reset_index(drop=True, inplace=True)
