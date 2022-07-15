# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import time

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point, Polygon
from tqdm import tqdm

from dave.datapool import (
    oep_request,
    query_osm,
    read_federal_states,
    read_nuts_regions,
    read_postal,
)
from dave.io import archiv_inventory, from_json_string
from dave.settings import dave_settings
from dave.toolbox import intersection_with_area


class target_area:
    """
    This class contains functions to define a target area and getting all relevant osm data for it

    INPUT:
        **grid_data** (attrdict) - grid_data as a attrdict in dave structure
        **power_levels** (list)  - this parameter defines which power levels should be considered
                                   options: 'ehv','hv','mv','lv', [].
                                   there could be choose: one level, multiple levels or 'ALL'
        **gas_levels** (list)    - this parameter defines which gas levels should be considered
                                   options: 'hp','mp','lp', [].
                                   there could be choose: one level, multiple levels or 'ALL'

        One of these parameters must be set:
        **postalcode** (List of strings) - numbers of the target postalcode areas.
                                           it could also be choose ['ALL'] for all postalcode areas
                                           in germany
        **town_name** (List of strings) - names of the target towns
                                          it could also be choose ['ALL'] for all citys in germany
        **federal_state** (List of strings) - names of the target federal states
                                              it could also be choose ['ALL'] for all federal states
                                              in germany
        **nuts_region** (List of strings) - codes of the target nuts regions
                                              it could also be choose ['ALL'] for all nuts regions
                                              in europe
        **own_area** (string) - full path to a shape file which includes own target area
                                (e.g. "C:/Users/name/test/test.shp") or Geodataframe as string

    OPTIONAL:
        **buffer** (float, default 0) - buffer for the target area
        **roads** (boolean, default True) - obtain informations about roads which are relevant for
                                            the grid model
        **roads_plot** (boolean, default False) - obtain informations about roads which can be nice
                                                  for the visualization
        **buildings** (boolean, default True) - obtain informations about buildings
        **landuse** (boolean, default True) - obtain informations about landuses
        **railway** (boolean, default True) - obtain informations about railways

    OUTPUT:

    EXAMPLE:
            from dave.topology import target_area
            target_area(town_name = ['Kassel'], buffer=0).target()
    """

    def __init__(
        self,
        grid_data,
        power_levels,
        gas_levels,
        postalcode=None,
        town_name=None,
        federal_state=None,
        nuts_region=None,
        own_area=None,
        buffer=0,
        roads=True,
        roads_plot=True,
        buildings=True,
        landuse=True,
        railways=True,
    ):
        # Init input parameters
        self.grid_data = grid_data
        self.postalcode = postalcode
        self.town_name = town_name
        self.federal_state = federal_state
        self.nuts_region = nuts_region
        self.own_area = own_area
        self.buffer = buffer
        self.roads = roads
        self.roads_plot = roads_plot
        self.buildings = buildings
        self.railways = railways
        self.landuse = landuse
        self.power_levels = power_levels
        self.gas_levels = gas_levels

    def _target_geom(self, target_number, target_town):
        """
        This function searches the suitable geometry for the processing step

        """
        if target_number or target_number == 0:
            target_geom = self.target.geometry.iloc[target_number]
        elif target_town:
            targets = self.target[self.target.town == target_town]
            target_geom = targets.geometry.unary_union
        return target_geom

    def _from_osm(self, target, target_number=None, target_town=None, progress_step=None):
        """
        This function searches for data on OpenStreetMap (OSM) and filters the relevant paramerters
        for grid modeling
        """
        # add time delay because osm doesn't alowed more than 1 request per second.
        time_delay = dave_settings()["osm_time_delay"]
        # count object types to consider for progress bar
        objects_list = [self.roads, self.roads_plot, self.buildings, self.landuse, self.railways]
        objects_con = len([x for x in objects_list if x is True])
        if objects_con == 0:
            # update progress
            self.pbar.update(progress_step)
        # get target geometry for the processing step
        target_geom = target_area._target_geom(self, target_number, target_town)
        # search relevant road informations in the target area
        if self.roads:
            roads, meta_data = query_osm(
                "way", target, recurse="down", tags=[dave_settings()["road_tags"]]
            )
            # add meta data
            if f"{meta_data['Main'].Titel.loc[0]}" not in self.grid_data.meta_data.keys():
                self.grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
            # check if there are data for roads
            if not roads.empty:
                # define road parameters which are relevant for the grid modeling
                roads = roads.filter(["geometry", "name", "highway"])
                # consider only the linestring elements
                roads = roads[roads.geometry.apply(lambda x: isinstance(x, LineString))]
                # consider only roads which intersects the target area
                roads = roads[roads.geometry.intersects(target_geom)]
                # write roads into grid_data
                roads.set_crs(dave_settings()["crs_main"], inplace=True)
                self.grid_data.roads.roads = pd.concat(
                    [self.grid_data.roads.roads, roads], ignore_index=True
                )
            # add time delay
            time.sleep(time_delay)
            # update progress
            self.pbar.update(progress_step / objects_con)
        # search irrelevant road informations in the target area for a better overview
        if self.roads_plot:
            roads_plot, meta_data = query_osm(
                "way", target, recurse="down", tags=[dave_settings()["road_plot_tags"]]
            )
            # add meta data
            if f"{meta_data['Main'].Titel.loc[0]}" not in self.grid_data.meta_data.keys():
                self.grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
            # check if there are data for roads_plot
            if not roads_plot.empty:
                # define road parameters which are relevant for the grid modeling
                roads_plot = roads_plot.filter(["geometry", "name"])
                # consider only the linestring elements
                roads_plot = roads_plot[
                    roads_plot.geometry.apply(lambda x: isinstance(x, LineString))
                ]
                # consider only roads which intersects the target area
                roads_plot = roads_plot[roads_plot.geometry.intersects(target_geom)]
                # write plotting roads into grid_data
                roads_plot.set_crs(dave_settings()["crs_main"], inplace=True)
                self.grid_data.roads.roads_plot = pd.concat(
                    [self.grid_data.roads.roads_plot, roads_plot], ignore_index=True
                )
            # add time delay
            time.sleep(time_delay)
            # update progress
            self.pbar.update(progress_step / objects_con)
        # search landuse informations in the target area
        if self.landuse:
            landuse, meta_data = query_osm(
                "way", target, recurse="down", tags=[dave_settings()["landuse_tags"]]
            )
            # add meta data
            if f"{meta_data['Main'].Titel.loc[0]}" not in self.grid_data.meta_data.keys():
                self.grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
            # check additionally osm relations
            landuse_rel, meta_data = query_osm(
                "relation", target, recurse="down", tags=[dave_settings()["landuse_tags"]]
            )
            # add landuses from relations to landuses from ways
            landuse = pd.concat([landuse, landuse_rel], ignore_index=True)
            # check if there are data for landuse
            if not landuse.empty:
                # define landuse parameters which are relevant for the grid modeling
                landuse = landuse.filter(["landuse", "geometry", "name"])
                # consider only the linestring elements
                landuse = landuse[landuse.geometry.apply(lambda x: isinstance(x, LineString))]
                # consider only landuses which intersects the target area
                landuse = landuse[landuse.geometry.intersects(target_geom)]
                # convert geometry to polygon
                for i, land in landuse.iterrows():
                    if isinstance(land.geometry, LineString):
                        # A LinearRing must have at least 3 coordinate tuples
                        if len(land.geometry.coords[:]) >= 3:
                            landuse.at[land.name, "geometry"] = Polygon(land.geometry)
                        else:
                            landuse = landuse.drop([land.name])
                    elif isinstance(land.geometry, Point):
                        # delet landuse if geometry is a point
                        landuse = landuse.drop([land.name])
                # intersect landuses with the target area
                landuse = landuse.set_crs(dave_settings()["crs_main"])
                area = self.grid_data.area.rename(columns={"name": "bundesland"})
                # filter landuses which are within the grid area
                landuse = intersection_with_area(landuse, area)
                # calculate polygon area in km²
                landuse_3035 = landuse.to_crs(dave_settings()["crs_meter"])
                landuse["area_km2"] = landuse_3035.area / 1e06
                # write landuse into grid_data
                self.grid_data.landuse = pd.concat(
                    [self.grid_data.landuse, landuse], ignore_index=True
                )
                self.grid_data.landuse.set_crs(dave_settings()["crs_main"], inplace=True)
            # add time delay
            time.sleep(time_delay)
            # update progress
            self.pbar.update(progress_step / objects_con)
        # search building informations in the target area
        if self.buildings:
            buildings, meta_data = query_osm(
                "way", target, recurse="down", tags=[dave_settings()["building_tags"]]
            )
            # add meta data
            if f"{meta_data['Main'].Titel.loc[0]}" not in self.grid_data.meta_data.keys():
                self.grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
            # check if there are data for buildings
            if not buildings.empty:
                # define building parameters which are relevant for the grid modeling
                buildings = buildings.filter(
                    [
                        "addr:housenumber",
                        "addr:street",
                        "addr:suburb",
                        "amenity",
                        "building",
                        "building:levels",
                        "geometry",
                        "name",
                    ]
                )
                # consider only the linestring elements
                buildings = buildings[buildings.geometry.apply(lambda x: isinstance(x, LineString))]
                # consider only buildings which intersects the target area
                buildings = buildings[buildings.geometry.intersects(target_geom)]
                # create building categories
                residential = dave_settings()["buildings_residential"]
                commercial = dave_settings()["buildings_commercial"]
                # improve building tag with landuse parameter
                if self.landuse and not landuse.empty:
                    landuse_retail = landuse[landuse.landuse == "retail"].geometry.unary_union
                    landuse_industrial = landuse[
                        landuse.landuse == "industrial"
                    ].geometry.unary_union
                    landuse_commercial = landuse[
                        landuse.landuse == "commercial"
                    ].geometry.unary_union
                    for i, building in buildings.iterrows():
                        if building.building not in commercial:
                            if building.geometry.intersects(landuse_retail):
                                buildings.at[i, "building"] = "retail"
                            elif building.geometry.intersects(landuse_industrial):
                                buildings.at[i, "building"] = "industrial"
                            elif building.geometry.intersects(landuse_commercial):
                                buildings.at[i, "building"] = "commercial"
                # write buildings into grid_data
                buildings.set_crs(dave_settings()["crs_main"], inplace=True)
                self.grid_data.buildings.residential = pd.concat(
                    [
                        self.grid_data.buildings.residential,
                        buildings[buildings.building.isin(residential)],
                    ],
                    ignore_index=True,
                )
                self.grid_data.buildings.commercial = pd.concat(
                    [
                        self.grid_data.buildings.commercial,
                        buildings[buildings.building.isin(commercial)],
                    ],
                    ignore_index=True,
                )
                self.grid_data.buildings.other = pd.concat(
                    [
                        self.grid_data.buildings.other,
                        buildings[~buildings.building.isin(residential + commercial)],
                    ],
                    ignore_index=True,
                )
            # add time delay
            time.sleep(time_delay)
            # update progress
            self.pbar.update(progress_step / objects_con)
        # search railway informations in the target area
        if self.railways:
            railways, meta_data = query_osm(
                "way", target, recurse="down", tags=[dave_settings()["railway_tags"]]
            )
            # add meta data
            if f"{meta_data['Main'].Titel.loc[0]}" not in self.grid_data.meta_data.keys():
                self.grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
            # check if there are data for roads
            if not railways.empty:
                # define road parameters which are relevant for the grid modeling
                railways = railways.filter(
                    ["name", "railway", "geometry", "tram", "train", "usage", "voltage"]
                )
                # consider only the linestring elements
                railways = railways[railways.geometry.apply(lambda x: isinstance(x, LineString))]
                # consider only roads which intersects the target area
                railways = railways[railways.geometry.intersects(target_geom)]
                # write roads into grid_data
                railways.set_crs(dave_settings()["crs_main"], inplace=True)
                self.grid_data.railways = pd.concat(
                    [self.grid_data.railways, railways], ignore_index=True
                )
            # add time delay
            time.sleep(time_delay)
            # update progress
            self.pbar.update(progress_step / objects_con)

    def road_junctions(self):
        """
        This function searches junctions for the relevant roads in the target area
        """
        roads = self.grid_data.roads.roads.copy(deep=True)
        if not roads.empty:
            junction_points = []
            while len(roads) > 1:
                # considered line
                line_geometry = roads.iloc[0].geometry
                # check considered line surrounding for possible intersectionpoints with other lines
                lines_rel = roads[roads.geometry.crosses(line_geometry.buffer(1e-04))]
                other_lines = lines_rel.geometry.unary_union
                # find line intersections between considered line and other lines
                junctions = line_geometry.intersection(other_lines)
                if junctions.geom_type == "Point":
                    junction_points.append(junctions)
                elif junctions.geom_type == "MultiPoint":
                    for point in junctions.geoms:
                        junction_points.append(point)
                # set new roads quantity for the next iterationstep
                roads.drop([0], inplace=True)
                roads.reset_index(drop=True, inplace=True)
            # delet duplicates
            junction_points = gpd.GeoSeries(junction_points)
            road_junctions = junction_points.drop_duplicates()
            # write road junctions into grid_data
            road_junctions.set_crs(dave_settings()["crs_main"], inplace=True)
            self.grid_data.roads.road_junctions = road_junctions.rename("geometry")

    def _target_by_postalcode(self):
        """
        This function filter the postalcode informations for the target area.
        Multiple postalcode areas will be combinated.
        """
        postal, meta_data = read_postal()
        # add meta data
        if f"{meta_data['Main'].Titel.loc[0]}" not in self.grid_data.meta_data.keys():
            self.grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        if len(self.postalcode) == 1 and self.postalcode[0].lower() == "all":
            # in this case all postalcode areas will be choosen
            target = postal
        else:
            for i, plz in enumerate(self.postalcode):
                target = (
                    postal[postal.postalcode == plz]
                    if i == 0
                    else pd.concat([target, postal[postal.postalcode == plz]], ignore_index=True)
                )
            # sort federal state names
            self.postalcode.sort()
        self.target = target

    def _own_area_postal(self):
        """
        This functions searches for the postal codes which intersects with the own area
        """
        postal, meta_data = read_postal()
        # add meta data
        if f"{meta_data['Main'].Titel.loc[0]}" not in self.grid_data.meta_data.keys():
            self.grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        # filter postal code areas which are within the target area
        postal_intersection = intersection_with_area(postal, self.target, remove_columns=False)
        # filter duplicated postal codes
        self.own_postal = postal_intersection["postalcode"].unique().tolist()

    def _target_by_town_name(self):
        """
        This function filter the postalcode informations for the target area.
        Multiple town name areas will be combinated
        """
        postal, meta_data = read_postal()
        # add meta data
        if f"{meta_data['Main'].Titel.loc[0]}" not in self.grid_data.meta_data.keys():
            self.grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        if len(self.town_name) == 1 and self.town_name[0].lower() == "all":
            # in this case all city names will be choosen (same case as all postalcode areas)
            target = postal
        else:
            names_right = []
            for i, town in enumerate(self.town_name):
                town_name = town.capitalize()
                target = (
                    postal[postal.town == town_name]
                    if i == 0
                    else target.append(postal[postal.town == town_name])
                )
                names_right.append(town_name)
                if target.empty:
                    raise ValueError("town name wasn`t found. Please check your input")
            # sort federal state names
            names_right.sort()
            self.town_name = names_right
        self.target = target

    def _target_by_federal_state(self):
        """
        This function filter the federal state informations for the target area.
        Multiple federal state areas will be combinated.
        """
        states, meta_data = read_federal_states()
        # add meta data
        if f"{meta_data['Main'].Titel.loc[0]}" not in self.grid_data.meta_data.keys():
            self.grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        if len(self.federal_state) == 1 and self.federal_state[0].lower() == "all":
            # in this case all federal states will be choosen
            target = states
        else:
            names_right = []
            for state in self.federal_state:
                # bring name in right format
                state_name = state.split("-")
                if len(state_name) == 1:
                    state_name = state_name[0].capitalize()
                else:
                    state_name = state_name[0].capitalize() + "-" + state_name[1].capitalize()
                names_right.append(state_name)
                if self.federal_state[0] == state:
                    target = states[states["name"] == state_name]
                else:
                    target = pd.concat(
                        [target, states[states["name"] == state_name]], ignore_index=True
                    )
                if target.empty:
                    raise ValueError("federal state name wasn`t found. Please check your input")
            # sort federal state names
            names_right.sort()
            self.federal_state = names_right
        self.target = target
        # convert federal states into postal code areas for target_input
        postal, meta_data = read_postal()
        # add meta data
        if f"{meta_data['Main'].Titel.loc[0]}" not in self.grid_data.meta_data.keys():
            self.grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        # filter postal code areas which are within the target area
        postal_intersection = intersection_with_area(postal, self.target, remove_columns=False)
        # filter duplicated postal codes
        self.federal_state_postal = postal_intersection["postalcode"].unique().tolist()

    def _target_by_nuts_region(self):
        """
        This function filter the nuts region informations for the target area.
        """
        # check user input
        if isinstance(self.nuts_region, list):
            self.nuts_region = (self.nuts_region, "2016")  # default year
        # request nuts-3 areas from oep
        nuts, meta_data = read_nuts_regions(year=self.nuts_region[1])
        nuts_3 = nuts[nuts.LEVL_CODE == 3]
        # add meta data
        if f"{meta_data['Main'].Titel.loc[0]}" not in self.grid_data.meta_data.keys():
            self.grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        if len(self.nuts_region[0]) == 1 and self.nuts_region[0][0].lower() == "all":
            # in this case all nuts_regions will be choosen
            self.target = nuts_3
        else:
            for i, region in enumerate(self.nuts_region[0]):
                # bring NUTS ID in right format
                region_letters = list(region)
                region_renamed = "".join(
                    [letter.upper() if letter.isalpha() else letter for letter in region_letters]
                )
                self.nuts_region[0][i] = region_renamed
                # get area for nuts region
                nuts_contains = nuts_3[nuts_3["NUTS_ID"].str.contains(region_renamed)]
                self.target = (
                    nuts_contains
                    if i == 0
                    else pd.concat([self.target, nuts_contains], ignore_index=True)
                )
                if nuts_contains.empty:
                    raise ValueError("nuts region name wasn`t found. Please check your input")
        # filter duplicates
        self.target.drop_duplicates(inplace=True)
        # merge multipolygons
        # target['geometry'] = target.geometry.apply(lambda x: unary_union(x))
        # convert nuts regions into postal code areas for target_input
        postal, meta_data = read_postal()
        # add meta data
        if f"{meta_data['Main'].Titel.loc[0]}" not in self.grid_data.meta_data.keys():
            self.grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        # filter postal code areas which are within the target area
        postal_intersection = intersection_with_area(postal, self.target, remove_columns=False)
        # filter duplicated postal codes
        self.nuts_region_postal = postal_intersection["postalcode"].unique().tolist()

    def target(self):
        """
        This function calculate all relevant geographical informations for the
        target area and add it to the grid_data
        """
        # set progress bar
        self.pbar = tqdm(
            total=100,
            desc="collect geographical data:         ",
            position=0,
            bar_format=dave_settings()["bar_format"],
        )
        # check wich input parameter is given
        if self.postalcode:
            target_area._target_by_postalcode(self)
            target_input = pd.DataFrame(
                {
                    "typ": "postalcode",
                    "data": [self.postalcode],
                    "power_levels": [self.power_levels],
                    "gas_levels": [self.gas_levels],
                }
            )
            self.grid_data.target_input = target_input
        elif self.town_name:
            target_area._target_by_town_name(self)
            target_input = pd.DataFrame(
                {
                    "typ": "town name",
                    "data": [self.town_name],
                    "power_levels": [self.power_levels],
                    "gas_levels": [self.gas_levels],
                }
            )
            self.grid_data.target_input = target_input
        elif self.federal_state:
            target_area._target_by_federal_state(self)
            target_input = pd.DataFrame(
                {
                    "typ": "federal state",
                    "federal_states": [self.federal_state],
                    "data": [self.federal_state_postal],
                    "power_levels": [self.power_levels],
                    "gas_levels": [self.gas_levels],
                }
            )
            self.grid_data.target_input = target_input
        elif self.nuts_region:
            target_area._target_by_nuts_region(self)
            target_input = pd.DataFrame(
                {
                    "typ": "nuts region",
                    "nuts_regions": [self.nuts_region],
                    "data": [self.nuts_region_postal],
                    "power_levels": [self.power_levels],
                    "gas_levels": [self.gas_levels],
                }
            )
            self.grid_data.target_input = target_input
        elif self.own_area:
            if self.own_area[-3:] == "shp":
                self.target = gpd.read_file(self.own_area)
            else:
                self.target = from_json_string(self.own_area)
            # check crs and project to the right one if needed
            if (self.target.crs) and (self.target.crs != dave_settings()["crs_main"]):
                self.target = self.target.to_crs(dave_settings()["crs_main"])
            if "id" in self.target.keys():
                self.target = self.target.drop(columns=["id"])
            target_area._own_area_postal(self)
            target_input = pd.DataFrame(
                {
                    "typ": "own area",
                    "data": [self.own_postal],
                    "power_levels": [self.power_levels],
                    "gas_levels": [self.gas_levels],
                }
            )
            self.grid_data.target_input = target_input
        else:
            raise SyntaxError("target area wasn`t defined")
        # write area informations into grid_data
        self.grid_data.area = pd.concat([self.grid_data.area, self.target], ignore_index=True)
        if self.grid_data.area.crs is None:
            self.grid_data.area.set_crs(dave_settings()["crs_main"], inplace=True)
        elif self.grid_data.area.crs != dave_settings()["crs_main"]:
            self.grid_data.area.to_crs(dave_settings()["crs_main"], inplace=True)
        # check if requested model is already in the archiv
        if not self.grid_data.target_input.iloc[0].typ == "own area":
            file_exists, file_name = archiv_inventory(self.grid_data, read_only=True)
        else:
            file_exists, file_name = False, "None"
        # update progress
        self.pbar.update(float(10))
        if not file_exists:
            # create borders for target area, load osm-data and write into grid data
            if self.town_name:
                diff_targets = self.target["town"].drop_duplicates()
                # define progress step
                progress_step = 80 / len(diff_targets)
                for diff_target in diff_targets:
                    town = self.target[self.target.town == diff_target]
                    border = (
                        town.geometry.unary_union.convex_hull
                        if len(town) > 1
                        else town.iloc[0].geometry.convex_hull
                    )
                    # Obtain data from OSM
                    target_area._from_osm(
                        self, target=border, target_town=diff_target, progress_step=progress_step
                    )
            else:
                for i in range(0, len(self.target)):
                    # define progress step
                    progress_step = 80 / len(self.target)
                    border = self.target.iloc[i].geometry.convex_hull
                    # Obtain data from OSM
                    target_area._from_osm(
                        self, target=border, target_number=i, progress_step=progress_step
                    )
            # reset index for all osm data
            self.grid_data.roads.roads.reset_index(drop=True, inplace=True)
            self.grid_data.roads.roads_plot.reset_index(drop=True, inplace=True)
            self.grid_data.landuse.reset_index(drop=True, inplace=True)
            self.grid_data.buildings.residential.reset_index(drop=True, inplace=True)
            self.grid_data.buildings.commercial.reset_index(drop=True, inplace=True)
            # find road junctions
            if "lv" in self.grid_data.target_input.power_levels[0]:
                target_area.road_junctions(self)
            # close progress bar
            self.pbar.update(float(10))
            self.pbar.close()
            return file_exists, file_name
        else:
            # close progress bar
            self.pbar.update(float(90))
            self.pbar.close()
            return file_exists, file_name
