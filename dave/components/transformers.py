# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import geopandas as gpd
import pandas as pd
from shapely import wkb
from shapely.geometry import LineString, MultiPoint, Point
from shapely.ops import nearest_points
from tqdm import tqdm

from dave.datapool import oep_request
from dave.settings import dave_settings


def create_transformers(grid_data):
    """
    This function collects the transformers.
    EHV/EHV and EHV/HV trafos are based on ego_pf_hv_transformer from OEP
    HV/MV trafos are based on ego_dp_hvmv_substation from OEP
    MV/LV trafos are based on ego_dp_mvlv_substation from OEP
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create transformers:               ",
        position=0,
        bar_format=dave_settings()["bar_format"],
    )
    # define power_levels
    power_levels = grid_data.target_input.power_levels[0]
    # --- create ehv/ehv and ehv/hv trafos
    if any(map(lambda x: x in power_levels, ["ehv", "hv"])):
        # read transformator data from OEP, filter current exsist ones and rename paramter names
        hv_trafos, meta_data = oep_request(
            schema="grid",
            table="ego_pf_hv_transformer",
            where=dave_settings()["ehvhv_trans_ver"],
            geometry="geom",
        )
        # add meta data
        if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
            grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        hv_trafos.rename(
            columns={
                "version": "ego_version",
                "scn_name": "ego_scn_name",
                "trafo_id": "ego_trafo_id",
                "s_nom": "s_nom_mva",
            },
            inplace=True,
        )
        hv_trafos = hv_trafos[hv_trafos.ego_scn_name == "Status Quo"]
        # change geometry to point because in original data the geometry was lines with length 0
        hv_trafos["geometry"] = hv_trafos.geometry.apply(
            lambda x: Point(x.geoms[0].coords[:][0][0], x.geoms[0].coords[:][0][1])
        )
        # check for transformer in the target area
        hv_trafos = gpd.overlay(hv_trafos, grid_data.area, how="intersection")
        if not hv_trafos.empty:
            remove_columns = grid_data.area.keys().tolist()
            remove_columns.remove("geometry")
            hv_trafos.drop(columns=remove_columns, inplace=True)
        # update progress
        pbar.update(5)
        # in case of missing ehv/hv-level, nodes for the transformator must be procured from OEP
        if ("ehv" in power_levels and grid_data.hv_data.hv_nodes.empty) or (
            "hv" in power_levels and grid_data.ehv_data.ehv_nodes.empty
        ):
            # read ehv/hv node data from OpenEnergyPlatform and adapt names
            ehvhv_buses, meta_data = oep_request(
                schema="grid",
                table="ego_pf_hv_bus",
                where=dave_settings()["hv_buses_ver"],
                geometry="geom",
            )
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
            ehvhv_buses = ehvhv_buses[ehvhv_buses.ego_scn_name == "Status Quo"]
            ehvhv_buses = gpd.overlay(ehvhv_buses, grid_data.area, how="intersection")
            if not ehvhv_buses.empty:
                remove_columns = grid_data.area.keys().tolist()
                remove_columns.remove("geometry")
                ehvhv_buses.drop(columns=remove_columns, inplace=True)
        # update progress
        pbar.update(5)
        # search for trafo voltage and create missing nodes
        for i, trafo in hv_trafos.iterrows():
            if "ehv" in power_levels:
                ehv_bus0 = grid_data.ehv_data.ehv_nodes[
                    grid_data.ehv_data.ehv_nodes.ego_bus_id == trafo.bus0
                ]
                ehv_bus1 = grid_data.ehv_data.ehv_nodes[
                    grid_data.ehv_data.ehv_nodes.ego_bus_id == trafo.bus1
                ]
                if not ehv_bus0.empty:
                    hv_trafos.at[trafo.name, "voltage_kv_lv"] = grid_data.ehv_data.ehv_nodes.loc[
                        ehv_bus0.index[0]
                    ].voltage_kv
                if not ehv_bus1.empty:
                    hv_trafos.at[trafo.name, "voltage_kv_hv"] = grid_data.ehv_data.ehv_nodes.loc[
                        ehv_bus1.index[0]
                    ].voltage_kv
                if ("hv" not in power_levels) and (ehv_bus0.empty):
                    hv_buses = ehvhv_buses[ehvhv_buses.voltage_kv.isin([110])]
                    hv_bus0 = hv_buses[hv_buses.ego_bus_id == trafo.bus0]
                    if not hv_bus0.empty:
                        hv_trafos.at[trafo.name, "voltage_kv_lv"] = hv_buses.loc[
                            hv_bus0.index[0]
                        ].voltage_kv
                        # check if node allready exsist, otherwise create them
                        if grid_data.hv_data.hv_nodes.empty:
                            hv_bus0["voltage_level"] = 3
                            hv_bus0["source"] = "OEP"
                            grid_data.hv_data.hv_nodes = pd.concat(
                                [grid_data.hv_data.hv_nodes, hv_bus0], ignore_index=True
                            )
                        elif grid_data.hv_data.hv_nodes[
                            grid_data.hv_data.hv_nodes.ego_bus_id == trafo.bus0
                        ].empty:
                            hv_bus0["voltage_level"] = 3
                            hv_bus0["source"] = "OEP"
                            grid_data.hv_data.hv_nodes = pd.concat(
                                [grid_data.hv_data.hv_nodes, hv_bus0], ignore_index=True
                            )
            if "hv" in power_levels:
                hv_bus0 = grid_data.hv_data.hv_nodes[
                    grid_data.hv_data.hv_nodes.ego_bus_id == trafo.bus0
                ]
                if not hv_bus0.empty:
                    hv_trafos.at[trafo.name, "voltage_kv_lv"] = grid_data.hv_data.hv_nodes.loc[
                        hv_bus0.index[0]
                    ].voltage_kv
                if ("ehv" not in power_levels) and (not hv_bus0.empty):
                    ehv_buses = ehvhv_buses[ehvhv_buses.voltage_kv.isin([380, 220])]
                    ehv_bus1 = ehv_buses[ehv_buses.ego_bus_id == trafo.bus1]
                    if not ehv_bus1.empty:
                        hv_trafos.at[trafo.name, "voltage_kv_hv"] = ehv_buses.loc[
                            ehv_bus1.index[0]
                        ].voltage_kv
                        # check if node allready exsist, otherwise create them
                        if grid_data.ehv_data.ehv_nodes.empty:
                            ehv_bus1["voltage_level"] = 1
                            ehv_bus1["source"] = "OEP"
                            grid_data.ehv_data.ehv_nodes = pd.concat(
                                [grid_data.ehv_data.ehv_nodes, ehv_bus1], ignore_index=True
                            )
                        elif grid_data.ehv_data.ehv_nodes[
                            grid_data.ehv_data.ehv_nodes.ego_bus_id == trafo.bus1
                        ].empty:
                            ehv_bus1["voltage_level"] = 1
                            ehv_bus1["source"] = "OEP"
                            grid_data.ehv_data.ehv_nodes = pd.concat(
                                [grid_data.ehv_data.ehv_nodes, ehv_bus1], ignore_index=True
                            )
            # update progress
            pbar.update(10 / len(hv_trafos))
        # add dave name for nodes which are created for the transformers
        if "dave_name" not in grid_data.hv_data.hv_nodes.keys():
            grid_data.hv_data.hv_nodes.reset_index(drop=True, inplace=True)
            name = pd.Series(list(map(lambda x: f"node_3_{x}", grid_data.hv_data.hv_nodes.index)))
            grid_data.hv_data.hv_nodes.insert(0, "dave_name", name)
            grid_data.hv_data.hv_nodes.set_crs(dave_settings()["crs_main"], inplace=True)
        if "dave_name" not in grid_data.ehv_data.ehv_nodes.keys():
            grid_data.ehv_data.ehv_nodes.reset_index(drop=True, inplace=True)
            name = pd.Series(list(map(lambda x: f"node_1_{x}", grid_data.ehv_data.ehv_nodes.index)))
            grid_data.ehv_data.ehv_nodes.insert(0, "dave_name", name)
            grid_data.ehv_data.ehv_nodes.set_crs(dave_settings()["crs_main"], inplace=True)
        # write transformator data in grid data and decied the grid level depending on voltage level
        if not hv_trafos.empty:
            ehv_buses = grid_data.ehv_data.ehv_nodes
            hv_buses = grid_data.hv_data.hv_nodes
            if "ehv" in power_levels:
                ehv_ehv_trafos = hv_trafos[hv_trafos.voltage_kv_lv.isin([380, 220])]
                ehv_ehv_trafos["voltage_level"] = 1
                # add dave name for trafo and connection buses
                ehv_ehv_trafos.insert(0, "dave_name", None)
                ehv_ehv_trafos.insert(1, "bus_hv", None)
                ehv_ehv_trafos.insert(2, "bus_lv", None)
                ehv_ehv_trafos["substation_name"] = None
                ehv_ehv_trafos["tso_name"] = None
                ehv_ehv_trafos.reset_index(drop=True, inplace=True)
                for i, trafo in ehv_ehv_trafos.iterrows():
                    ehv_ehv_trafos.at[trafo.name, "dave_name"] = f"trafo_1_{i}"
                    # search for bus dave name and replace ego id
                    bus0 = ehv_buses[ehv_buses.ego_bus_id == trafo.bus0].iloc[0]
                    bus1 = ehv_buses[ehv_buses.ego_bus_id == trafo.bus1].iloc[0]
                    ehv_ehv_trafos.at[trafo.name, "bus_lv"] = bus0.dave_name
                    ehv_ehv_trafos.at[trafo.name, "bus_hv"] = bus1.dave_name
                    ehv_ehv_trafos.at[trafo.name, "substation_name"] = bus0.subst_name
                    ehv_ehv_trafos.at[trafo.name, "tso_name"] = bus0.tso_name
                # drop columns with ego_id
                ehv_ehv_trafos.drop(columns=["bus0", "bus1"], inplace=True)
                # set crs
                ehv_ehv_trafos.set_crs(dave_settings()["crs_main"], inplace=True)
                # add ehv/ehv trafos to grid data
                grid_data.components_power.transformers.ehv_ehv = pd.concat(
                    [grid_data.components_power.transformers.ehv_ehv, ehv_ehv_trafos],
                    ignore_index=True,
                )
            ehv_hv_trafos = hv_trafos[hv_trafos.voltage_kv_lv == 110]
            ehv_hv_trafos["voltage_level"] = 2
            # add dave name trafo and connection buses
            ehv_hv_trafos.insert(0, "dave_name", None)
            ehv_hv_trafos.insert(1, "bus_hv", None)
            ehv_hv_trafos.insert(2, "bus_lv", None)
            ehv_hv_trafos["substation_name"] = None
            ehv_hv_trafos["tso_name"] = None
            ehv_hv_trafos.reset_index(drop=True, inplace=True)
            for i, trafo in ehv_hv_trafos.iterrows():
                ehv_hv_trafos.at[trafo.name, "dave_name"] = f"trafo_2_{i}"
                # search for bus dave name and replace ego id
                bus0 = hv_buses[hv_buses.ego_bus_id == trafo.bus0].iloc[0]
                bus1 = ehv_buses[ehv_buses.ego_bus_id == trafo.bus1].iloc[0]
                ehv_hv_trafos.at[trafo.name, "bus_lv"] = bus0.dave_name
                ehv_hv_trafos.at[trafo.name, "bus_hv"] = bus1.dave_name
                ehv_hv_trafos.at[trafo.name, "substation_name"] = bus1.subst_name
                ehv_hv_trafos.at[trafo.name, "tso_name"] = bus1.tso_name
            # change column name
            ehv_hv_trafos.drop(columns=["bus0", "bus1"], inplace=True)
            # set crs
            ehv_hv_trafos.set_crs(dave_settings()["crs_main"], inplace=True)
            # add ehv/ehv trafos to grid data
            grid_data.components_power.transformers.ehv_hv = pd.concat(
                [grid_data.components_power.transformers.ehv_hv, ehv_hv_trafos], ignore_index=True
            )
        # update progress
        pbar.update(10)
    else:
        # update progress
        pbar.update(30)

    # --- create hv/mv trafos
    if any(map(lambda x: x in power_levels, ["hv", "mv"])):
        if grid_data.components_power.substations.hv_mv.empty:
            # read transformator data from OEP, filter relevant parameters and rename paramter names
            substations, meta_data = oep_request(
                schema="grid",
                table="ego_dp_hvmv_substation",
                where=dave_settings()["hvmv_sub_ver"],
                geometry="polygon",
            )  # polygon to get the full area
            # add meta data
            if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
                grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
            substations.rename(
                columns={
                    "version": "ego_version",
                    "subst_id": "ego_subst_id",
                    "voltage": "voltage_kv",
                    "ags_0": "Gemeindeschluessel",
                },
                inplace=True,
            )
            # filter substations with point as geometry
            drop_substations = [
                sub.name
                for i, sub in substations.iterrows()
                if isinstance(sub.geometry, (Point, LineString))
            ]
            substations.drop(drop_substations, inplace=True)
            # check for substations in the target area
            substations = gpd.overlay(substations, grid_data.area, how="intersection")
            if not substations.empty:
                remove_columns = grid_data.area.keys().tolist()
                remove_columns.remove("geometry")
                substations.drop(columns=remove_columns, inplace=True)
        else:
            substations = grid_data.components_power.substations.hv_mv.copy()
        substations.drop(
            columns=[
                "power_type",
                "substation",
                "frequency",
                "ref",
                "dbahn",
                "status",
                "otg_id",
                "geom",
            ],
            inplace=True,
        )
        # update progress
        pbar.update(10)
        # --- prepare hv nodes for the transformers
        # check if the hv nodes already exist, otherwise create them
        if grid_data.hv_data.hv_nodes.empty:
            # --- in this case the missing hv nodes for the transformator must be procured from OEP
            # read hv node data from OpenEnergyPlatform and adapt names
            hv_nodes, meta_data = oep_request(
                schema="grid",
                table="ego_pf_hv_bus",
                where=dave_settings()["hv_buses_ver"],
                geometry="geom",
            )
            # add meta data
            if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
                grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
            hv_nodes.rename(
                columns={
                    "version": "ego_version",
                    "scn_name": "ego_scn_name",
                    "bus_id": "ego_bus_id",
                    "v_nom": "voltage_kv",
                },
                inplace=True,
            )
            # filter nodes which are on the hv level, current exsist and within the target area
            hv_nodes = hv_nodes[
                (hv_nodes.voltage_kv == 110) & (hv_nodes.ego_scn_name == "Status Quo")
            ]
            hv_nodes = gpd.overlay(hv_nodes, grid_data.area, how="intersection")
            if not hv_nodes.empty:
                remove_columns = grid_data.area.keys().tolist()
                remove_columns.remove("geometry")
                hv_nodes = hv_nodes.drop(columns=remove_columns)
            hv_nodes["voltage_level"] = 3
            hv_nodes["source"] = "OEP"
            hv_nodes.drop(
                columns=(["current_type", "v_mag_pu_min", "v_mag_pu_max", "geom"]), inplace=True
            )
            # check for hv nodes within hv/mv substations
            substations_keys = substations.keys().tolist()
            substations_keys.remove("ego_subst_id")
            substations_keys.remove("geometry")
            substations_reduced = substations.drop(columns=(substations_keys))
            hv_nodes = gpd.overlay(hv_nodes, substations_reduced, how="intersection")
            # add dave name
            hv_nodes.reset_index(drop=True, inplace=True)
            name = pd.Series(list(map(lambda x: f"node_3_{x}", hv_nodes.index)))
            hv_nodes.insert(0, "dave_name", name)
            # set crs
            hv_nodes.set_crs(dave_settings()["crs_main"], inplace=True)
            # add mv nodes to grid data
            grid_data.hv_data.hv_nodes = pd.concat(
                [grid_data.hv_data.hv_nodes, hv_nodes], ignore_index=True
            )
        else:
            hv_nodes = grid_data.hv_data.hv_nodes
        # update progress
        pbar.update(10)
        # --- prepare mv nodes for the transformers
        # check for mv nodes within hv/mv substations if they were created in mv topology function
        # Otherwise create missing mv nodes
        if grid_data.mv_data.mv_nodes.empty:
            # --- in this case the missing mv nodes for the transformers must be created
            mv_nodes = substations.copy()
            mv_nodes.rename(
                columns={"dave_name": "subst_name"},
                inplace=True,
            )
            # set points for geometry
            mv_nodes["geometry"] = mv_nodes.point.apply(lambda x: wkb.loads(x, hex=True))
            mv_nodes["node_type"] = "hvmv_substation"
            mv_nodes["voltage_level"] = 5
            mv_nodes["voltage_kv"] = dave_settings()["mv_voltage"]
            # add oep as source
            mv_nodes["source"] = "OEP"
            # add dave name
            mv_nodes.reset_index(drop=True, inplace=True)
            name = pd.Series(list(map(lambda x: f"node_5_{x}", mv_nodes.index)))
            mv_nodes.insert(0, "dave_name", name)
            # set crs
            mv_nodes.set_crs(dave_settings()["crs_main"], inplace=True)
            # add mv nodes to grid data
            grid_data.mv_data.mv_nodes = pd.concat(
                [grid_data.mv_data.mv_nodes, mv_nodes], ignore_index=True
            )
        else:
            mv_nodes = grid_data.mv_data.mv_nodes
        # create hv/mv transfromers
        for i, sub in substations.iterrows():
            # get hv bus
            if ("ego_subst_id" in hv_nodes.keys()) and (
                sub.ego_subst_id in hv_nodes.ego_subst_id.tolist()
            ):
                bus_hv = hv_nodes[hv_nodes.ego_subst_id == sub.ego_subst_id].iloc[0].dave_name
            else:
                # find closest hv node to the substation
                multipoints_hv = MultiPoint(hv_nodes.geometry.tolist())
                nearest_point = nearest_points(sub.geometry.centroid, multipoints_hv)[1]
                for _, node in hv_nodes.iterrows():
                    if nearest_point == node.geometry:
                        bus_hv = node.dave_name
                        break
            # get lv bus
            mv_nodes_hvmv = mv_nodes[mv_nodes.node_type == "hvmv_substation"]
            if (not mv_nodes_hvmv.empty) and (
                sub.ego_subst_id in mv_nodes_hvmv.ego_subst_id.tolist()
            ):
                bus_lv = (
                    mv_nodes_hvmv[mv_nodes_hvmv.ego_subst_id == sub.ego_subst_id].iloc[0].dave_name
                )
            else:
                # find closest mv node to the substation
                multipoints_hv = MultiPoint(mv_nodes.geometry.tolist())
                nearest_point = nearest_points(sub.geometry.centroid, multipoints_hv)[1]
                for _, node in hv_nodes.iterrows():
                    if nearest_point == node.geometry:
                        bus_lv = node.dave_name
                        break
            # create transformer
            trafo_df = gpd.GeoDataFrame(
                {
                    "bus_hv": bus_hv,
                    "bus_lv": bus_lv,
                    "voltage_kv_hv": [110],
                    "voltage_kv_lv": [dave_settings()["mv_voltage"]],
                    "voltage_level": [4],
                    "ego_version": sub.ego_version,
                    "ego_subst_id": sub.ego_subst_id,
                    "osm_id": sub.osm_id,
                    "osm_www": sub.osm_www,
                    "substation_name": sub.subst_name,
                    "operator": sub.operator,
                    "Gemeindeschluessel": sub.Gemeindeschluessel,
                    "geometry": [sub.geometry.centroid],
                },
                crs=dave_settings()["crs_main"],
            )
            grid_data.components_power.transformers.hv_mv = pd.concat(
                [grid_data.components_power.transformers.hv_mv, trafo_df], ignore_index=True
            )
            # update progress
            pbar.update(9.98 / len(substations))
        # add dave name
        name = pd.Series(
            list(map(lambda x: f"trafo_4_{x}", grid_data.components_power.transformers.hv_mv.index))
        )
        grid_data.components_power.transformers.hv_mv.insert(0, "dave_name", name)
    else:
        # update progress
        pbar.update(30)

    # --- create mv/lv trafos
    if any(map(lambda x: x in power_levels, ["mv", "lv"])):
        if grid_data.components_power.substations.mv_lv.empty:
            # get transformator data from OEP
            substations, meta_data = oep_request(
                schema="grid",
                table="ego_dp_mvlv_substation",
                where=dave_settings()["mvlv_sub_ver"],
                geometry="geom",
            )
            # add meta data
            if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
                grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
            substations.rename(
                columns={"version": "ego_version", "mvlv_subst_id": "ego_subst_id"}, inplace=True
            )
            # change wrong crs from oep
            substations.crs = dave_settings()["crs_meter"]
            substations = substations.to_crs(dave_settings()["crs_main"])
            # filter trafos for target area
            substations = gpd.overlay(substations, grid_data.area, how="intersection")
            if not substations.empty:
                remove_columns = grid_data.area.keys().tolist()
                remove_columns.remove("geometry")
                substations.drop(columns=remove_columns, inplace=True)
        else:
            substations = grid_data.components_power.substations.mv_lv.copy()
        substations.drop(
            columns=(["la_id", "geom", "subst_id", "is_dummy", "subst_cnt"]), inplace=True
        )
        # update progress
        pbar.update(10)
        # --- prepare mv nodes for the transformers
        # check if the mv nodes already exist, otherwise create them
        if grid_data.mv_data.mv_nodes.empty:
            # --- in this case the missing mv nodes for the transformator must be created
            mv_buses = substations.copy()
            mv_nodes.rename(
                columns={"dave_name": "subst_name"},
                inplace=True,
            )
            mv_buses["node_type"] = "mvlv_substation"
            mv_buses["voltage_level"] = 5
            mv_buses["voltage_kv"] = dave_settings()["mv_voltage"]
            # add oep as source
            mv_buses["source"] = "OEP"
            # add dave name
            mv_buses.reset_index(drop=True, inplace=True)
            name = pd.Series(list(map(lambda x: f"node_5_{x}", mv_buses.index)))
            mv_buses.insert(0, "dave_name", name)
            # set crs
            mv_buses.set_crs(dave_settings()["crs_main"], inplace=True)
            # add mv nodes to grid data
            grid_data.mv_data.mv_nodes = pd.concat(
                [grid_data.mv_data.mv_nodes, mv_buses], ignore_index=True
            )
        else:
            mv_buses = grid_data.mv_data.mv_nodes
        # --- prepare lv nodes for the transformers
        # check if the lv nodes already exist, otherwise create them
        if grid_data.lv_data.lv_nodes.empty:
            # --- in this case the missing lv nodes for the transformator must be created
            lv_buses = substations.copy()
            lv_buses.rename(
                columns={"dave_name": "subst_name"},
                inplace=True,
            )
            lv_buses["node_type"] = "mvlv_substation"
            lv_buses["voltage_level"] = 7
            lv_buses["voltage_kv"] = 0.4
            # add oep as source
            lv_buses["source"] = "OEP"
            # add dave name
            lv_buses.reset_index(drop=True, inplace=True)
            name = pd.Series(list(map(lambda x: f"node_7_{x}", lv_buses.index)))
            lv_buses.insert(0, "dave_name", name)
            # set crs
            lv_buses.set_crs(dave_settings()["crs_main"], inplace=True)
            # add mv nodes to grid data
            grid_data.lv_data.lv_nodes = pd.concat(
                [grid_data.lv_data.lv_nodes, lv_buses], ignore_index=True
            )
        else:
            lv_buses = grid_data.lv_data.lv_nodes
        # update progress
        pbar.update(10)
        # create mv/lv transfromers
        for i, sub in substations.iterrows():
            # get hv bus
            mv_buses_mvlv = mv_buses[mv_buses.node_type == "mvlv_substation"]
            if (not mv_buses_mvlv.empty) and (sub.ego_subst_id in mv_buses.ego_subst_id.tolist()):
                bus_hv = mv_buses[mv_buses.ego_subst_id == sub.ego_subst_id].iloc[0].dave_name
            else:
                # find closest mv node to the substation
                multipoints_mv = MultiPoint(mv_buses.geometry.tolist())
                nearest_point = nearest_points(sub.geometry, multipoints_mv)[1]
                for _, node in mv_buses.iterrows():
                    if nearest_point == node.geometry:
                        bus_hv = node.dave_name
                        break
            # get lv bus
            if ("ego_subst_id" in lv_buses.keys()) and (
                sub.ego_subst_id in lv_buses.ego_subst_id.tolist()
            ):
                bus_lv = lv_buses[lv_buses.ego_subst_id == sub.ego_subst_id].iloc[0].dave_name
            else:
                # find closest lv node to the substation
                multipoints_lv = MultiPoint(lv_buses.geometry.tolist())
                nearest_point = nearest_points(sub.geometry, multipoints_lv)[1]
                for _, node in lv_buses.iterrows():
                    if nearest_point == node.geometry:
                        bus_lv = node.dave_name
                        break
            # create transformer
            trafo_df = gpd.GeoDataFrame(
                {
                    "bus_hv": bus_hv,
                    "bus_lv": bus_lv,
                    "voltage_kv_hv": [dave_settings()["mv_voltage"]],
                    "voltage_kv_lv": [0.4],
                    "voltage_level": [6],
                    "ego_version": sub.ego_version,
                    "ego_subst_id": sub.ego_subst_id,
                    "geometry": [sub.geometry],
                },
                crs=dave_settings()["crs_main"],
            )
            grid_data.components_power.transformers.mv_lv = pd.concat(
                [grid_data.components_power.transformers.mv_lv, trafo_df], ignore_index=True
            )
        # add a synthetic tranformer on the first grid node if necessary
        if grid_data.components_power.transformers.mv_lv.empty:
            if "mv" not in power_levels:
                buses_lv = grid_data.lv_data.lv_nodes
                first_bus = buses_lv[buses_lv.node_type == "road_junction"].iloc[0]
                if grid_data.mv_data.mv_nodes.empty:
                    # if there are no mv nodes, create a new one from data of the first lv bus
                    dave_name = "node_5_0"
                    mv_bus_df = gpd.GeoDataFrame(
                        {
                            "dave_name": dave_name,
                            "voltage_kv": [dave_settings()["mv_voltage"]],
                            "voltage_level": [5],
                            "geometry": [first_bus.geometry],
                            "source": "dave internal",
                        },
                        crs=dave_settings()["crs_main"],
                    )
                    grid_data.mv_data.mv_nodes = pd.concat(
                        [grid_data.mv_data.mv_nodes, mv_bus_df], ignore_index=True
                    )
                    bus_hv = dave_name
                bus_lv = first_bus.dave_name
                # create transformer
                trafo_df = gpd.GeoDataFrame(
                    {
                        "bus_hv": bus_hv,
                        "bus_lv": bus_lv,
                        "voltage_kv_hv": [dave_settings()["mv_voltage"]],
                        "voltage_kv_lv": [0.4],
                        "voltage_level": [6],
                        "geometry": [first_bus.geometry],
                    },
                    crs=dave_settings()["crs_main"],
                )
                grid_data.components_power.transformers.mv_lv = pd.concat(
                    [grid_data.components_power.transformers.mv_lv, trafo_df], ignore_index=True
                )
            elif "lv" not in power_levels:
                pass
                # noch definieren

        # add dave name
        name = pd.Series(
            list(map(lambda x: f"trafo_6_{x}", grid_data.components_power.transformers.mv_lv.index))
        )
        grid_data.components_power.transformers.mv_lv.insert(0, "dave_name", name)
        # update progress
        pbar.update(10)
    else:
        # update progress
        pbar.update(30)
    # close progress bar
    pbar.update(10)
    pbar.close()

    # lv_nodes find closest node, hierbei wenn distanz mehr als 50 m dann leitung erstellen auf
    # lv ebene. schauen ob bereits ein Knoten existiert (distance <=10E-05?) da die bei mv ebene
    # schon erstellt werden, ansonsonsten knoten erstellen an dem trafo und mit dem nächsten
    # knoten verbinden + Leitung diese zusätzzliche Leitung auch bei hv/mv trafos mit rein
