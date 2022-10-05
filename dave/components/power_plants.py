# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import geopandas as gpd
import pandas as pd
from geopy.geocoders import ArcGIS
from shapely.geometry import LineString
from tqdm import tqdm

from dave.datapool import oep_request
from dave.settings import dave_settings
from dave.toolbox import intersection_with_area, voronoi


def aggregate_plants_ren(grid_data, plants_aggr, aggregate_name=None):
    """
    This function aggregates renewables power plants with the same energy source which are connected
    to the same trafo

    INPUT:
        **grid_data** (dict) - all Informations about the target area
        **plants_aggr** (DataFrame) - all renewable power plants that sould be aggregate after
                                      voronoi analysis
    OPTIONAL:
        **aggregate_name** (string) - the original voltage level of the aggregated power plants
    """
    # create list of all diffrent connection transformers
    trafo_names = list(set(plants_aggr.connection_trafo_dave_name.tolist()))
    trafo_names.sort()
    # iterate through the trafo_names to aggregate the power plants with the same energy source
    energy_sources = ["biomass", "gas", "geothermal", "hydro", "solar", "wind"]
    # concat all trafos to assigne the lv node name to the power plant
    trafos = pd.concat(
        [
            grid_data.components_power.transformers.ehv_ehv,
            grid_data.components_power.transformers.ehv_hv,
            grid_data.components_power.transformers.hv_mv,
            grid_data.components_power.transformers.mv_lv,
        ]
    )
    # create aggregated power plants and assigne them to the grid data
    for trafo_name in trafo_names:
        plants_area = plants_aggr[plants_aggr.connection_trafo_dave_name == trafo_name]
        trafo_bus_lv = trafos[trafos.dave_name == trafo_name].iloc[0].bus_lv
        for esource in energy_sources:
            plant_esource = plants_area[plants_area.generation_type == esource]
            if not plant_esource.empty:
                plant_power = pd.to_numeric(plant_esource.electrical_capacity_kw, downcast="float")
                plant_df = gpd.GeoDataFrame(
                    {
                        "aggregated": aggregate_name,
                        "electrical_capacity_kw": plant_power.sum(),
                        "generation_type": esource,
                        "voltage_level": plant_esource.voltage_level.iloc[0],
                        "source": [list(set(plant_esource.source.tolist()))],
                        "geometry": [plant_esource.connection_node.iloc[0]],
                        "bus": trafo_bus_lv,
                    }
                )
                grid_data.components_power.renewable_powerplants = pd.concat(
                    [grid_data.components_power.renewable_powerplants, plant_df], ignore_index=True
                )


def aggregate_plants_con(grid_data, plants_aggr, aggregate_name=None):
    """
    This function aggregates conventionals power plants with the same energy source which are
    connected to the same trafo

    INPUT:
        **grid_data** (dict) - all Informations about the target area
        **plants_aggr** (DataFrame) - all conventional power plants that sould be aggregate after
                                      voronoi analysis
    OPTIONAL:
        **aggregate_name** (string) - the original voltage level of the aggregated power plants
    """
    # create list of all diffrent connection transformers
    trafo_names = list(set(plants_aggr.connection_trafo_dave_name))
    trafo_names.sort()
    # iterate through the trafo_names to aggregate the power plants with the same energy source
    energy_sources = [
        "biomass",
        "coal",
        "gas",
        "gas_mine",
        "lignite",
        "multiple_non_renewable",
        "oil",
        "other_non_renewable",
        "pumped_storage",
        "reservoir",
        "run_of_river",
        "uranium",
        "waste",
    ]
    # concat all trafos to assigne the lv node name to the power plant
    trafos = pd.concat(
        [
            grid_data.components_power.transformers.ehv_ehv,
            grid_data.components_power.transformers.ehv_hv,
            grid_data.components_power.transformers.hv_mv,
            grid_data.components_power.transformers.mv_lv,
        ]
    )
    # create aggregated power plants and assigne them to the grid data
    for trafo_name in trafo_names:
        plants_area = plants_aggr[plants_aggr.connection_trafo_dave_name == trafo_name]
        trafo_bus_lv = trafos[trafos.dave_name == trafo_name].iloc[0].bus_lv
        for esource in energy_sources:
            plant_esource = plants_area[plants_area.fuel == esource]
            if not plant_esource.empty:
                plant_power = pd.to_numeric(plant_esource.capacity_mw, downcast="float")
                plant_df = gpd.GeoDataFrame(
                    {
                        "aggregated": aggregate_name,
                        "electrical_capacity_mw": plant_power.sum(),
                        "fuel": esource,
                        "voltage_level": plant_esource.voltage_level.iloc[0],
                        "geometry": [plant_esource.connection_node.iloc[0]],
                        "bus": trafo_bus_lv,
                    }
                )
                grid_data.components_power.conventional_powerplants = pd.concat(
                    [grid_data.components_power.conventional_powerplants, plant_df],
                    ignore_index=True,
                )


def create_power_plant_lines(grid_data):
    """
    This function checks the distance between a power plant and the associated grid node.
    If the distance is greater than 50 meteres, a auxillary node for the power plant and a
    connection line to the originial node will be created.

    This function is not for aggregated power plants because these are anyway close to the
    connection point
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create powerplant lines:           ",
        position=0,
        bar_format=dave_settings()["bar_format"],
    )
    # get all grid nodes
    all_nodes = pd.concat(
        [
            grid_data.ehv_data.ehv_nodes,
            grid_data.hv_data.hv_nodes,
            grid_data.mv_data.mv_nodes,
            grid_data.lv_data.lv_nodes,
        ]
    )
    all_nodes_3035 = all_nodes.to_crs(dave_settings()["crs_meter"])
    # select all power plants
    renewables = grid_data.components_power.renewable_powerplants
    conventionals = grid_data.components_power.conventional_powerplants
    all_plants = pd.concat([renewables, conventionals], ignore_index=True)
    # update progress
    pbar.update(10)
    # --- create auxillary buses and lines for the power plants
    if not all_plants.empty:
        plants_rel = (
            all_plants[all_plants.aggregated.isnull()]
            if "aggregated" in all_plants.keys()
            else all_plants
        )
        plants_rel.crs = dave_settings()["crs_main"]
        plants_rel_3035 = plants_rel.to_crs(dave_settings()["crs_meter"])
        # considered voltage level
        considered_levels = list(
            map(
                lambda x: {"ehv": 1, "hv": 3, "mv": 5, "lv": 7}[x],
                grid_data.target_input.power_levels[0],
            )
        )
        for _, plant in plants_rel_3035.iterrows():
            plant_bus = all_nodes_3035[all_nodes_3035.dave_name == plant.bus].iloc[0]
            distance = plant.geometry.distance(plant_bus.geometry)  # in meter
            if (distance > 50) and (plant_bus.voltage_level in considered_levels):
                # get plant coordinates in crs 4326
                plant_geometry = plants_rel.loc[plant.name].geometry
                # create auillary node
                if plant_bus.voltage_level == 1:  # (EHV)
                    buses = grid_data.ehv_data.ehv_nodes
                    last_bus_name = buses.iloc[len(buses) - 1].dave_name
                    number = int(last_bus_name.replace("node_1_", "")) + 1
                    dave_name_bus_aux = f"node_1_{number}"
                    auxillary_bus = gpd.GeoDataFrame(
                        {
                            "dave_name": dave_name_bus_aux,
                            "voltage_kv": plant_bus.voltage_kv,
                            "geometry": [plant_geometry],
                            "voltage_level": plant_bus.voltage_level,
                            "source": "dave internal",
                        }
                    )
                    grid_data.ehv_data.ehv_nodes = pd.concat(
                        [grid_data.ehv_data.ehv_nodes, auxillary_bus], ignore_index=True
                    )
                elif plant_bus.voltage_level == 3:  # (HV)
                    buses = grid_data.hv_data.hv_nodes
                    last_bus_name = buses.iloc[len(buses) - 1].dave_name
                    number = int(last_bus_name.replace("node_3_", "")) + 1
                    dave_name_bus_aux = f"node_3_{number}"
                    auxillary_bus = gpd.GeoDataFrame(
                        {
                            "dave_name": dave_name_bus_aux,
                            "voltage_kv": plant_bus.voltage_kv,
                            "geometry": [plant_geometry],
                            "voltage_level": plant_bus.voltage_level,
                            "source": "dave internal",
                        }
                    )
                    grid_data.hv_data.hv_nodes = pd.concat(
                        [grid_data.hv_data.hv_nodes, auxillary_bus], ignore_index=True
                    )
                elif plant_bus.voltage_level == 5:  # (MV)
                    buses = grid_data.mv_data.mv_nodes
                    last_bus_name = buses.iloc[len(buses) - 1].dave_name
                    number = int(last_bus_name.replace("node_5_", "")) + 1
                    dave_name_bus_aux = f"node_5_{number}"
                    auxillary_bus = gpd.GeoDataFrame(
                        {
                            "dave_name": dave_name_bus_aux,
                            "voltage_kv": plant_bus.voltage_kv,
                            "geometry": [plant_geometry],
                            "voltage_level": plant_bus.voltage_level,
                            "source": "dave internal",
                        }
                    )
                    grid_data.mv_data.mv_nodes = pd.concat(
                        [grid_data.mv_data.mv_nodes, auxillary_bus], ignore_index=True
                    )
                elif plant_bus.voltage_level == 7:  # (LV)
                    buses = grid_data.lv_data.lv_nodes
                    last_bus_name = buses.iloc[len(buses) - 1].dave_name
                    number = int(last_bus_name.replace("node_7_", "")) + 1
                    dave_name_bus_aux = f"node_7_{number}"
                    auxillary_bus = gpd.GeoDataFrame(
                        {
                            "dave_name": dave_name_bus_aux,
                            "voltage_kv": plant_bus.voltage_kv,
                            "geometry": [plant_geometry],
                            "voltage_level": plant_bus.voltage_level,
                            "source": "dave internal",
                        }
                    )
                    grid_data.lv_data.lv_nodes = pd.concat(
                        [grid_data.lv_data.lv_nodes, auxillary_bus], ignore_index=True
                    )
                # change bus name in power plant characteristics
                if plant.dave_name[:3] == "con":
                    plant_index = conventionals[conventionals.dave_name == plant.dave_name].index[0]
                    grid_data.components_power.conventional_powerplants.at[
                        plant_index, "bus"
                    ] = dave_name_bus_aux
                elif plant.dave_name[:3] == "ren":
                    plant_index = renewables[renewables.dave_name == plant.dave_name].index[0]
                    grid_data.components_power.renewable_powerplants.at[
                        plant_index, "bus"
                    ] = dave_name_bus_aux
                # create connection line
                bus_origin = all_nodes[all_nodes.dave_name == plant.bus].iloc[0]
                line_geometry = LineString([plant_geometry, bus_origin.geometry])
                if plant_bus.voltage_level == 1:  # (EHV)
                    ehv_lines = grid_data.ehv_data.ehv_lines
                    last_line_name = ehv_lines.iloc[len(ehv_lines) - 1].dave_name
                    number = int(last_line_name.replace("line_1_", "")) + 1
                    # check if there is a line neighbor
                    line_neighbor = ehv_lines[
                        (ehv_lines.from_bus == bus_origin.dave_name)
                        | (ehv_lines.to_bus == bus_origin.dave_name)
                    ]
                    if not line_neighbor.empty:
                        line_neighbor = line_neighbor.iloc[0]
                        auxillary_line = gpd.GeoDataFrame(
                            {
                                "dave_name": f"line_1_{number}",
                                "bus0": dave_name_bus_aux,
                                "bus1": bus_origin.dave_name,
                                "x_ohm": line_neighbor.x_ohm_per_km / distance,
                                "x_ohm_per_km": line_neighbor.x_ohm_per_km,
                                "r_ohm": line_neighbor.r_ohm_per_km / distance,
                                "r_ohm_per_km": line_neighbor.r_ohm_per_km,
                                "c_nf": line_neighbor.c_nf_per_km / distance,
                                "c_nf_per_km": line_neighbor.c_nf_per_km,
                                "s_nom_mva": line_neighbor.s_nom_mva,
                                "length_km": distance / 1000,
                                "geometry": [line_geometry],
                                "voltage_kv": line_neighbor.voltage_kv,
                                "max_i_ka": line_neighbor.max_i_ka,
                                "parallel": line_neighbor.parallel,
                                "voltage_level": line_neighbor.voltage_level,
                                "source": "dave internal",
                            },
                            crs=dave_settings()["crs_main"],
                        )
                        grid_data.ehv_data.ehv_lines = pd.concat(
                            [grid_data.ehv_data.ehv_lines, auxillary_line], ignore_index=True
                        )
                elif plant_bus.voltage_level == 3:  # (HV)
                    hv_lines = grid_data.hv_data.hv_lines
                    last_line_name = hv_lines.iloc[len(hv_lines) - 1].dave_name
                    number = int(last_line_name.replace("line_3_", "")) + 1
                    # check if there is a line neighbor
                    line_neighbor = hv_lines[
                        (hv_lines.from_bus == bus_origin.dave_name)
                        | (hv_lines.to_bus == bus_origin.dave_name)
                    ]
                    if not line_neighbor.empty:
                        line_neighbor = line_neighbor.iloc[0]
                        auxillary_line = gpd.GeoDataFrame(
                            {
                                "dave_name": f"line_3_{number}",
                                "bus0": dave_name_bus_aux,
                                "bus1": bus_origin.dave_name,
                                "x_ohm": line_neighbor.x_ohm_per_km / distance,
                                "x_ohm_per_km": line_neighbor.x_ohm_per_km,
                                "r_ohm": line_neighbor.r_ohm_per_km / distance,
                                "r_ohm_per_km": line_neighbor.r_ohm_per_km,
                                "c_nf": line_neighbor.c_nf_per_km / distance,
                                "c_nf_per_km": line_neighbor.c_nf_per_km,
                                "s_nom_mva": line_neighbor.s_nom_mva,
                                "length_km": distance / 1000,
                                "geometry": [line_geometry],
                                "voltage_kv": line_neighbor.voltage_kv,
                                "max_i_ka": line_neighbor.max_i_ka,
                                "parallel": line_neighbor.parallel,
                                "voltage_level": line_neighbor.voltage_level,
                                "source": "dave internal",
                            },
                            crs=dave_settings()["crs_main"],
                        )
                        grid_data.hv_data.hv_lines = pd.concat(
                            [grid_data.hv_data.hv_lines, auxillary_line], ignore_index=True
                        )
                elif plant_bus.voltage_level == 5:  # (MV)
                    mv_lines = grid_data.mv_data.mv_lines
                    last_line_name = mv_lines.iloc[len(mv_lines) - 1].dave_name
                    number = int(last_line_name.replace("line_5_", "")) + 1
                    # check if there is a line neighbor
                    line_neighbor = mv_lines[
                        (mv_lines.from_bus == bus_origin.dave_name)
                        | (mv_lines.to_bus == bus_origin.dave_name)
                    ]
                    if not line_neighbor.empty:
                        line_neighbor = line_neighbor.iloc[0]
                        # Diese Parameter noch angepasst, wenn die MV Line Daten bekannt sind
                        auxillary_line = gpd.GeoDataFrame(
                            {
                                "dave_name": f"line_5_{number}",
                                "from_bus": dave_name_bus_aux,
                                "to_bus": bus_origin.dave_name,
                                "length_km": distance / 1000,
                                "geometry": [line_geometry],
                                "voltage_kv": line_neighbor.voltage_kv,
                                "voltage_level": line_neighbor.voltage_level,
                                "source": "dave internal",
                            },
                            crs=dave_settings()["crs_main"],
                        )
                        grid_data.mv_data.mv_lines = pd.concat(
                            [grid_data.mv_data.mv_lines, auxillary_line], ignore_index=True
                        )
                elif plant_bus.voltage_level == 7:  # (LV)
                    lv_lines = grid_data.lv_data.lv_lines
                    last_line_name = lv_lines.iloc[len(lv_lines) - 1].dave_name
                    number = int(last_line_name.replace("line_7_", "")) + 1
                    # check if there is a line neighbor
                    # line neighbor muss noch angepasst werden auf from und to bus aus lv_lines
                    line_neighbor = lv_lines[
                        (lv_lines.from_bus == bus_origin.dave_name)
                        | (lv_lines.to_bus == bus_origin.dave_name)
                    ]
                    if not line_neighbor.empty:
                        line_neighbor = line_neighbor.iloc[0]
                        # Diese Parameter müssen noch angepasst werden wenn lv neu berechnet wird
                        auxillary_line = gpd.GeoDataFrame(
                            {
                                "dave_name": f"line_7_{number}",
                                "length_km": distance / 1000,
                                "geometry": [line_geometry],
                                "voltage_kv": line_neighbor.voltage_kv,
                                "voltage_level": line_neighbor.voltage_level,
                                "line_type": "power plant line",
                                "source": "dave internal",
                                "from_bus": dave_name_bus_aux,
                                "to_bus": bus_origin.dave_name,
                            },
                            crs=dave_settings()["crs_main"],
                        )
                        grid_data.lv_data.lv_lines = pd.concat(
                            [grid_data.lv_data.lv_lines, auxillary_line], ignore_index=True
                        )
            # update progress
            pbar.update(89.98 / len(plants_rel_3035))
    else:
        # update progress
        pbar.update(90)
    # close progress bar
    pbar.close()


def create_renewable_powerplants(grid_data):
    """
    This function collects the generators based on ego_renewable_powerplant from OEP
    and perhaps assign them their exact location by adress, if these are available.
    Furthermore assign a grid node to the generators and aggregated them depending on the situation
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create renewable powerplants:      ",
        position=0,
        bar_format=dave_settings()["bar_format"],
    )
    # define power_levels
    power_levels = grid_data.target_input.power_levels[0]
    # load powerplant data in target area
    typ = grid_data.target_input.typ.iloc[0]
    if typ in ["postalcode", "federal state", "own area", "nuts region"]:
        for plz in grid_data.target_input.data.iloc[0]:
            data, meta_data = oep_request(table="ego_renewable_powerplant", where=f"postcode={plz}")
            # add meta data
            if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
                grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
            if plz == grid_data.target_input.data.iloc[0][0]:
                renewables = data
            else:
                renewables = pd.concat([renewables, data], ignore_index=True)
    elif typ == "town name":
        for name in grid_data.target_input.data.iloc[0]:
            data, meta_data = oep_request(table="ego_renewable_powerplant", where=f"city={name}")
            # add meta data
            if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
                grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
            if name == grid_data.target_input.data.iloc[0][0]:
                renewables = data
            else:
                renewables = renewables.append(data)
    else:
        renewables = pd.DataFrame()
    # update progress
    pbar.update(10)
    # prepare the DataFrame of the renewable plants
    if not renewables.empty:
        renewables.reset_index(drop=True, inplace=True)
        renewables.drop(columns=["id", "gps_accuracy", "geom"], inplace=True)
        renewables["lon"] = renewables["lon"].astype(float)
        renewables["lat"] = renewables["lat"].astype(float)
        renewables.rename(
            columns={
                "electrical_capacity": "electrical_capacity_kw",
                "thermal_capacity": "thermal_capacity_kw",
            },
            inplace=True,
        )
        # change voltage level to numbers
        for i, plant in renewables.iterrows():
            if plant.voltage_level:
                renewables.at[i, "voltage_level"] = int(plant.voltage_level[1:2])
            # This is for plants which have a nan value at the voltage level parameter
            elif float(plant.electrical_capacity_kw) <= 50:
                renewables.at[i, "voltage_level"] = 7
            else:
                renewables.at[i, "voltage_level"] = 5
        # restrict plants to considered power levels
        if "HV" in power_levels:
            renewables = renewables[renewables.voltage_level >= 3]
        elif "MV" in power_levels:
            renewables = renewables[renewables.voltage_level >= 5]
        elif "LV" in power_levels:
            renewables = renewables[renewables.voltage_level == 7]
        # find exact location by adress for renewable power plants which are on mv-level or lower
        if any(map(lambda x: x in power_levels, ["MV", "LV"])):
            geolocator = ArcGIS(timeout=None)
            plant_georefernce = renewables[renewables.voltage_level >= 5]
            for i, plant in plant_georefernce.iterrows():
                if plant.address:
                    address = str(plant.address) + " " + str(plant.postcode) + " " + str(plant.city)
                    location = geolocator.geocode(address)
                    renewables.at[i, "lon"] = location.longitude
                    renewables.at[i, "lat"] = location.latitude
                else:
                    pass
                    # zu diesem Zeitpunkt erstmal die Geokoordinaten des Rasterpunktes
                    # behalten, falls keine Adresse bekannt. Das aber noch abändern.
                # update progress
                pbar.update(20 / len(plant_georefernce))
        else:
            # update progress
            pbar.update(20)
        # convert DataFrame into a GeoDataFrame
        renewables_geo = gpd.GeoDataFrame(
            renewables,
            crs=dave_settings()["crs_main"],
            geometry=gpd.points_from_xy(renewables.lon, renewables.lat),
        )
        # intersection of power plants with target_area when target is an own area
        if typ == "own area":
            renewables_geo = intersection_with_area(
                renewables_geo, grid_data.area, remove_columns=False
            )
        # --- node assignment with case distinction depending on considered power levels
        # divide the plants in the target area according to their voltage level
        renewables_lv = renewables_geo[renewables_geo.voltage_level == 7]
        renewables_mv_lv = renewables_geo[renewables_geo.voltage_level == 6]
        renewables_mv = renewables_geo[renewables_geo.voltage_level == 5]
        renewables_hv_mv = renewables_geo[renewables_geo.voltage_level == 4]
        renewables_hv = renewables_geo[renewables_geo.voltage_level == 3]
        renewables_ehv_hv = renewables_geo[renewables_geo.voltage_level == 2]
        renewables_ehv = renewables_geo[renewables_geo.voltage_level == 1]

        # --- nodes for level 7 plants (LV)
        if not renewables_lv.empty:
            if "lv" in power_levels:
                # In this case the Level 7 plants are assigned to the nearest lv node
                voronoi_polygons = voronoi(grid_data.lv_data.lv_nodes[["dave_name", "geometry"]])
                intersection = gpd.sjoin(renewables_lv, voronoi_polygons, how="inner")
                intersection.drop(columns=["index_right", "centroid"], inplace=True)
                intersection.rename(columns={"dave_name": "bus"}, inplace=True)
                grid_data.components_power.renewable_powerplants = pd.concat(
                    [grid_data.components_power.renewable_powerplants, intersection],
                    ignore_index=True,
                )
            # find next higher and considered voltage level to assigne the lv-plants
            elif any(map(lambda x: x in power_levels, ["ehv", "hv", "mv"])):
                if "mv" in power_levels:
                    # In this case the Level 7 plants are assigned to the nearest mv/lv-transformer
                    voronoi_polygons = voronoi(
                        grid_data.components_power.transformers.mv_lv[["dave_name", "geometry"]]
                    )
                    voltage_level = 6
                elif "hv" in power_levels:
                    # In this case the Level 7 plants are assigned to the nearest hv/mv-transformer
                    voronoi_polygons = voronoi(
                        grid_data.components_power.transformers.hv_mv[["dave_name", "geometry"]]
                    )
                    voltage_level = 4
                elif "ehv" in power_levels:
                    # In this case the Level 7 plants are assigned to the nearest ehv/hv-transformer
                    voronoi_polygons = voronoi(
                        grid_data.components_power.transformers.ehv_hv[["dave_name", "geometry"]]
                    )
                    voltage_level = 2
                intersection = gpd.sjoin(renewables_lv, voronoi_polygons, how="inner")
                intersection.drop(columns=["index_right"], inplace=True)
                intersection.rename(
                    columns={
                        "centroid": "connection_node",
                        "dave_name": "connection_trafo_dave_name",
                    },
                    inplace=True,
                )
                # change voltage level to the new connection level
                intersection.voltage_level = voltage_level
                # select only data which is relevant after aggregation
                intersection_rel = intersection[
                    [
                        "electrical_capacity_kw",
                        "generation_type",
                        "voltage_level",
                        "source",
                        "connection_node",
                        "connection_trafo_dave_name",
                    ]
                ]
                # aggregated power plants, set geometry and write them into grid data
                aggregate_plants_ren(grid_data, intersection_rel, aggregate_name="level 7 plants")
        # update progress
        pbar.update(10)

        # --- nodes for level 6 plants (MV/LV)
        if not renewables_mv_lv.empty:
            if any(map(lambda x: x in power_levels, ["mv", "lv"])):
                # In this case the Level 6 plants are assigned to the nearest mv/lv-transformer
                voronoi_polygons = voronoi(
                    grid_data.components_power.transformers.mv_lv[["dave_name", "geometry"]]
                )
                intersection = gpd.sjoin(renewables_mv_lv, voronoi_polygons, how="inner")
                intersection.rename(columns={"dave_name": "trafo_name"}, inplace=True)
                # search transformer bus lv name
                trafos = grid_data.components_power.transformers.mv_lv
                intersection["bus"] = intersection.trafo_name.apply(
                    lambda x: trafos[trafos.dave_name == x].iloc[0].bus_lv
                )
                intersection.drop(columns=["index_right", "centroid", "trafo_name"], inplace=True)
                grid_data.components_power.renewable_powerplants = pd.concat(
                    [grid_data.components_power.renewable_powerplants, intersection],
                    ignore_index=True,
                )
            # find next higher and considered voltage level to assigne the mvlv-plants
            elif any(map(lambda x: x in power_levels, ["ehv", "hv"])):
                if "hv" in power_levels:
                    # In this case the Level 6 plants are assigned to the nearest hv/mv-transformer
                    voronoi_polygons = voronoi(
                        grid_data.components_power.transformers.hv_mv[["dave_name", "geometry"]]
                    )
                    voltage_level = 4
                elif "ehv" in power_levels:
                    # In this case the Level 6 plants are assigned to the nearest ehv/hv-transformer
                    voronoi_polygons = voronoi(
                        grid_data.components_power.transformers.ehv_hv[["dave_name", "geometry"]]
                    )
                    voltage_level = 2
                intersection = gpd.sjoin(renewables_mv_lv, voronoi_polygons, how="inner")
                intersection.drop(columns=["index_right"], inplace=True)
                intersection.rename(
                    columns={
                        "centroid": "connection_node",
                        "dave_name": "connection_trafo_dave_name",
                    },
                    inplace=True,
                )
                # change voltage level to the new connection level
                intersection.voltage_level = voltage_level
                # select only data which is relevant after aggregation
                intersection_rel = intersection[
                    [
                        "electrical_capacity_kw",
                        "generation_type",
                        "voltage_level",
                        "source",
                        "connection_node",
                        "connection_trafo_dave_name",
                    ]
                ]
                # aggregated power plants, set geometry and write them into grid data
                aggregate_plants_ren(grid_data, intersection_rel, aggregate_name="level 6 plants")
        # update progress
        pbar.update(10)

        # --- nodes for level 5 plants (MV)
        if not renewables_mv.empty:
            if "mv" in power_levels:
                # In this case the Level 5 plants are assigned to the nearest mv node
                voronoi_polygons = voronoi(grid_data.mv_data.mv_nodes[["dave_name", "geometry"]])
                intersection = gpd.sjoin(
                    renewables_mv, voronoi_polygons, how="inner", op="intersects"
                )
                intersection.drop(columns=["index_right", "centroid"], inplace=True)
                intersection.rename(columns={"dave_name": "bus"}, inplace=True)
                grid_data.components_power.renewable_powerplants = pd.concat(
                    [grid_data.components_power.renewable_powerplants, intersection],
                    ignore_index=True,
                )
            # find next higher and considered voltage level to assigne the mv-plants
            elif any(map(lambda x: x in power_levels, ["ehv", "hv"])):
                if "hv" in power_levels:
                    # In this case the Level 5 plants area assigned to the nearest hv/mv-transformer
                    voronoi_polygons = voronoi(
                        grid_data.components_power.transformers.hv_mv[["dave_name", "geometry"]]
                    )
                    voltage_level = 4
                elif "ehv" in power_levels:
                    # In this case the Level 5 plants are assigned to the nearest ehv/hv-transformer
                    voronoi_polygons = voronoi(
                        grid_data.components_power.transformers.ehv_hv[["dave_name", "geometry"]]
                    )
                    voltage_level = 2
                intersection = gpd.sjoin(renewables_mv, voronoi_polygons, how="inner")
                intersection.drop(columns=["index_right"], inplace=True)
                intersection.rename(
                    columns={
                        "centroid": "connection_node",
                        "dave_name": "connection_trafo_dave_name",
                    },
                    inplace=True,
                )
                # change voltage level to the new connection level
                intersection.voltage_level = voltage_level
                # select only data which is relevant after aggregation
                intersection_rel = intersection[
                    [
                        "electrical_capacity_kw",
                        "generation_type",
                        "voltage_level",
                        "source",
                        "connection_node",
                        "connection_trafo_dave_name",
                    ]
                ]
                # aggregated power plants, set geometry and write them into grid data
                aggregate_plants_ren(grid_data, intersection_rel, aggregate_name="level 5 plants")
        # update progress
        pbar.update(10)

        # --- nodes for level 4 plants (HV/MV)
        if not renewables_hv_mv.empty:
            if any(map(lambda x: x in power_levels, ["hv", "mv"])):
                # In this case the Level 4 plants are assigned to the nearest hv/mv-transformer
                voronoi_polygons = voronoi(
                    grid_data.components_power.transformers.hv_mv[["dave_name", "geometry"]]
                )
                intersection = gpd.sjoin(
                    renewables_hv_mv, voronoi_polygons, how="inner", op="intersects"
                )
                intersection.rename(columns={"dave_name": "trafo_name"}, inplace=True)
                # search transformer bus lv name
                trafos = grid_data.components_power.transformers.hv_mv
                intersection["bus"] = intersection.trafo_name.apply(
                    lambda x: trafos[trafos.dave_name == x].iloc[0].bus_lv
                )
                intersection.drop(columns=["index_right", "centroid", "trafo_name"], inplace=True)
                grid_data.components_power.renewable_powerplants = pd.concat(
                    [grid_data.components_power.renewable_powerplants, intersection],
                    ignore_index=True,
                )
            # find next higher and considered voltage level to assigne the hvmv-plants
            elif "ehv" in power_levels:
                # In this case the Level 4 plants assigned to the nearest ehv/hv-transformer
                voronoi_polygons = voronoi(
                    grid_data.components_power.transformers.ehv_hv[["dave_name", "geometry"]]
                )
                intersection = gpd.sjoin(renewables_hv_mv, voronoi_polygons, how="inner")
                intersection.drop(columns=["index_right"], inplace=True)
                intersection.rename(
                    columns={
                        "centroid": "connection_node",
                        "dave_name": "connection_trafo_dave_name",
                    },
                    inplace=True,
                )
                # change voltage level to the new connection level
                intersection.voltage_level = 2
                # select only data which is relevant after aggregation
                intersection_rel = intersection[
                    [
                        "electrical_capacity_kw",
                        "generation_type",
                        "voltage_level",
                        "source",
                        "connection_node",
                        "connection_trafo_dave_name",
                    ]
                ]
                # aggregated power plants, set geometry and write them into grid data
                aggregate_plants_ren(grid_data, intersection_rel, aggregate_name="level 4 plants")
        # update progress
        pbar.update(10)

        # --- nodes for level 3 plants (HV)
        if not renewables_hv.empty:
            if "hv" in power_levels:
                # In this case the Level 3 plants are assigned to the nearest hv node
                voronoi_polygons = voronoi(grid_data.hv_data.hv_nodes[["dave_name", "geometry"]])
                intersection = gpd.sjoin(
                    renewables_hv, voronoi_polygons, how="inner", op="intersects"
                )
                intersection.drop(columns=["index_right", "centroid"], inplace=True)
                intersection.rename(columns={"dave_name": "bus"}, inplace=True)
                grid_data.components_power.renewable_powerplants = pd.concat(
                    [grid_data.components_power.renewable_powerplants, intersection],
                    ignore_index=True,
                )
            # find next higher and considered voltage level to assigne the hv-plants
            elif "ehv" in power_levels:
                # In this case the Level 3 plants are assigned to the nearest ehv/hv-transformer
                voronoi_polygons = voronoi(
                    grid_data.components_power.transformers.ehv_hv[["dave_name", "geometry"]]
                )
                intersection = gpd.sjoin(renewables_hv, voronoi_polygons, how="inner")
                intersection.drop(columns=["index_right"], inplace=True)
                intersection.rename(
                    columns={
                        "centroid": "connection_node",
                        "dave_name": "connection_trafo_dave_name",
                    },
                    inplace=True,
                )
                # change voltage level to the new connection level
                intersection.voltage_level = 2
                # select only data which is relevant after aggregation
                intersection_rel = intersection[
                    [
                        "electrical_capacity_kw",
                        "generation_type",
                        "voltage_level",
                        "source",
                        "connection_node",
                        "connection_trafo_dave_name",
                    ]
                ]
                # aggregated power plants, set geometry and write them into grid data
                aggregate_plants_ren(grid_data, intersection_rel, aggregate_name="level 3 plants")
        # update progress
        pbar.update(10)

        # --- nodes for level 2 plants (EHV/HV)
        if not renewables_ehv_hv.empty:
            if any(map(lambda x: x in power_levels, ["ehv", "hv"])):
                # In this case the Level 2 plants are assigned to the nearest ehv/hv-transformer
                voronoi_polygons = voronoi(
                    grid_data.components_power.transformers.ehv_hv[["dave_name", "geometry"]]
                )
                intersection = gpd.sjoin(
                    renewables_ehv_hv, voronoi_polygons, how="inner", op="intersects"
                )
                intersection.rename(columns={"dave_name": "trafo_name"}, inplace=True)
                # search transformer bus lv name
                trafos = grid_data.components_power.transformers.ehv_hv
                intersection["bus"] = intersection.trafo_name.apply(
                    lambda x: trafos[trafos.dave_name == x].iloc[0].bus_lv
                )
                intersection.drop(columns=["index_right", "centroid", "trafo_name"], inplace=True)
                grid_data.components_power.renewable_powerplants = pd.concat(
                    [grid_data.components_power.renewable_powerplants, intersection],
                    ignore_index=True,
                )
        # update progress
        pbar.update(10)

        # --- nodes for level 1 plants (EHV)
        if not renewables_ehv.empty:
            if "ehv" in power_levels:
                # In this case the Level 1 plants are assigned to the nearest ehv node
                voronoi_polygons = voronoi(grid_data.ehv_data.ehv_nodes[["dave_name", "geometry"]])
                intersection = gpd.sjoin(renewables_ehv, voronoi_polygons, how="inner")
                intersection.drop(columns=["index_right", "centroid"], inplace=True)
                intersection.rename(columns={"dave_name": "bus"}, inplace=True)
                grid_data.components_power.renewable_powerplants = pd.concat(
                    [grid_data.components_power.renewable_powerplants, intersection],
                    ignore_index=True,
                )
        # --- add general informations
        if not grid_data.components_power.renewable_powerplants.empty:
            # add dave name
            name = grid_data.components_power.renewable_powerplants.apply(
                lambda x: f"ren_powerplant_{x.voltage_level}_{x.name}", axis=1
            )
            grid_data.components_power.renewable_powerplants.insert(0, "dave_name", name)
            # set crs
            grid_data.components_power.renewable_powerplants.set_crs(
                dave_settings()["crs_main"], inplace=True
            )
        # update progress
        pbar.update(9.98)
    else:
        # update progress
        pbar.update(89.98)
    # close progress bar
    pbar.close()


def create_conventional_powerplants(grid_data):
    """
    This function collects the generators based on ego_conventional_powerplant from OEP
    Furthermore assign a grid node to the generators and aggregated them depending on the situation
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create conventional powerplants:   ",
        position=0,
        bar_format=dave_settings()["bar_format"],
    )
    # define power_levels
    power_levels = grid_data.target_input.power_levels[0]
    # load powerplant data in target area
    typ = grid_data.target_input.typ.iloc[0]
    if typ in ["postalcode", "federal state", "own area", "nuts region"]:
        for plz in grid_data.target_input.data.iloc[0]:
            data, meta_data = oep_request(
                table="ego_conventional_powerplant", where=f"postcode={plz}"
            )
            # add meta data
            if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
                grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
            if plz == grid_data.target_input.data.iloc[0][0]:
                conventionals = data
            else:
                conventionals = pd.concat([conventionals, data], ignore_index=True)
    elif typ == "town name":
        for name in grid_data.target_input.data.iloc[0]:
            data, meta_data = oep_request(table="ego_conventional_powerplant", where=f"city={name}")
            # add meta data
            if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
                grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
            if name == grid_data.target_input.data.iloc[0][0]:
                conventionals = data
            else:
                conventionals = conventionals.append(data)
    # update progress
    pbar.update(20)
    # prepare the DataFrame of the conventional plants
    if not conventionals.empty:
        conventionals.reset_index(drop=True, inplace=True)
        conventionals.drop(columns=["gid", "geom"], inplace=True)
        conventionals.rename(
            columns={"capacity": "capacity_mw", "chp_capacity_uba": "chp_capacity_uba_mw"},
            inplace=True,
        )
        # prepare power plant voltage parameter for processing
        for i, plant in conventionals.iterrows():
            if plant.voltage is None:
                conventionals.at[plant.name, "voltage"] = "None"
            elif plant.voltage in ["HS", "10 und 110", "110/6"]:
                conventionals.at[plant.name, "voltage"] = "110"
            elif plant.voltage in ["MS", "MSP", "10kV, 25kV", "Mai 25"]:
                conventionals.at[plant.name, "voltage"] = "20"
            elif plant.voltage == "220 / 110 / 10":
                conventionals.at[plant.name, "voltage"] = "220"
            elif plant.voltage == "30 auf 6":
                conventionals.at[plant.name, "voltage"] = "30"
            elif plant.voltage == "6\n20":
                conventionals.at[plant.name, "voltage"] = "Werknetz"
        # drop plants with no defined voltage, plants at factory networks and shutdowned plants
        conventionals.drop(
            conventionals[conventionals.voltage.isin(["Werknetz", "None"])].index.to_list()
            + conventionals[conventionals.status == "shutdown"].index.to_list(),
            inplace=True,
        )
        # add voltage level
        for i, plant in conventionals.iterrows():
            if plant.voltage == "HS":
                conventionals.at[i, "voltage_level"] = 3
            elif plant.voltage == "HS/MS":
                conventionals.at[i, "voltage_level"] = 4
            elif plant.voltage == "MS":
                conventionals.at[i, "voltage_level"] = 5
            elif int(plant.voltage) >= 220:
                conventionals.at[i, "voltage_level"] = 1
            elif (int(plant.voltage) < 220) and (int(plant.voltage) >= 60):
                conventionals.at[i, "voltage_level"] = 3
            elif (int(plant.voltage) < 60) and (int(plant.voltage) >= 1):
                conventionals.at[i, "voltage_level"] = 5
            elif int(plant.voltage) < 1:
                conventionals.at[i, "voltage_level"] = 7
        # restrict plants to considered power levels
        if "hv" in power_levels:
            conventionals = conventionals[conventionals.voltage_level >= 3]
        elif "mv" in power_levels:
            conventionals = conventionals[conventionals.voltage_level >= 5]
        elif "lv" in power_levels:
            conventionals = conventionals[conventionals.voltage_level == 7]
        # convert DataFrame into a GeoDataFrame
        conventionals_geo = gpd.GeoDataFrame(
            conventionals,
            crs=dave_settings()["crs_main"],
            geometry=gpd.points_from_xy(conventionals.lon, conventionals.lat),
        )
        # intersection of power plants with target_area when target is an own area
        if (typ == "own area") and (not conventionals_geo.empty):
            conventionals_geo = intersection_with_area(
                conventionals_geo, grid_data.area, remove_columns=False
            )
        # --- node assignment with case distinction depending on considered power levels
        # divide the plants in the target area according to their voltage level
        conventionals_lv = conventionals_geo[conventionals_geo.voltage_level == 7]
        conventionals_mv_lv = conventionals_geo[conventionals_geo.voltage_level == 6]
        conventionals_mv = conventionals_geo[conventionals_geo.voltage_level == 5]
        conventionals_hv_mv = conventionals_geo[conventionals_geo.voltage_level == 4]
        conventionals_hv = conventionals_geo[conventionals_geo.voltage_level == 3]
        conventionals_ehv_hv = conventionals_geo[conventionals_geo.voltage_level == 2]
        conventionals_ehv = conventionals_geo[conventionals_geo.voltage_level == 1]
        # update progress
        pbar.update(10)

        # --- nodes for level 7 plants (LV)
        if not conventionals_lv.empty:
            if "LV" in power_levels:
                # In this case the Level 7 plants are assigned to the nearest lv node
                voronoi_polygons = voronoi(grid_data.lv_data.lv_nodes[["dave_name", "geometry"]])
                intersection = gpd.sjoin(conventionals_lv, voronoi_polygons, how="inner")
                intersection.drop(columns=["index_right", "centroid"], inplace=True)
                intersection.rename(
                    columns={"dave_name": "bus", "capacity_mw": "electrical_capacity_mw"},
                    inplace=True,
                )
                grid_data.components_power.conventional_powerplants = pd.concat(
                    [grid_data.components_power.conventional_powerplants, intersection],
                    ignore_index=True,
                )
            # find next higher and considered voltage level to assigne the lv-plants
            elif any(map(lambda x: x in power_levels, ["ehv", "hv", "mv"])):
                if "mv" in power_levels:
                    # In this case the Level 7 plants are assigned to the nearest mv/lv-transformer
                    voronoi_polygons = voronoi(
                        grid_data.components_power.transformers.mv_lv[["dave_name", "geometry"]]
                    )
                    voltage_level = 6
                elif "hv" in power_levels:
                    # In this case the Level 7 plants are assigned to the nearest hv/mv-transformer
                    voronoi_polygons = voronoi(
                        grid_data.components_power.transformers.hv_mv[["dave_name", "geometry"]]
                    )
                    voltage_level = 4
                elif "ehv" in power_levels:
                    # In this case the Level 7 plants are assigned to the nearest ehv/hv-transformer
                    voronoi_polygons = voronoi(
                        grid_data.components_power.transformers.ehv_hv[["dave_name", "geometry"]]
                    )
                    voltage_level = 2
                intersection = gpd.sjoin(conventionals_lv, voronoi_polygons, how="inner")
                intersection.drop(columns=["index_right"], inplace=True)
                intersection.rename(
                    columns={
                        "centroid": "connection_node",
                        "dave_name": "connection_trafo_dave_name",
                    },
                    inplace=True,
                )
                # change voltage level to the new connection level
                intersection.voltage_level = voltage_level
                # select only data which is relevant after aggregation
                intersection_rel = intersection[
                    [
                        "capacity_mw",
                        "voltage_level",
                        "fuel",
                        "connection_node",
                        "connection_trafo_dave_name",
                    ]
                ]
                # aggregated power plants, set geometry and write them into grid data
                aggregate_plants_con(grid_data, intersection_rel, aggregate_name="level 7 plants")
        # update progress
        pbar.update(10)

        # --- nodes for level 6 plants (MV/LV)
        if not conventionals_mv_lv.empty:
            if any(map(lambda x: x in power_levels, ["mv", "lv"])):
                # In this case the Level 6 plants are assigned to the nearest mv/lv-transformer
                voronoi_polygons = voronoi(
                    grid_data.components_power.transformers.mv_lv[["dave_name", "geometry"]]
                )
                intersection = gpd.sjoin(conventionals_mv_lv, voronoi_polygons, how="inner")
                intersection.drop(columns=["index_right", "centroid"], inplace=True)
                intersection.rename(
                    columns={"dave_name": "trafo_name", "capacity_mw": "electrical_capacity_mw"},
                    inplace=True,
                )
                # search transformer bus lv name
                trafos = grid_data.components_power.transformers.mv_lv
                intersection["bus"] = intersection.trafo_name.apply(
                    lambda x: trafos[trafos.dave_name == x].iloc[0].bus_lv
                )
                intersection.drop(columns=["index_right", "centroid", "trafo_name"], inplace=True)
                grid_data.components_power.conventional_powerplants = pd.concat(
                    [grid_data.components_power.conventional_powerplants, intersection],
                    ignore_index=True,
                )
            # find next higher and considered voltage level to assigne the mvlv-plants
            elif any(map(lambda x: x in power_levels, ["ehv", "hv"])):
                if "hv" in power_levels:
                    # In this case the Level 6 plants are assigned to the nearest hv/mv-transformer
                    voronoi_polygons = voronoi(
                        grid_data.components_power.transformers.hv_mv[["dave_name", "geometry"]]
                    )
                    voltage_level = 4
                elif "ehv" in power_levels:
                    # In this case the Level 6 plants are assigned to the nearest ehv/hv-transformer
                    voronoi_polygons = voronoi(
                        grid_data.components_power.transformers.ehv_hv[["dave_name", "geometry"]]
                    )
                    voltage_level = 2
                intersection = gpd.sjoin(conventionals_mv_lv, voronoi_polygons, how="inner")
                intersection.drop(columns=["index_right"], inplace=True)
                intersection.rename(
                    columns={
                        "centroid": "connection_node",
                        "dave_name": "connection_trafo_dave_name",
                    },
                    inplace=True,
                )
                # change voltage level to the new connection level
                intersection.voltage_level = voltage_level
                # select only data which is relevant after aggregation
                intersection_rel = intersection[
                    [
                        "capacity_mw",
                        "voltage_level",
                        "fuel",
                        "connection_node",
                        "connection_trafo_dave_name",
                    ]
                ]
                # aggregated power plants, set geometry and write them into grid data
                aggregate_plants_con(grid_data, intersection_rel, aggregate_name="level 6 plants")
        # update progress
        pbar.update(10)

        # --- nodes for level 5 plants (MV)
        if not conventionals_mv.empty:
            if "mv" in power_levels:
                # In this case the Level 5 plants are assigned to the nearest mv node
                voronoi_polygons = voronoi(grid_data.mv_data.mv_nodes[["dave_name", "geometry"]])
                intersection = gpd.sjoin(conventionals_mv, voronoi_polygons, how="inner")
                intersection.drop(columns=["index_right", "centroid"], inplace=True)
                intersection.rename(
                    columns={"dave_name": "bus", "capacity_mw": "electrical_capacity_mw"},
                    inplace=True,
                )
                grid_data.components_power.conventional_powerplants = pd.concat(
                    [grid_data.components_power.conventional_powerplants, intersection],
                    ignore_index=True,
                )
            # find next higher and considered voltage level to assigne the mv-plants
            elif any(map(lambda x: x in power_levels, ["ehv", "hv"])):
                if "hv" in power_levels:
                    # In this case the Level 5 plants are assigned to the nearest hv/mv-transformer
                    voronoi_polygons = voronoi(
                        grid_data.components_power.transformers.hv_mv[["dave_name", "geometry"]]
                    )
                    voltage_level = 4
                elif "ehv" in power_levels:
                    # In this case the Level 5 plants are assigned to the nearest ehv/hv-transformer
                    voronoi_polygons = voronoi(
                        grid_data.components_power.transformers.ehv_hv[["dave_name", "geometry"]]
                    )
                    voltage_level = 2
                intersection = gpd.sjoin(conventionals_mv, voronoi_polygons, how="inner")
                intersection.drop(columns=["index_right"], inplace=True)
                intersection.rename(
                    columns={
                        "centroid": "connection_node",
                        "dave_name": "connection_trafo_dave_name",
                    },
                    inplace=True,
                )
                # change voltage level to the new connection level
                intersection.voltage_level = voltage_level
                # select only data which is relevant after aggregation
                intersection_rel = intersection[
                    [
                        "capacity_mw",
                        "voltage_level",
                        "fuel",
                        "connection_node",
                        "connection_trafo_dave_name",
                    ]
                ]
                # aggregated power plants, set geometry and write them into grid data
                aggregate_plants_con(grid_data, intersection_rel, aggregate_name="level 5 plants")
        # update progress
        pbar.update(10)

        # --- nodes for level 4 plants (HV/MV)
        if not conventionals_hv_mv.empty:
            if any(map(lambda x: x in power_levels, ["hv", "mv"])):
                # In this case the Level 4 plants are assigned to the nearest hv/mv-transformer
                voronoi_polygons = voronoi(
                    grid_data.components_power.transformers.hv_mv[["dave_name", "geometry"]]
                )
                intersection = gpd.sjoin(conventionals_hv_mv, voronoi_polygons, how="inner")
                intersection.drop(columns=["index_right", "centroid"], inplace=True)
                intersection.rename(
                    columns={"dave_name": "trafo_name", "capacity_mw": "electrical_capacity_mw"},
                    inplace=True,
                )
                # search transformer bus lv name
                trafos = grid_data.components_power.transformers.hv_mv
                intersection["bus"] = intersection.trafo_name.apply(
                    lambda x: trafos[trafos.dave_name == x].iloc[0].bus_lv
                )
                # intersection = intersection.drop(columns=['index_right', 'centroid', 'trafo_name'])
                intersection.drop(columns=["trafo_name"], inplace=True)
                grid_data.components_power.conventional_powerplants = pd.concat(
                    [grid_data.components_power.conventional_powerplants, intersection],
                    ignore_index=True,
                )
            # find next higher and considered voltage level to assigne the hvmv-plants
            elif "ehv" in power_levels:
                # In this case the Level 4 plants are assigned to the nearest ehv/hv-transformer
                voronoi_polygons = voronoi(
                    grid_data.components_power.transformers.ehv_hv[["dave_name", "geometry"]]
                )
                intersection = gpd.sjoin(conventionals_hv_mv, voronoi_polygons, how="inner")
                intersection.drop(columns=["index_right"], inplace=True)
                intersection.rename(
                    columns={
                        "centroid": "connection_node",
                        "dave_name": "connection_trafo_dave_name",
                    },
                    inplace=True,
                )
                # change voltage level to the new connection level
                intersection.voltage_level = 2
                # select only data which is relevant after aggregation
                intersection_rel = intersection[
                    [
                        "capacity_mw",
                        "voltage_level",
                        "fuel",
                        "connection_node",
                        "connection_trafo_dave_name",
                    ]
                ]
                # aggregated power plants, set geometry and write them into grid data
                aggregate_plants_con(grid_data, intersection_rel, aggregate_name="level 4 plants")
        # update progress
        pbar.update(10)

        # --- nodes for level 3 plants (HV)
        if not conventionals_hv.empty:
            if "hv" in power_levels:
                # In this case the Level 3 plants are assigned to the nearest hv node
                voronoi_polygons = voronoi(grid_data.hv_data.hv_nodes[["dave_name", "geometry"]])
                intersection = gpd.sjoin(
                    conventionals_hv, voronoi_polygons, how="inner", op="intersects"
                )
                intersection.drop(columns=["index_right", "centroid"], inplace=True)
                intersection.rename(
                    columns={"dave_name": "bus", "capacity_mw": "electrical_capacity_mw"},
                    inplace=True,
                )
                grid_data.components_power.conventional_powerplants = pd.concat(
                    [grid_data.components_power.conventional_powerplants, intersection],
                    ignore_index=True,
                )
            # find next higher and considered voltage level to assigne the hv-plants
            elif "ehv" in power_levels:
                # In this case the Level 3 plants are assigned to the nearest ehv/hv-transformer
                voronoi_polygons = voronoi(
                    grid_data.components_power.transformers.ehv_hv[["dave_name", "geometry"]]
                )
                intersection = gpd.sjoin(conventionals_hv, voronoi_polygons, how="inner")
                intersection.drop(columns=["index_right"], inplace=True)
                intersection.rename(
                    columns={
                        "centroid": "connection_node",
                        "dave_name": "connection_trafo_dave_name",
                    },
                    inplace=True,
                )
                # change voltage level to the new connection level
                intersection.voltage_level = 2
                # select only data which is relevant after aggregation
                intersection_rel = intersection[
                    [
                        "capacity_mw",
                        "voltage_level",
                        "fuel",
                        "connection_node",
                        "connection_trafo_dave_name",
                    ]
                ]
                # aggregated power plants, set geometry and write them into grid data
                aggregate_plants_con(grid_data, intersection_rel, aggregate_name="level 3 plants")
        # update progress
        pbar.update(10)

        # --- nodes for level 2 plants (EHV/HV)
        if not conventionals_ehv_hv.empty:
            if any(map(lambda x: x in power_levels, ["ehv", "hv"])):
                # In this case the Level 2 plants are assigned to the nearest ehv/hv-transformer
                voronoi_polygons = voronoi(
                    grid_data.components_power.transformers.ehv_hv[["dave_name", "geometry"]]
                )
                intersection = gpd.sjoin(conventionals_ehv_hv, voronoi_polygons, how="inner")
                intersection.rename(
                    columns={"dave_name": "trafo_name", "capacity_mw": "electrical_capacity_mw"},
                    inplace=True,
                )
                # search transformer bus lv name
                trafos = grid_data.components_power.transformers.ehv_hv
                intersection["bus"] = intersection.trafo_name.apply(
                    lambda x: trafos[trafos.dave_name == x].iloc[0].bus_lv
                )
                intersection.drop(columns=["index_right", "centroid", "trafo_name"], inplace=True)
                grid_data.components_power.conventional_powerplants = pd.concat(
                    [grid_data.components_power.conventional_powerplants, intersection],
                    ignore_index=True,
                )
        # update progress
        pbar.update(10)

        # --- nodes for level 1 plants (EHV)
        if not conventionals_ehv.empty:
            if "ehv" in power_levels:
                # In this case the Level 1 plants are assigned to the nearest ehv node
                voronoi_polygons = voronoi(grid_data.ehv_data.ehv_nodes[["dave_name", "geometry"]])
                intersection = gpd.sjoin(conventionals_ehv, voronoi_polygons, how="inner")
                intersection.drop(columns=["index_right", "centroid"], inplace=True)
                intersection.rename(
                    columns={"dave_name": "bus", "capacity_mw": "electrical_capacity_mw"},
                    inplace=True,
                )
                grid_data.components_power.conventional_powerplants = pd.concat(
                    [grid_data.components_power.conventional_powerplants, intersection],
                    ignore_index=True,
                )
        # --- add general informations
        if not grid_data.components_power.conventional_powerplants.empty:
            # add dave name
            name = grid_data.components_power.conventional_powerplants.apply(
                lambda x: f"con_powerplant_{x.voltage_level}_{x.name}", axis=1
            )
            grid_data.components_power.conventional_powerplants.insert(0, "dave_name", name)
            # set crs
            grid_data.components_power.conventional_powerplants.set_crs(
                dave_settings()["crs_main"], inplace=True
            )
        # update progress
        pbar.update(10)
    else:
        # update progress
        pbar.update(90)
    # close progress bar
    pbar.close()
