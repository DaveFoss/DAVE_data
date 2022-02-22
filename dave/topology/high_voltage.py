import math

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point
from tqdm import tqdm

from dave.datapool import oep_request
from dave.settings import dave_settings


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
        ehvhv_substations, meta_data = oep_request(
            schema="grid",
            table="ego_dp_ehv_substation",
            where=dave_settings()["ehv_sub_ver"],
            geometry="polygon",
        )
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
        ehvhv_substations = gpd.overlay(ehvhv_substations, grid_data.area, how="intersection")
        if not ehvhv_substations.empty:
            remove_columns = grid_data.area.keys().tolist()
            remove_columns.remove("geometry")
            ehvhv_substations.drop(columns=remove_columns, inplace=True)
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
    # create hv/mv substations
    if grid_data.components_power.substations.hv_mv.empty:
        hvmv_substations, meta_data = oep_request(
            schema="grid",
            table="ego_dp_hvmv_substation",
            where=dave_settings()["hvmv_sub_ver"],
            geometry="polygon",
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
        drop_substations = [
            sub.name
            for i, sub in hvmv_substations.iterrows()
            if isinstance(sub.geometry, (Point, LineString))
        ]
        hvmv_substations.drop(drop_substations, inplace=True)
        # check for substations in the target area
        hvmv_substations = gpd.overlay(hvmv_substations, grid_data.area, how="intersection")
        if not hvmv_substations.empty:
            remove_columns = grid_data.area.keys().tolist()
            remove_columns.remove("geometry")
            hvmv_substations.drop(columns=remove_columns, inplace=True)
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
    pbar.update(10)

    # --- create hv nodes
    ehvhv_buses, meta_data = oep_request(
        schema="grid", table="ego_pf_hv_bus", where=dave_settings()["hv_buses_ver"], geometry="geom"
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
    # update progress
    pbar.update(10)
    # filter nodes which are on the hv level, current exsist and within the target area
    hv_buses = ehvhv_buses[
        (ehvhv_buses.voltage_kv == 110) & (ehvhv_buses.ego_scn_name == "Status Quo")
    ]
    hv_buses = gpd.overlay(hv_buses, grid_data.area, how="intersection")
    if not hv_buses.empty:
        remove_columns = grid_data.area.keys().tolist()
        remove_columns.remove("geometry")
        hv_buses = hv_buses.drop(columns=remove_columns)
    hv_buses["voltage_level"] = 3
    hv_buses = hv_buses.drop(columns=(["current_type", "v_mag_pu_min", "v_mag_pu_max", "geom"]))
    # consider data only if there are more than one node in the target area
    if len(hv_buses) > 1:
        # search for the substations where the hv nodes are within
        hv_buses.insert(0, "ego_subst_id", None)
        hv_buses.insert(1, "subst_dave_name", None)
        hv_buses.insert(2, "subst_name", None)
        for _, bus in hv_buses.iterrows():
            ego_subst_id = []
            subst_dave_name = []
            subst_name = []
            for _, sub in ehvhv_substations.iterrows():
                if (bus.geometry.within(sub.geometry)) or (
                    bus.geometry.distance(sub.geometry) < 1e-05
                ):
                    ego_subst_id.append(sub.ego_subst_id)
                    subst_dave_name.append(sub.dave_name)
                    subst_name.append(sub.subst_name)
                    break
            for _, sub in hvmv_substations.iterrows():
                if (bus.geometry.within(sub.geometry)) or (
                    bus.geometry.distance(sub.geometry) < 1e-05
                ):
                    ego_subst_id.append(sub.ego_subst_id)
                    subst_dave_name.append(sub.dave_name)
                    subst_name.append(sub.subst_name)
                    break
            if len(ego_subst_id) != 0:
                hv_buses.at[bus.name, "ego_subst_id"] = ego_subst_id
            if len(subst_dave_name) != 0:
                hv_buses.at[bus.name, "subst_dave_name"] = subst_dave_name
            if len(subst_name) != 0:
                hv_buses.at[bus.name, "subst_name"] = subst_name
            # update progress
            pbar.update(10 / len(hv_buses))
        # add oep as source
        hv_buses["source"] = "OEP"
        # add dave name
        hv_buses.reset_index(drop=True, inplace=True)
        name = pd.Series(list(map(lambda x: f"node_3_{x}", hv_buses.index)))
        hv_buses.insert(0, "dave_name", name)
        # set crs
        hv_buses.set_crs(dave_settings()["crs_main"], inplace=True)
        # add hv nodes to grid data
        grid_data.hv_data.hv_nodes = pd.concat(
            [grid_data.hv_data.hv_nodes, hv_buses], ignore_index=True
        )
        # --- create hv lines
        hv_lines, meta_data = oep_request(
            schema="grid",
            table="ego_pf_hv_line",
            where=dave_settings()["hv_line_ver"],
            geometry="geom",
        )
        # add meta data
        if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
            grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        hv_lines.rename(
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
            },
            inplace=True,
        )
        # update progress
        pbar.update(10)
        # filter lines which are on the hv level by check if both endpoints are on the hv level
        hv_bus_ids = hv_buses.ego_bus_id.tolist()
        hv_lines = hv_lines[
            (hv_lines.bus0.isin(hv_bus_ids))
            & (hv_lines.bus1.isin(hv_bus_ids))
            & (hv_lines.ego_scn_name == "Status Quo")
        ]
        # --- add additional line parameter and change bus names
        hv_lines.insert(hv_lines.columns.get_loc("r_ohm") + 1, "r_ohm_per_km", None)
        hv_lines.insert(hv_lines.columns.get_loc("x_ohm") + 1, "x_ohm_per_km", None)
        hv_lines.insert(hv_lines.columns.get_loc("b_s") + 1, "c_nf_per_km", None)
        hv_lines.insert(hv_lines.columns.get_loc("b_s") + 1, "c_nf", None)
        # add voltage
        hv_lines["voltage_kv"] = 110
        bus0_new = []
        bus1_new = []
        for _, line in hv_lines.iterrows():
            # calculate and add r,x,c per km
            hv_lines.at[line.name, "r_ohm_per_km"] = float(line.r_ohm) / line.length_km
            hv_lines.at[line.name, "x_ohm_per_km"] = float(line.x_ohm) / line.length_km
            c_nf = float(line.b_s) / (2 * math.pi * float(line.frequency)) * 1e09
            hv_lines.at[line.name, "c_nf"] = c_nf
            hv_lines.at[line.name, "c_nf_per_km"] = c_nf / line.length_km
            # calculate and add max i
            hv_lines.at[line.name, "max_i_ka"] = (
                (float(line.s_nom_mva) * 1e06) / (line.voltage_kv * 1e03)
            ) * 1e-03
            # calculate parallel lines
            hv_lines.at[line.name, "parallel"] = line.cables / 3
            # change line bus names from ego id to dave name
            bus0_dave = hv_buses[hv_buses.ego_bus_id == line.bus0].iloc[0].dave_name
            bus1_dave = hv_buses[hv_buses.ego_bus_id == line.bus1].iloc[0].dave_name
            bus0_new.append(bus0_dave)
            bus1_new.append(bus1_dave)
            # update progress
            pbar.update(50 / len(hv_lines))
        hv_lines["bus0"] = bus0_new
        hv_lines["bus1"] = bus1_new
        # add oep as source
        hv_lines["source"] = "OEP"
        # add voltage level
        hv_lines["voltage_level"] = 3
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
        pbar.update(80)
    # close progress bar
    pbar.close()
