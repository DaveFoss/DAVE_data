# Copyright (c) 2022-2023 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import warnings
from math import acos, sin

import geopandas as gpd
import pandas as pd
from numpy import array, random
from shapely.geometry import LineString, MultiLineString, Polygon
from shapely.ops import polygonize, unary_union
from tqdm import tqdm

from dave.datapool.osm_request import query_osm
from dave.datapool.read_data import read_federal_states, read_household_consumption, read_postal
from dave.settings import dave_settings
from dave.toolbox import intersection_with_area, voronoi


def get_household_power(consumption_data, household_size):
    """
    This function calculates the active and reactive power consumption for a given houshold size
    based on the consumption data for a year

    INPUT:
        **consumption_data** (Dict) - consumption data for germany from dave internal datapool
        **household_size** (int) - size of the houshold between 1 and 5 person
    """
    # set power factor
    household_consumption = consumption_data["household_consumptions"][
        consumption_data["household_consumptions"]["Personen pro Haushalt"] == household_size
    ]
    p_mw = (household_consumption.iloc[0]["Durchschnitt  [kwh/a]"] / 1000) / dave_settings()[
        "h_per_a"
    ]
    q_mvar = (
        p_mw
        * sin(acos(dave_settings()["cos_phi_residential"]))
        / dave_settings()["cos_phi_residential"]
    )
    return p_mw, q_mvar


def create_loads(grid_data):
    """
    This function creates loads by osm landuse polygons in the target area an assigne them to a
    suitable node on the considered voltage level by voronoi analysis
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create electrical loads:           ",
        position=0,
        bar_format=dave_settings()["bar_format"],
    )
    # define avarage load values
    residential_load = dave_settings()["residential_load"]
    industrial_load = dave_settings()["industrial_load"]
    commercial_load = dave_settings()["commercial_load"]
    # set power factor for loads
    cos_phi_residential = dave_settings()["cos_phi_residential"]
    cos_phi_industrial = dave_settings()["cos_phi_industrial"]
    cos_phi_commercial = dave_settings()["cos_phi_commercial"]
    # define power_levels
    power_levels = grid_data.target_input.power_levels[0]
    # create loads on grid level 7 (LV)
    if "lv" in power_levels and not grid_data.lv_data.lv_nodes.empty:
        # get lv building nodes
        building_nodes = grid_data.lv_data.lv_nodes[
            grid_data.lv_data.lv_nodes.node_type == "building_connection"
        ]
        # --- create lv loads for residential
        federal_states, meta_data = read_federal_states()
        # add meta data
        if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
            grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        federal_states.rename(columns={"name": "federal state"}, inplace=True)
        # intersect residential buildings with federal state areas to get the suitable federal state
        buildings_feds = intersection_with_area(
            grid_data.buildings.residential, federal_states, remove_columns=False
        )
        buildings_feds.drop(
            columns=federal_states.keys().drop("federal state").drop("geometry"), inplace=True
        )
        # read consumption data
        consumption_data, meta_data = read_household_consumption()
        # update progress
        pbar.update(10)
        # add meta data
        if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
            grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        # get population for the diffrent areas
        if grid_data.target_input.iloc[0].typ in ["postalcode", "town name", "federal state"]:
            population_area = grid_data.area
        else:
            # --- Case for own shape as input data
            # calculate proportions of postal area for grid area
            postals, meta_data = read_postal()
            # add meta data
            if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
                grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
            # filter postal code areas which are within the grid area
            postal_own_intersection = intersection_with_area(
                postals, grid_data.area, remove_columns=False
            )
            postal_own_intersection.rename(
                columns={"population": "population_origin"}, inplace=True
            )
            # filter landuses which are within postal code areas
            postal_own_landuse = intersection_with_area(
                grid_data.landuse, postal_own_intersection, remove_columns=False
            )
            for i, postal in postal_own_intersection.iterrows():
                # --- calculate full plz residential area
                border = (
                    postals[postals.postalcode == postal.postalcode].iloc[0].geometry.convex_hull
                )
                # Obtain data from OSM
                plz_residential, meta_data = query_osm(
                    "way", border, recurse="down", tags=['landuse~"residential"']
                )  # !!! nicht sowieso in landuse enthalten?
                # add meta data
                if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
                    grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
                # filter non Linestring objects
                drop_objects = [
                    obj.name
                    for j, obj in plz_residential.iterrows()
                    if not isinstance(obj.geometry, LineString)
                ]
                plz_residential.drop(drop_objects, inplace=True)
                plz_residential = unary_union(
                    list(polygonize(plz_residential.geometry))
                )  # !!! replace unary union function
                # calculate plz  residential area for grid area
                plz_own_landuse = postal_own_landuse[
                    postal_own_landuse.postalcode == postal.postalcode
                ]
                plz_own_residential = plz_own_landuse[plz_own_landuse.landuse == "residential"]
                plz_own_residential = plz_own_residential.geometry.unary_union
                # calculate population for proportion of postal area
                pop_own = (
                    plz_own_residential.area / plz_residential.area
                ) * postal.population_origin
                postal_own_intersection.at[i, "population"] = round(pop_own)
            population_area = postal_own_intersection
        # update progress
        pbar.update(10)
        for i, area in population_area.iterrows():
            if area.population != 0:
                # filter buildings for considered area
                buildings_area = buildings_feds[buildings_feds.geometry.within(area.geometry)]
                buildings_idx_first = buildings_area.index.to_list()  # this will be reduced later
                federal_state = buildings_area.iloc[0]["federal state"]
                household_sizes = consumption_data["household_sizes"]
                sizes_feds = household_sizes[household_sizes.Bundesland == federal_state].iloc[0]
                # household weights for considered federal state
                w_1p = sizes_feds["Anteil 1 Person [%]"] / 100
                w_2p = sizes_feds["Anteil 2 Personen [%]"] / 100
                w_3p = sizes_feds["Anteil 3 Personen [%]"] / 100
                w_4p = sizes_feds["Anteil 4 Personen [%]"] / 100
                w_5p = sizes_feds["Anteil 5 Personen und mehr [%]"] / 100
                # distribute the whole population over the considered area
                pop_distribute = area.population
                # construct random generator
                rng = random.default_rng()
                while pop_distribute != 0:
                    if pop_distribute > 5:
                        # select houshold size, weighted randomly
                        household_size = rng.choice(
                            [1, 2, 3, 4, 5], 1, p=[w_1p, w_2p, w_3p, w_4p, w_5p]
                        )[0]
                    else:
                        # selcet  the rest of population
                        household_size = pop_distribute
                    # get power values for household
                    p_mw, q_mvar = get_household_power(consumption_data, household_size)
                    # reduce population to distribute
                    pop_distribute -= household_size
                    # --- select building in grid area
                    # first every building needs a load
                    if len(buildings_idx_first) != 0:
                        building_idx = buildings_idx_first[0]
                        buildings_idx_first.remove(building_idx)
                    # distribution for the rest loads makes no matter so selected randomly
                    else:
                        building_idx = rng.choice(buildings_area.index.to_list(), 1)[0]
                    # search for suitable grid node
                    building_boundary = buildings_area.loc[building_idx].geometry
                    if isinstance(building_boundary, LineString):
                        building_geom = Polygon(building_boundary)
                    elif isinstance(building_boundary, MultiLineString):
                        multiline_coords = []
                        for line in building_boundary.geoms:
                            multiline_coords.extend([coords for coords in list(line.coords)])
                        building_geom = Polygon(multiline_coords)

                    building_node = building_nodes[building_nodes.geometry.within(building_geom)]
                    if not building_node.empty:
                        lv_node = building_node.iloc[0]
                    else:
                        # check the case that the building centroid is outside building boundary
                        building_centroid = building_geom.centroid
                        centroid_distance = building_nodes.geometry.apply(
                            lambda x: building_centroid.distance(x)
                        )
                        if centroid_distance.min() < 1e-04:
                            lv_node = building_nodes.loc[centroid_distance.idxmin()]
                    # create residential load
                    load_df = gpd.GeoDataFrame(
                        {
                            "bus": lv_node.dave_name,
                            "p_mw": p_mw,
                            "q_mvar": q_mvar,
                            "landuse": "residential",
                            "voltage_level": [7],
                            "geometry": lv_node.geometry,
                        }
                    )
                    grid_data.components_power.loads = pd.concat(
                        [grid_data.components_power.loads, load_df], ignore_index=True
                    )
            # update progress
            pbar.update(40 / len(population_area))
        # create lv loads for industrial
        industrial_polygons = grid_data.landuse[grid_data.landuse.landuse == "industrial"]
        industrial_load_full = industrial_polygons.area_km2.sum() * industrial_load  # in MW
        industrial_buildings = grid_data.buildings.commercial[
            grid_data.buildings.commercial.building == "industrial"
        ]
        industrial_polygons_sum = unary_union(
            array(list(polygonize(industrial_buildings.geometry)))
        )  # !!! replace unary union function
        industrial_area_full = industrial_polygons_sum.area
        for i, industrial_poly in industrial_buildings.iterrows():
            building_poly = list(polygonize(industrial_poly.geometry))[0]
            # check for builing bus for load connection
            building_point = grid_data.lv_data.lv_nodes[
                grid_data.lv_data.lv_nodes.geometry.within(building_poly)
            ]
            if not building_point.empty:
                if p_mw != 0:
                    load_df = gpd.GeoDataFrame(
                        {
                            "bus": building_point.iloc[0].dave_name,
                            "p_mw": industrial_load_full
                            * (building_poly.area / industrial_area_full),
                            "q_mvar": p_mw * sin(acos(cos_phi_industrial)) / cos_phi_industrial,
                            "landuse": "industrial",
                            "voltage_level": [7],
                            "geometry": building_point.iloc[0].geometry,
                        }
                    )
                    grid_data.components_power.loads = pd.concat(
                        [grid_data.components_power.loads, load_df], ignore_index=True
                    )
            # update progress
            pbar.update(20 / len(industrial_buildings))
        # create lv loads for commercial
        commercial_polygons = grid_data.landuse[grid_data.landuse.landuse == "commercial"]
        commercial_load_full = commercial_polygons.area_km2.sum() * commercial_load  # in MW
        commercial_buildings = grid_data.buildings.commercial[
            grid_data.buildings.commercial.building != "industrial"
        ]
        commercial_polygons_sum = unary_union(
            array(list(polygonize(commercial_buildings.geometry)))
        )
        commercial_area_full = commercial_polygons_sum.area
        for i, commercial_poly in commercial_buildings.iterrows():
            building_poly = list(polygonize(commercial_poly.geometry))[0]
            # check for builing bus for load connection
            building_point = grid_data.lv_data.lv_nodes[
                grid_data.lv_data.lv_nodes.geometry.within(building_poly)
            ]
            if not building_point.empty:
                if p_mw != 0:
                    load_df = gpd.GeoDataFrame(
                        {
                            "bus": building_point.iloc[0].dave_name,
                            "p_mw": commercial_load_full
                            * (building_poly.area / commercial_area_full),
                            "q_mvar": p_mw * sin(acos(cos_phi_commercial)) / cos_phi_commercial,
                            "landuse": "commercial",
                            "voltage_level": [7],
                            "geometry": building_point.iloc[0].geometry,
                        }
                    )
                    grid_data.components_power.loads = pd.concat(
                        [grid_data.components_power.loads, load_df], ignore_index=True
                    )
            # update progress
            pbar.update(19.8 / len(commercial_buildings))
    # create loads for non grid level 7
    elif any(map(lambda x: x in power_levels, ["ehv", "hv", "mv"])) and not (
        grid_data.components_power.transformers.ehv_hv.empty
        and grid_data.components_power.transformers.hv_mv.empty
        and grid_data.components_power.transformers.mv_lv.empty
    ):
        # create loads on grid level 6 (MV/LV)
        if "mv" in power_levels:
            # In this case the loads are assigned to the nearest mv/lv-transformer
            voronoi_polygons = voronoi(
                grid_data.components_power.transformers.mv_lv[["dave_name", "geometry"]]
            )
            trafos = grid_data.components_power.transformers.mv_lv
            voltage_level = 6
        # create loads on grid level 4 (HV/MV)
        elif "hv" in power_levels:
            # In this case the loads are assigned to the nearest hv/mv-transformer
            voronoi_polygons = voronoi(
                grid_data.components_power.transformers.hv_mv[["dave_name", "geometry"]]
            )
            trafos = grid_data.components_power.transformers.hv_mv
            voltage_level = 4
        # create loads on grid level 2 (EHV/HV)
        elif "ehv" in power_levels:
            # In this case the loads are assigned to the nearest ehv/hv-transformer
            voronoi_polygons = voronoi(
                grid_data.components_power.transformers.ehv_hv[["dave_name", "geometry"]]
            )
            trafos = grid_data.components_power.transformers.ehv_hv
            voltage_level = 2
        # update progress
        pbar.update(10)
        # --- create loads for the lowest considered voltage level
        # filter landuses which are within the voronoi regions
        intersection = intersection_with_area(
            grid_data.landuse, voronoi_polygons, remove_columns=False
        )
        intersection.drop(columns=["area_km2"], inplace=True)
        # calculate area from intersected polygons
        intersection_3035 = intersection.to_crs(dave_settings()["crs_meter"])
        intersection["area_km2"] = intersection_3035.area / 1e06
        # --- calculate consumption for the diffrent landuses in every single voronoi polygon
        # create list of all diffrent connection transformers
        trafo_names = list(set(intersection.dave_name))
        trafo_names.sort()
        # update progress
        pbar.update(10)
        # iterate trough diffrent transformers and calulate the diffrent landuse consumptions
        for trafo_name in trafo_names:
            # search trafo bus
            trafo = trafos[trafos.dave_name == trafo_name].iloc[0]
            landuse_polygons = intersection[intersection.dave_name == trafo_name]
            # categorize landuse polygons and add to grid_data
            for loadtype in ["residential", "industrial", "commercial"]:
                if loadtype == "residential":
                    residential_polygons = landuse_polygons[
                        landuse_polygons.landuse == "residential"
                    ]
                    area = residential_polygons.area_km2.sum()
                    p_mw = residential_load * area
                    q_mvar = p_mw * sin(acos(cos_phi_residential)) / cos_phi_residential
                elif loadtype == "industrial":
                    industrial_polygons = landuse_polygons[landuse_polygons.landuse == "industrial"]
                    area = industrial_polygons.area_km2.sum()
                    p_mw = industrial_load * area
                    q_mvar = p_mw * sin(acos(cos_phi_industrial)) / cos_phi_industrial
                elif loadtype == "commercial":
                    commercial_polygons = landuse_polygons[
                        landuse_polygons.landuse.isin(["commercial", "retail"])
                    ]
                    area = commercial_polygons.area_km2.sum()
                    p_mw = commercial_load * area
                    q_mvar = p_mw * sin(acos(cos_phi_commercial)) / cos_phi_commercial
                if p_mw != 0:
                    load_df = gpd.GeoDataFrame(
                        {
                            "bus": trafo.bus_lv,
                            "p_mw": p_mw,
                            "q_mvar": q_mvar,
                            "landuse": loadtype,
                            "trafo_name": trafo_name,
                            "area_km2": area,
                            "voltage_level": [voltage_level],
                            "geometry": trafo.geometry,
                        }
                    )
                    grid_data.components_power.loads = pd.concat(
                        [grid_data.components_power.loads, load_df], ignore_index=True
                    )
            # update progress
            pbar.update(79.8 / len(trafo_names))
    # add dave name
    if not grid_data.components_power.loads.empty:
        grid_data.components_power.loads.insert(
            0,
            "dave_name",
            grid_data.components_power.loads.apply(
                lambda x: f"load_{x.voltage_level}_{x.index}", axis=1
            ),
        )
    # close progress bar
    pbar.close()
