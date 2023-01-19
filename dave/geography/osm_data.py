# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point, Polygon

from dave.datapool.osm_request import osm_request
from dave.settings import dave_settings
from dave.toolbox import intersection_with_area


def get_osm_data(grid_data, key, border, target_geom):
    """
    This function requests data from osm and filter it

    INPUT:

        **grid_data** (string) - DAVE data dictionary
        **key** (string) - name of the object type which should be considered
        **border** (geometrie) - border for the data consideration
        **target_geom** (geometrie) - geometry of the considerd target
    """
    data, meta_data = osm_request(data_type=key, area=border)
    # add meta data
    if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
        grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
    # check if there are data
    if not data.empty:
        # filter data parameters which are relevant for the grid modeling
        data = data.filter(dave_settings()["osm_tags"][key][3])
        data.rename(columns={"id": "osm_id"}, inplace=True)
        # consider only data which are linestring elements and within considered area
        data = data[
            (data.geometry.apply(lambda x: isinstance(x, LineString)))
            & (data.geometry.intersects(target_geom))
        ]
        data.set_crs(dave_settings()["crs_main"], inplace=True)
    return data


def from_osm(
    grid_data,
    pbar,
    roads,
    roads_plot,
    buildings,
    landuse,
    railways,
    waterways,
    target_geom,
    progress_step=None,
):
    """
    This function searches for data on OpenStreetMap (OSM) and filters the relevant paramerters
    for grid modeling

    target = geometry of the considerd target
    """
    # count object types to consider for progress bar
    objects_list = [roads, roads_plot, buildings, landuse, railways, waterways]
    objects_con = len([x for x in objects_list if x is True])
    if objects_con == 0:
        # update progress
        pbar.update(progress_step)
    # create border for osm query
    border = target_geom.convex_hull
    # search relevant road informations in the target area
    if roads:
        roads = get_osm_data(grid_data, "road", border, target_geom)
        grid_data.roads.roads = pd.concat([grid_data.roads.roads, roads], ignore_index=True)
        # update progress
        pbar.update(progress_step / objects_con)
    # search irrelevant road informations in the target area for a better overview
    if roads_plot:
        roads_plot = get_osm_data(grid_data, "road_plot", border, target_geom)
        grid_data.roads.roads_plot = pd.concat(
            [grid_data.roads.roads_plot, roads_plot], ignore_index=True
        )
        # update progress
        pbar.update(progress_step / objects_con)
    # search landuse informations in the target area
    if landuse:
        landuse = get_osm_data(grid_data, "landuse", border, target_geom)
        # check if there are data for landuse
        if not landuse.empty:
            # convert geometry to polygon
            for i, land in landuse.iterrows():
                if isinstance(land.geometry, LineString):
                    # A LinearRing must have at least 3 coordinate tuples
                    if len(land.geometry.coords[:]) >= 3:
                        landuse.at[land.name, "geometry"] = Polygon(land.geometry)
                    else:
                        landuse.drop([land.name], inplace=True)
                elif isinstance(land.geometry, Point):
                    # delet landuse if geometry is a point
                    landuse.drop([land.name], inplace=True)
            # intersect landuses with the target area
            area = grid_data.area.rename(columns={"name": "bundesland"})
            # filter landuses which are within the grid area
            landuse = intersection_with_area(
                landuse, area
            )  # !!! duplicated with intersection before?
            # calculate polygon area in km²
            landuse_3035 = landuse.to_crs(dave_settings()["crs_meter"])
            landuse["area_km2"] = landuse_3035.area / 1e06
            # write landuse into grid_data
            grid_data.landuse = pd.concat([grid_data.landuse, landuse], ignore_index=True)
            grid_data.landuse.set_crs(dave_settings()["crs_main"], inplace=True)
        # update progress
        pbar.update(progress_step / objects_con)
    # search building informations in the target area
    if buildings:
        buildings = get_osm_data(grid_data, "building", border, target_geom)
        # check if there are data for buildings
        if not buildings.empty:
            # create building categories
            residential = dave_settings()["buildings_residential"]
            commercial = dave_settings()["buildings_commercial"]
            # improve building tag with landuse parameter
            if landuse if isinstance(landuse, bool) else not landuse.empty:
                landuse_retail = landuse[landuse.landuse == "retail"].geometry.unary_union
                landuse_industrial = landuse[landuse.landuse == "industrial"].geometry.unary_union
                landuse_commercial = landuse[landuse.landuse == "commercial"].geometry.unary_union
                for i, building in buildings.iterrows():
                    if building.building not in commercial:
                        if not landuse_retail is None and building.geometry.intersects(
                            landuse_retail
                        ):
                            buildings.at[i, "building"] = "retail"
                        elif not landuse_industrial is None and building.geometry.intersects(
                            landuse_industrial
                        ):
                            buildings.at[i, "building"] = "industrial"
                        elif not landuse_commercial is None and building.geometry.intersects(
                            landuse_commercial
                        ):
                            buildings.at[i, "building"] = "commercial"
            # write buildings into grid_data
            grid_data.buildings.residential = pd.concat(
                [
                    grid_data.buildings.residential,
                    buildings[buildings.building.isin(residential)],
                ],
                ignore_index=True,
            )
            grid_data.buildings.commercial = pd.concat(
                [
                    grid_data.buildings.commercial,
                    buildings[buildings.building.isin(commercial)],
                ],
                ignore_index=True,
            )
            grid_data.buildings.other = pd.concat(
                [
                    grid_data.buildings.other,
                    buildings[~buildings.building.isin(residential + commercial)],
                ],
                ignore_index=True,
            )
        # update progress
        pbar.update(progress_step / objects_con)
    # search railway informations in the target area
    if railways:
        railways = get_osm_data(grid_data, "railway", border, target_geom)
        grid_data.railways = pd.concat([grid_data.railways, railways], ignore_index=True)
        # update progress
        pbar.update(progress_step / objects_con)
    # search waterway informations in the target area
    if waterways:
        waterways = get_osm_data(grid_data, "waterway", border, target_geom)
        grid_data.waterways = pd.concat([grid_data.waterways, waterways], ignore_index=True)
        # update progress
        pbar.update(progress_step / objects_con)


def road_junctions(grid_data):
    """
    This function searches junctions for the relevant roads in the target area
    """
    roads = grid_data.roads.roads.copy(deep=True)
    if not roads.empty:
        junction_points = []
        while len(roads) > 1:
            # considered line
            line_geometry = roads.iloc[0].geometry
            # check considered line surrounding for possible intersectionpoints with other lines
            lines_cross = roads[roads.geometry.crosses(line_geometry.buffer(1e-04))]
            if not lines_cross.empty:
                other_lines = lines_cross.geometry.unary_union
                # find line intersections between considered line and other lines
                line_junctions = line_geometry.intersection(other_lines)
                if line_junctions.geom_type == "Point":
                    junction_points.append(line_junctions)
                elif line_junctions.geom_type == "MultiPoint":
                    for point in line_junctions.geoms:
                        junction_points.append(point)
            # set new roads quantity for the next iterationstep
            roads.drop([0], inplace=True)
            roads.reset_index(drop=True, inplace=True)
        # delet duplicates
        junctions = gpd.GeoSeries(junction_points).drop_duplicates()
        # write road junctions into grid_data
        junctions.set_crs(dave_settings()["crs_main"], inplace=True)
        grid_data.roads.road_junctions = junctions.rename("geometry")
