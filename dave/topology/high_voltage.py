# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from math import pi

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point
from tqdm import tqdm

from dave.datapool.oep_request import oep_request
from dave.settings import dave_settings
from dave.toolbox import intersection_with_area, related_sub


def create_hv_topology(grid_data):
    """
    This function creates a dictonary with all relevant parameters for the
    high voltage level

    INPUT:
        **grid_data** (dict) - all Informations about the grid area

    OUTPUT:
        Writes data in the DaVe dataset
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create high voltage topology:      ",
        position=0,
        bar_format=dave_settings()["bar_format"],
    )

    # --- create substations
    # create ehv/hv substations
    if grid_data.components_power.substations.ehv_hv.empty:
        ehvhv_substations, meta_data = oep_request(table="ego_dp_ehv_substation")
        # add meta data
        if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
            grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        ehvhv_substations.rename(
            columns={"version": "ego_version", "subst_id": "ego_subst_id", "voltage": "voltage_kv"},
            inplace=True,
        )
        # filter ehv/hv substations
        ehvhv_substations = ehvhv_substations[
            pd.Series(list(map(lambda x: bool("110000" in x), ehvhv_substations.voltage_kv)))
        ]
        # filter substations which are within the grid area
        ehvhv_substations = intersection_with_area(ehvhv_substations, grid_data.area)
        if not ehvhv_substations.empty:
            ehvhv_substations["voltage_level"] = 2
            # add dave name
            ehvhv_substations.reset_index(drop=True, inplace=True)
            ehvhv_substations.insert(
                0,
                "dave_name",
                pd.Series(list(map(lambda x: f"substation_2_{x}", ehvhv_substations.index))),
            )
            # set crs
            ehvhv_substations.set_crs(dave_settings()["crs_main"], inplace=True)
            # add ehv substations to grid data
            grid_data.components_power.substations.ehv_hv = pd.concat(
                [grid_data.components_power.substations.ehv_hv, ehvhv_substations],
                ignore_index=True,
            )
    else:
        ehvhv_substations = grid_data.components_power.substations.ehv_hv.copy()
    # update progress
    pbar.update(20)
    # create hv/mv substations
    if grid_data.components_power.substations.hv_mv.empty:
        hvmv_substations, meta_data = oep_request(
            table="ego_dp_hvmv_substation"
        )  # take polygon for full area
        # add meta data
        if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
            grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        hvmv_substations.rename(
            columns={
                "version": "ego_version",
                "subst_id": "ego_subst_id",
                "voltage": "voltage_kv",
                "ags_0": "Gemeindeschluessel",
            },
            inplace=True,
        )
        # filter substations with point as geometry
        hvmv_substations.drop(
            hvmv_substations[
                hvmv_substations.geometry.apply(lambda x: isinstance(x, (Point, LineString)))
            ].index.values,
            inplace=True,
        )
        # filter substations which are within the grid area
        hvmv_substations = intersection_with_area(hvmv_substations, grid_data.area)
        if not hvmv_substations.empty:
            hvmv_substations["voltage_level"] = 4
            # add dave name
            hvmv_substations.reset_index(drop=True, inplace=True)
            hvmv_substations.insert(
                0,
                "dave_name",
                pd.Series(list(map(lambda x: f"substation_4_{x}", hvmv_substations.index))),
            )
            # set crs
            hvmv_substations.set_crs(dave_settings()["crs_main"], inplace=True)
            # add ehv substations to grid data
            grid_data.components_power.substations.hv_mv = pd.concat(
                [grid_data.components_power.substations.hv_mv, hvmv_substations], ignore_index=True
            )
    else:
        hvmv_substations = grid_data.components_power.substations.hv_mv.copy()
    # update progress
    pbar.update(20)
    # --- import hv lines and reduce them to the target area
    ehvhv_lines, meta_data = oep_request(table="ego_pf_hv_line")
    # add meta data
    if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
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
    # filter lines which are currently available and within the considered area
    ehvhv_lines = ehvhv_lines[
        (ehvhv_lines.ego_scn_name == "Status Quo")
        & (ehvhv_lines.geometry.intersects(grid_data.area.geometry.unary_union))
    ]
    # update progress
    pbar.update(10)
    # consider data only if there are minimum one line in the target area
    if not ehvhv_lines.empty:
        # --- create hv nodes
        ehvhv_buses, meta_data = oep_request(table="ego_pf_hv_bus")
        # add meta data
        if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
            grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        ehvhv_buses.rename(
            columns={
                "version": "ego_version",
                "scn_name": "ego_scn_name",
                "bus_id": "ego_bus_id",
                "v_nom": "voltage_kv",
            },
            inplace=True,
        )
        # filter nodes which are on the hv level and current exsist
        hv_buses = ehvhv_buses[
            (ehvhv_buses.voltage_kv == 110) & (ehvhv_buses.ego_scn_name == "Status Quo")
        ]
        # filter nodes within the target area by checking their connection to a line
        line_buses_ids = pd.concat(
            [ehvhv_lines.from_bus, ehvhv_lines.to_bus], ignore_index=True
        ).unique()
        hv_buses = hv_buses[hv_buses.ego_bus_id.isin(line_buses_ids)]
    else:
        # create empty DataFrame for the next check
        hv_buses = gpd.GeoDataFrame()
    # update progress
    pbar.update(10)
    # consider data only if there are more than one node in the target area
    if len(hv_buses) > 1:
        hv_buses["voltage_level"] = 3
        hv_buses = hv_buses.drop(columns=(["current_type", "v_mag_pu_min", "v_mag_pu_max", "geom"]))
        # search for the substations where the hv nodes are within
        substations_rel = pd.concat([ehvhv_substations, hvmv_substations], ignore_index=True)
        sub_infos = hv_buses.geometry.apply(lambda x: related_sub(x, substations_rel))
        hv_buses.insert(0, "ego_subst_id", sub_infos.apply(lambda x: x[0]))
        hv_buses.insert(1, "subst_dave_name", sub_infos.apply(lambda x: x[1]))
        hv_buses.insert(2, "subst_name", sub_infos.apply(lambda x: x[2]))
        # update progress
        pbar.update(10)
        # add oep as source
        hv_buses["source"] = "OEP"
        # add dave name
        hv_buses.reset_index(drop=True, inplace=True)
        hv_buses.insert(
            0, "dave_name", pd.Series(list(map(lambda x: f"node_3_{x}", hv_buses.index)))
        )
        # set crs
        hv_buses.set_crs(dave_settings()["crs_main"], inplace=True)
        # add hv nodes to grid data
        grid_data.hv_data.hv_nodes = pd.concat(
            [grid_data.hv_data.hv_nodes, hv_buses], ignore_index=True
        )
        # update progress
        pbar.update(10)

        # --- create hv lines
        # filter lines which are on the hv level by check if both endpoints are on the hv level
        hv_bus_ids = hv_buses.ego_bus_id.tolist()
        hv_lines = ehvhv_lines[
            (ehvhv_lines.from_bus.isin(hv_bus_ids)) & (ehvhv_lines.to_bus.isin(hv_bus_ids))
        ]
        # --- add additional line parameter and change bus names
        hv_lines.insert(
            hv_lines.columns.get_loc("r_ohm") + 1,
            "r_ohm_per_km",
            hv_lines.r_ohm.astype("float") / hv_lines.length_km,
        )
        hv_lines.insert(
            hv_lines.columns.get_loc("x_ohm") + 1,
            "x_ohm_per_km",
            hv_lines.x_ohm.astype("float") / hv_lines.length_km,
        )
        c_nf = hv_lines.b_s.astype("float") / (2 * pi * hv_lines.frequency.astype("float")) * 1e09
        hv_lines.insert(hv_lines.columns.get_loc("b_s") + 1, "c_nf", c_nf)
        hv_lines.insert(
            hv_lines.columns.get_loc("c_nf") + 1, "c_nf_per_km", c_nf / hv_lines.length_km
        )
        hv_lines["voltage_kv"] = 110
        hv_lines["max_i_ka"] = (
            hv_lines.s_nom_mva.astype("float") * 1e06 / (hv_lines.voltage_kv * 1e03)
        ) * 1e-03
        hv_lines["parallel"] = hv_lines.cables / 3
        hv_lines["from_bus"] = hv_lines.from_bus.apply(
            lambda x: hv_buses[hv_buses.ego_bus_id == x].iloc[0].dave_name
        )
        hv_lines["to_bus"] = hv_lines.to_bus.apply(
            lambda x: hv_buses[hv_buses.ego_bus_id == x].iloc[0].dave_name
        )
        hv_lines["source"] = "OEP"
        hv_lines["voltage_level"] = 3
        # update progress
        pbar.update(10)
        # add dave name
        hv_lines.reset_index(drop=True, inplace=True)
        name = pd.Series(list(map(lambda x: f"line_3_{x}", hv_lines.index)))
        hv_lines.insert(0, "dave_name", name)
        # set crs
        hv_lines.set_crs(dave_settings()["crs_main"], inplace=True)
        # add hv lines to grid data
        grid_data.hv_data.hv_lines = pd.concat(
            [grid_data.hv_data.hv_lines, hv_lines], ignore_index=True
        )
        # update progress
        pbar.update(9.999)
    else:
        # update progress
        pbar.update(40)
    # close progress bar
    pbar.close()
