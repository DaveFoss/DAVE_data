# Copyright (c) 2022-2024 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from geopandas import GeoDataFrame, GeoSeries
from pandas import Series, concat
from shapely.geometry import LineString, MultiPoint, Point
from shapely.ops import nearest_points
from tqdm import tqdm

from dave.datapool.oep_request import oep_request
from dave.settings import dave_settings
from dave.toolbox import intersection_with_area, related_sub


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
    multiline_roads = roads.geometry.unary_union
    # finding nearest connection between the building centroids and the roads
    near_points = GeoSeries(
        list(map(lambda x: nearest_points(x, multiline_roads)[1], building_centroids)),
        crs="EPSG:4326",
    )
    building_connections = concat([building_centroids, near_points], axis=1)
    building_connections.columns = ["building_centroid", "nearest_point"]
    return building_connections


def connect_grid_nodes(road_course, road_points, start_node, end_node):
    """
    This function builds lines to connect grid nodes with each other along road courses
    """
    # get considered grid node pair
    start_point = Point(start_node)
    end_point = Point(end_node)
    # find nearest points to them
    start_nearest = nearest_points(start_point, road_points)[1]
    end_nearest = nearest_points(end_point, road_points)[1]
    # find road index
    start_index = road_course.index((start_nearest.x, start_nearest.y))
    end_index = road_course.index((end_nearest.x, end_nearest.y))
    # check if start_nearest between start and end point
    if abs(end_point.distance(start_nearest)) > abs(end_point.distance(start_point)):
        start_index += 1
    # check if end_nearest is between start and end point
    if abs(start_point.distance(end_nearest)) > abs(start_point.distance(end_point)):
        end_index -= 1
    # add points [start_point, points to follow the road course, end point]
    line_points = (
        [start_node] + [road_course[k] for k in range(start_index, end_index + 1)] + [end_node]
    )
    # create a lineString and return them
    return LineString(line_points)


def search_line_connections(road_geometry, all_nodes):
    road_course = road_geometry.coords[:]
    # change road direction to become a uniformly road style
    if road_course[0] > road_course[len(road_course) - 1]:
        road_course = road_course[::-1]
    road_points = MultiPoint(road_course)
    # find nodes on the considered road and sort them by their longitude to find start point
    grid_nodes = sorted(
        [node.coords[:][0] for node in all_nodes if road_geometry.distance(node) < 1e-10]
    )
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
        # build lines to connect all grid nodes with each other
        return [
            connect_grid_nodes(
                road_course,
                road_points,
                start_node=grid_nodes_sort[j],
                end_node=grid_nodes_sort[j + 1],
            )
            for j in range(0, len(grid_nodes_sort) - 1)
        ]
    else:
        return []


def line_connections(grid_data):
    """
    This function creates the line connections between the building lines (Points on the roads)
    and the road junctions
    """
    # define relevant nodes
    nearest_building_point = GeoSeries(
        grid_data.lv_data.lv_nodes[
            grid_data.lv_data.lv_nodes.node_type == "grid_connection"
        ].geometry
    )
    all_nodes = concat([nearest_building_point, grid_data.roads.road_junctions]).drop_duplicates()
    # search line connections
    line_connect = GeoSeries(
        sum(
            grid_data.roads.roads.geometry.apply(
                lambda x: search_line_connections(x, all_nodes)
            ).to_list(),
            [],
        ),
        crs=dave_settings["crs_main"],
    )  # Todo: TypeError: Non geometry data passed to GeoSeries constructor, received data of dtype 'object'
    # calculate line length
    line_connections_3035 = line_connect.to_crs(dave_settings["crs_meter"])
    lines_gdf = GeoDataFrame(
        {
            "geometry": line_connect,
            "line_type": "line_connections",
            "length_km": line_connections_3035.length / 1000,
            "voltage_kv": 0.4,
            "voltage_level": 7,
            "source": "dave internal",
        },
        crs=dave_settings["crs_main"],
    )
    grid_data.lv_data.lv_lines = concat([grid_data.lv_data.lv_lines, lines_gdf], ignore_index=True)


def create_lv_topology(grid_data):
    """
    This function creates a dictonary with all relevant geographical
    informations for the target area

    INPUT:
        **grid_data** (attrdict) - all Informations about the grid

    OUTPUT:
        Writes data in the DaVe dataset
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create low voltage topology:       ",
        position=0,
        bar_format=dave_settings["bar_format"],
    )
    # --- create substations
    # create mv/lv substations
    if grid_data.components_power.substations.mv_lv.empty:
        mvlv_substations, meta_data = oep_request(table="ego_dp_mvlv_substation")
        # add meta data
        if (
            bool(meta_data)
            and f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys()
        ):
            grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        mvlv_substations.rename(
            columns={"version": "ego_version", "mvlv_subst_id": "ego_subst_id"}, inplace=True
        )
        # change wrong crs from oep
        mvlv_substations.crs = dave_settings["crs_main"]
        # filter trafos which are within the grid area
        mvlv_substations = intersection_with_area(mvlv_substations, grid_data.area)
        if not mvlv_substations.empty:
            mvlv_substations["voltage_level"] = 6
            # add dave name
            mvlv_substations.reset_index(drop=True, inplace=True)
            mvlv_substations.insert(
                0,
                "dave_name",
                Series(list(map(lambda x: f"substation_6_{x}", mvlv_substations.index))),
            )
            # add ehv substations to grid data
            grid_data.components_power.substations.mv_lv = concat(
                [grid_data.components_power.substations.mv_lv, mvlv_substations], ignore_index=True
            )
    else:
        mvlv_substations = grid_data.components_power.substations.mv_lv.copy()
    # update progress
    pbar.update(5)
    # --- create lv nodes
    # shortest way between building centroid and road for relevant buildings (building connections)
    buildings_rel = concat(
        [grid_data.buildings.residential, grid_data.buildings.commercial], ignore_index=True
    )
    buildings_rel_3035 = buildings_rel.to_crs(dave_settings["crs_meter"])
    centroids = buildings_rel_3035.reset_index(drop=True).centroid
    centroids = centroids.to_crs(dave_settings["crs_main"])
    building_connections = nearest_road(building_centroids=centroids, roads=grid_data.roads.roads)
    # delet duplicates in nearest road points
    building_nearest = GeoSeries(building_connections.nearest_point)
    building_nearest.drop_duplicates(inplace=True)
    # add lv nodes to grid data
    building_nodes_df = GeoDataFrame(
        {
            "geometry": building_connections.building_centroid,
            "node_type": "building_connection",
            "voltage_level": 7,
            "voltage_kv": 0.4,
            "source": "dave internal",
        }
    )
    building_nodes_df = concat(
        [
            building_nodes_df,
            GeoDataFrame(
                {
                    "geometry": building_nearest,
                    "node_type": "grid_connection",
                    "voltage_level": 7,
                    "voltage_kv": 0.4,
                    "source": "dave internal",
                }
            ),
        ],
        ignore_index=True,
    )
    # search for the substations where the lv nodes are within
    sub_infos = building_nodes_df.geometry.apply(lambda x: related_sub(x, mvlv_substations))
    building_nodes_df["ego_subst_id"] = sub_infos.apply(lambda x: x[0])
    building_nodes_df["subst_dave_name"] = sub_infos.apply(lambda x: x[1])
    building_nodes_df["subst_name"] = sub_infos.apply(lambda x: x[2])
    # update progress
    pbar.update(5)
    # add dave name
    building_nodes_df.reset_index(drop=True, inplace=True)
    building_nodes_df.insert(
        0, "dave_name", Series(list(map(lambda x: f"node_7_{x}", building_nodes_df.index)))
    )
    # add lv nodes to grid data
    grid_data.lv_data.lv_nodes = concat(
        [grid_data.lv_data.lv_nodes, building_nodes_df], ignore_index=True
    )
    grid_data.lv_data.lv_nodes.crs = dave_settings["crs_main"]
    # update progress
    pbar.update(5)
    # --- create lines for building connections
    line_buildings = GeoSeries(
        list(
            map(
                lambda x, y: LineString([x, y]),
                building_connections["building_centroid"],
                building_connections["nearest_point"],
            )
        ),
        crs=dave_settings["crs_main"],
    )
    # calculate line length
    line_buildings = line_buildings.set_crs(dave_settings["crs_main"])
    line_buildings_3035 = line_buildings.to_crs(dave_settings["crs_meter"])
    line_gdf = GeoDataFrame(
        {
            "geometry": line_buildings,
            "line_type": "line_buildings",
            "length_km": line_buildings_3035.length / 1000,
            "voltage_kv": 0.4,
            "voltage_level": 7,
            "source": "dave internal",
        }
    )
    # write line informations into grid data
    grid_data.lv_data.lv_lines = concat([grid_data.lv_data.lv_lines, line_gdf], ignore_index=True)
    # set crs
    grid_data.lv_data.lv_lines.crs = dave_settings["crs_main"]
    # create line connections to connect lines for buildings and road junctions with each other
    line_connections(grid_data)
    # add dave name for lv_lines
    grid_data.lv_data.lv_lines.reset_index(drop=True, inplace=True)
    grid_data.lv_data.lv_lines.insert(
        0,
        "dave_name",
        Series(list(map(lambda x: f"line_7_{x}", grid_data.lv_data.lv_lines.index))),
    )
    # update progress
    pbar.update(5)
    # --- create missing road junctions to connect the lines with each other
    # get line bus names for each line and add to line data
    lv_nodes = grid_data.lv_data.lv_nodes
    # get road junctions
    road_junctions_origin = grid_data.roads.road_junctions
    for _, line in grid_data.lv_data.lv_lines.iterrows():
        road_junctions_grid = grid_data.lv_data.lv_nodes[
            grid_data.lv_data.lv_nodes.node_type == "road_junction"
        ]
        line_coords_from = line.geometry.coords[:][0]
        line_coords_to = line.geometry.coords[:][len(line.geometry.coords[:]) - 1]
        from_bus = lv_nodes[lv_nodes.geometry.x == line_coords_from[0]]
        if len(from_bus) > 1:
            from_bus = from_bus[from_bus.geometry.y == line_coords_from[1]]
        to_bus = lv_nodes[lv_nodes.geometry.x == line_coords_to[0]]
        if len(to_bus) > 1:
            to_bus = to_bus[to_bus.geometry.y == line_coords_to[1]]
        if not from_bus.empty:
            grid_data.lv_data.lv_lines.at[line.name, "from_bus"] = from_bus.iloc[0].dave_name
        else:
            # check if there is a suitable road junction in grid data
            distance = road_junctions_grid.geometry.apply(
                lambda x: Point(line_coords_from).distance(x)
            )
            if not distance.empty and distance.min() < 1e-04:
                # road junction node was found
                dave_name = road_junctions_grid.loc[distance.idxmin()].dave_name
            else:
                # no road junction was found, create it from road junction data
                distance = road_junctions_origin.geometry.apply(
                    lambda x: Point(line_coords_from).distance(x)
                )
                if distance.min() < 1e-04:
                    road_junction_geom = road_junctions_origin.loc[distance.idxmin()]
                    # create lv_point for relevant road junction
                    dave_number = int(
                        grid_data.lv_data.lv_nodes.dave_name.tail(1).iloc[0].replace("node_7_", "")
                    )
                    dave_name = "node_7_" + str(dave_number + 1)
                    junction_point_gdf = GeoDataFrame(
                        {
                            "geometry": [road_junction_geom],
                            "dave_name": dave_name,
                            "node_type": "road_junction",
                            "voltage_level": 7,
                            "voltage_kv": 0.4,
                            "source": "dave internal",
                        }
                    )
                    grid_data.lv_data.lv_nodes = concat(
                        [grid_data.lv_data.lv_nodes, junction_point_gdf], ignore_index=True
                    )
            grid_data.lv_data.lv_lines.at[line.name, "from_bus"] = dave_name
        grid_data.lv_data.lv_nodes.reset_index(drop=True, inplace=True)
        road_junctions_grid = grid_data.lv_data.lv_nodes[
            grid_data.lv_data.lv_nodes.node_type == "road_junction"
        ]
        if not to_bus.empty:
            grid_data.lv_data.lv_lines.at[line.name, "to_bus"] = to_bus.iloc[0].dave_name
        else:
            # check if there is a suitable road junction in grid data
            distance = road_junctions_grid.geometry.apply(
                lambda x: Point(line_coords_to).distance(x)
            )
            if distance.min() < 1e-04:
                # road junction node was found
                dave_name = road_junctions_grid.loc[distance.idxmin()].dave_name
            else:
                # no road junction was found, create it from road junction data
                distance = road_junctions_origin.geometry.apply(
                    lambda x: Point(line_coords_to).distance(x)
                )
                if distance.min() < 1e-04:
                    road_junction_geom = road_junctions_origin.loc[distance.idxmin()]
                    # create lv_point for relevant road junction
                    dave_number = int(
                        grid_data.lv_data.lv_nodes.dave_name.tail(1).iloc[0].replace("node_7_", "")
                    )
                    dave_name = "node_7_" + str(dave_number + 1)
                    junction_point_gdf = GeoDataFrame(
                        {
                            "geometry": [road_junction_geom],
                            "dave_name": dave_name,
                            "node_type": "road_junction",
                            "voltage_level": 7,
                            "voltage_kv": 0.4,
                            "source": "dave internal",
                        }
                    )
                    grid_data.lv_data.lv_nodes = concat(
                        [grid_data.lv_data.lv_nodes, junction_point_gdf], ignore_index=True
                    )
            grid_data.lv_data.lv_lines.at[line.name, "to_bus"] = dave_name
        grid_data.lv_data.lv_nodes.reset_index(drop=True, inplace=True)
        # set crs
        grid_data.lv_data.lv_nodes.set_crs(dave_settings["crs_main"], inplace=True)
        # update progress
        pbar.update(80 / len(grid_data.lv_data.lv_lines))
    # close progress bar
    pbar.close()
