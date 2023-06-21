# Copyright (c) 2022-2023 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from math import pi

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString
from tqdm import tqdm

from dave.datapool.oep_request import oep_request
from dave.datapool.read_data import read_ehv_data
from dave.settings import dave_settings
from dave.toolbox import intersection_with_area, related_sub


def create_ehv_topology(grid_data):
    """
    This function creates a dictonary with all relevant parameters for the
    extra high voltage level

    INPUT:
        **grid_data** (dict) - all Informations about the grid area

    OUTPUT:
        Writes data in the DaVe dataset
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create extra high voltage topology:",
        position=0,
        bar_format=dave_settings()["bar_format"],
    )
    # --- create ehv/ehv and ehv/hv substations
    # read ehv substation data from OpenEnergyPlatform and adapt names
    ehv_substations, meta_data = oep_request(table="ego_dp_ehv_substation")
    # add meta data
    if bool(meta_data) and f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
        grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
    ehv_substations.rename(
        columns={"version": "ego_version", "subst_id": "ego_subst_id", "voltage": "voltage_kv"},
        inplace=True,
    )
    # filter substations which are within the grid area
    ehv_substations = intersection_with_area(ehv_substations, grid_data.area)
    # update progress
    pbar.update(10)
    if not ehv_substations.empty:
        ehv_substations["voltage_level"] = 2
        # add dave name
        ehv_substations.reset_index(drop=True, inplace=True)
        ehv_substations.insert(
            0,
            "dave_name",
            pd.Series(list(map(lambda x: f"substation_2_{x}", ehv_substations.index))),
        )
        # set crs
        ehv_substations.set_crs(dave_settings()["crs_main"], inplace=True)
        # add ehv substations to grid data
        grid_data.components_power.substations.ehv_hv = pd.concat(
            [grid_data.components_power.substations.ehv_hv, ehv_substations], ignore_index=True
        )
    # update progress
    pbar.update(10)
    # --- import ehv lines and reduce them to the target area
    ehvhv_lines, meta_data = oep_request(table="ego_pf_hv_line")
    # add meta data
    if bool(meta_data) and f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
        grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
    ehvhv_lines.rename(
        columns={
            "version": "ego_version",
            "subst_id": "ego_subst_id",
            "scn_name": "ego_scn_name",
            "line_id": "ego_line_id",
            "length": "length_km",
            "s_nom": "s_nom_mva",
            "r": "r_ohm",
            "x": "x_ohm",
            "g": "g_s",
            "b": "b_s",
            "bus0": "from_bus",
            "bus1": "to_bus",
        },
        inplace=True,
    )
    # filter lines which are currently availible
    ehvhv_lines = ehvhv_lines[
        (ehvhv_lines.ego_scn_name == "Status Quo")
        & (ehvhv_lines.geometry.intersects(grid_data.area.geometry.unary_union))
    ]
    # consider data only if there are minimum one line in the target area
    if not ehvhv_lines.empty:
        # --- create ehv nodes
        # read ehv/hv node data from OpenEnergyPlatform and adapt names
        ehvhv_buses, meta_data = oep_request(table="ego_pf_hv_bus")
        # add meta data
        if (
            bool(meta_data)
            and f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys()
        ):
            grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        ehvhv_buses.rename(
            columns={
                "version": "ego_version",
                "scn_name": "ego_scn_name",
                "bus_id": "ego_bus_id",
                "v_nom": "voltage_kv",
                "length": "length_km",
            },
            inplace=True,
        )
        # filter nodes which are on the ehv-level and current exsist
        ehv_buses = ehvhv_buses[
            (ehvhv_buses.voltage_kv.isin([380, 220])) & (ehvhv_buses.ego_scn_name == "Status Quo")
        ]
        # filter nodes within the target area by checking their connection to a line
        line_buses_ids = pd.concat(
            [ehvhv_lines.from_bus, ehvhv_lines.to_bus], ignore_index=True
        ).unique()
        ehv_buses = ehv_buses[ehv_buses.ego_bus_id.isin(line_buses_ids)]
    else:
        # create empty DataFrame for the next check
        ehv_buses = gpd.GeoDataFrame()
    # update progress
    pbar.update(10)
    # consider data only if there are more than one ehv node in the target area
    if len(ehv_buses) > 1:
        # search for the substations where the ehv nodes are within
        sub_infos = ehv_buses.geometry.apply(lambda x: related_sub(x, ehv_substations))
        ehv_buses["ego_subst_id"] = sub_infos.apply(lambda x: x[0])
        ehv_buses["subst_dave_name"] = sub_infos.apply(lambda x: x[1])
        ehv_buses["subst_name"] = sub_infos.apply(lambda x: x[2])
        # update progress
        pbar.update(10)
        """ the license of the open tso data is not clarified
        # read ehv tso data
        ehv_data, meta_data = read_ehv_data()
        # add meta data
        if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
            grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        # assign tso ehv node names to the ego ehv nodes
        for _, node in ehv_data["ehv_nodes"].iterrows():
            if node.osm_id:
                substation = ehv_substations[ehv_substations.osm_id == "w" + node.osm_id]
                if not substation.empty:
                    ehv_buses_index = ehv_buses[
                        ehv_buses.ego_subst_id == substation.iloc[0].ego_subst_id
                    ].index
                    for index in ehv_buses_index:
                        ehv_buses.at[index, "tso_name"] = (
                            node["name"].replace("_380", "").replace("_220", "")
                        )
                        ehv_buses.at[index, "tso"] = node["tso"]
            else:
                # search for tso connection points in ego ehv nodes by a minimal distance
                for _, bus in ehv_buses.iterrows():
                    distance = node.geometry.distance(bus.geometry)
                    if distance < 2e-03:
                        ehv_buses.at[bus.name, "tso_name"] = (
                            node["name"].replace("_380", "").replace("_220", "")
                        )
                        ehv_buses.at[bus.name, "tso"] = node["tso"]
                        break
            # update progress
            pbar.update(10 / len(ehv_data["ehv_nodes"]))
        """
        # add oep as source
        ehv_buses["source"] = "OEP"
        """ the license of the open tso data is not clarified
        # add missing tso ehv nodes which are not in the ego node data
        ehv_buses_tso_names = ehv_buses.tso_name.to_list()
        area = grid_data.area.drop(columns=['name']) if 'name' in grid_data.area.keys() \
            else grid_data.area
        # filter nodes which are within the grid area
        ehv_buses_tso = intersection_with_area(ehv_data['ehv_nodes'], area, remove_columns=False)
        for _, tso_bus in ehv_buses_tso.iterrows():
            tso_name = tso_bus['name'].replace('_380', '').replace('_220', '')
            if tso_name not in ehv_buses_tso_names:
                ehv_buses = ehv_buses.append(gpd.GeoDataFrame({'voltage_kv': tso_bus.voltage_kv,
                                                               'geometry': [tso_bus.geometry],
                                                               'subst_name': tso_bus.name_osm,
                                                               'tso_name': tso_name,
                                                               'tso': tso_bus.tso,
                                                               'source': 'tso data'}))
        """
        # update progress
        pbar.update(10)
        # add voltage level
        ehv_buses["voltage_level"] = 1
        # add dave name
        ehv_buses.reset_index(drop=True, inplace=True)
        ehv_buses.insert(
            0, "dave_name", pd.Series(list(map(lambda x: f"node_1_{x}", ehv_buses.index)))
        )
        # set crs
        ehv_buses.set_crs(dave_settings()["crs_main"], inplace=True)
        # add ehv nodes to grid data
        grid_data.ehv_data.ehv_nodes = pd.concat(
            [grid_data.ehv_data.ehv_nodes, ehv_buses], ignore_index=True
        )

        # --- create ehv lines
        # filter lines which are on the ehv level by check if both endpoints are on the ehv level
        ehv_bus_ids = ehv_buses.ego_bus_id.tolist()
        ehv_lines = ehvhv_lines[
            (ehvhv_lines.from_bus.isin(ehv_bus_ids)) & (ehvhv_lines.to_bus.isin(ehv_bus_ids))
        ]
        # --- add additional line parameter and change bus names
        ehv_lines.insert(ehv_lines.columns.get_loc("r_ohm") + 1, "r_ohm_per_km", None)
        ehv_lines.insert(ehv_lines.columns.get_loc("x_ohm") + 1, "x_ohm_per_km", None)
        ehv_lines.insert(ehv_lines.columns.get_loc("b_s") + 1, "c_nf_per_km", None)
        ehv_lines.insert(ehv_lines.columns.get_loc("b_s") + 1, "c_nf", None)
        # update progress
        pbar.update(10)
        from_bus_new = []
        to_bus_new = []
        for _, line in ehv_lines.iterrows():
            # add voltage
            line_voltage = ehv_buses.loc[
                ehv_buses[ehv_buses.ego_bus_id == line.from_bus].index[0]
            ].voltage_kv
            ehv_lines.at[line.name, "voltage_kv"] = line_voltage
            # change line bus names from ego id to dave name
            from_bus_new.append(ehv_buses[ehv_buses.ego_bus_id == line.from_bus].iloc[0].dave_name)
            to_bus_new.append(ehv_buses[ehv_buses.ego_bus_id == line.to_bus].iloc[0].dave_name)
            # calculate and add r,x,c per km
            ehv_lines.at[line.name, "r_ohm_per_km"] = float(line.r_ohm) / line.length_km
            ehv_lines.at[line.name, "x_ohm_per_km"] = float(line.x_ohm) / line.length_km
            c_nf = float(line.b_s) / (2 * pi * float(line.frequency)) * 1e09
            ehv_lines.at[line.name, "c_nf"] = c_nf
            ehv_lines.at[line.name, "c_nf_per_km"] = c_nf / line.length_km
            # calculate and add max i
            ehv_lines.at[line.name, "max_i_ka"] = (
                (float(line.s_nom_mva) * 1e06) / (line_voltage * 1e03)
            ) * 1e-03
            # parallel lines
            ehv_lines.at[line.name, "parallel"] = line.cables / 3
            # update progress
            pbar.update(20 / len(ehv_lines))
        ehv_lines["from_bus"] = from_bus_new
        ehv_lines["to_bus"] = to_bus_new
        # add oep as source
        ehv_lines["source"] = "OEP"
        ehv_lines["voltage_level"] = 1
        # update progress
        pbar.update(30)
        """ the license of the open tso data is not clarified
        # add missing tso ehv lines which are not in the ego line data
        ehv_buses_from_tso = ehv_buses[ehv_buses.source == 'tso data'].tso_name.tolist()
        for _, line in ehv_data['ehv_lines'].iterrows():
            from_bus = line.from_bus_voltage.replace('_380', '').replace('_220', '')
            to_bus = line.to_bus_voltage.replace('_380', '').replace('_220', '')
            if (((from_bus in ehv_buses_from_tso) and (to_bus in ehv_buses_tso_names)) or
               ((to_bus in ehv_buses_from_tso) and (from_bus in ehv_buses_tso_names)) or
               ((from_bus in ehv_buses_from_tso) and (to_bus in ehv_buses_from_tso))):
                g_s = line.g_us*1E-06 if str(line.g_us) != 'nan' else line.g_us
                b_s = line.b_us*1E-06 if str(line.b_us) != 'nan' else line.b_us
                # search for the buses with the right voltage level
                from_bus = ehv_buses[ehv_buses.tso_name == from_bus]
                to_bus = ehv_buses[ehv_buses.tso_name == to_bus]
                # find the bus with the right voltage
                from_bus = from_bus[from_bus.voltage_kv == line.vn_kv]
                to_bus = to_bus[to_bus.voltage_kv == line.vn_kv]
                if (not from_bus.empty) and (not to_bus.empty):
                    ehv_lines = ehv_lines.append(gpd.GeoDataFrame(
                        {'from_bus': from_bus.iloc[0].dave_name,
                         'to_bus': to_bus.iloc[0].dave_name,
                         'x_ohm': line.x_ohm,
                         'x_ohm_per_km': line.x_ohm_per_km,
                         'r_ohm': line.r_ohm,
                         'r_ohm_per_km': line.r_ohm_per_km,
                         'g_s': g_s,
                         'b_s': b_s,
                         'c_nf': line.c_uf,
                         'c_nf_per_km': line.c_nf_per_km,
                         'length_km': line.length_km,
                         'geometry': [LineString([from_bus.iloc[0].geometry,
                                                  to_bus.iloc[0].geometry])],
                         'voltage_kv': line.vn_kv,
                         'max_i_ka': line.max_i_ka,
                         'source': 'tso data',
                         'parallel': 1}))
        """
        # add dave name
        ehv_lines.reset_index(drop=True, inplace=True)
        ehv_lines.insert(
            0, "dave_name", pd.Series(list(map(lambda x: f"line_1_{x}", ehv_lines.index)))
        )
        # set crs
        ehv_lines.set_crs(dave_settings()["crs_main"], inplace=True)
        # add ehv lines to grid data
        grid_data.ehv_data.ehv_lines = pd.concat(
            [grid_data.ehv_data.ehv_lines, ehv_lines], ignore_index=True
        )
        # update progress
        pbar.update(19.999)
    else:
        # update progress
        pbar.update(70)
    # close progress bar
    pbar.close()
