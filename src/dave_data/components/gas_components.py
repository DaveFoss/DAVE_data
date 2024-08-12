# Copyright (c) 2022-2024 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from geopandas import overlay
from pandas import Series, concat
from tqdm import tqdm

from src.dave_data.datapool.read_data import read_scigridgas_iggielgn
from dave.settings import dave_settings


def create_sources(grid_data, scigrid_productions):
    """
    This function adds the data for gas sources
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create sources:                    ",
        position=0,
        bar_format=dave_settings["bar_format"],
    )
    # get compressor data
    sources = scigrid_productions.copy()
    # prepare data
    sources.rename(columns={"id": "scigrid_id", "name": "scigrid_name"}, inplace=True)
    sources["source"] = "scigridgas"
    # intersection with target area
    sources = overlay(sources, grid_data.area, how="intersection")
    keys = grid_data.area.keys().tolist()
    keys.remove("geometry")
    sources = sources.drop(columns=(keys))
    # update progress
    pbar.update(40)
    if not sources.empty:
        # search for junction dave name
        junctions = grid_data.hp_data.hp_junctions.copy()
        sources["junction"] = sources.node_id.apply(
            lambda x: junctions[junctions.scigrid_id == eval(x)[0]].iloc[0].dave_name
        )
        # set junction is_export to true if a sink is connected to
        sources_junctions = sources.junction.to_list()
        for _, junction in grid_data.hp_data.hp_junctions.iterrows():
            if junction.dave_name in sources_junctions:
                grid_data.hp_data.hp_junctions.at[junction.name, "is_import"] = True
        # set grid level number
        sources["pressure_level"] = 1
        # get some relevant parameters out from scigrid param and write in single parameter
        sources["max_supply_M_m3_per_d"] = sources.param.apply(
            lambda x: eval(x)["max_supply_M_m3_per_d"]
        )
        # update progress
        pbar.update(40)
        # add dave name
        sources.reset_index(drop=True, inplace=True)
        sources.insert(0, "dave_name", Series(list(map(lambda x: f"source_1_{x}", sources.index))))
        # set crs
        sources.set_crs(dave_settings["crs_main"], inplace=True)
        # add hp junctions to grid data
        grid_data.components_gas.sources = concat(
            [grid_data.components_gas.sources, sources], ignore_index=True
        )
        # update progress
        pbar.update(20)
    else:
        # update progress
        pbar.update(60)
    # close progress bar
    pbar.close()


def create_compressors(grid_data, scigrid_compressors):
    """
    This function adds the data for gas compressors
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create compressors:                ",
        position=0,
        bar_format=dave_settings["bar_format"],
    )
    # get compressor data
    compressors = scigrid_compressors.copy()
    # prepare data
    compressors.rename(columns={"id": "scigrid_id", "name": "scigrid_name"}, inplace=True)
    compressors["source"] = "scigridgas"
    # intersection with target area
    compressors = overlay(compressors, grid_data.area, how="intersection")
    keys = grid_data.area.keys().tolist()
    keys.remove("geometry")
    compressors = compressors.drop(columns=(keys))
    # update progress
    pbar.update(40)
    if not compressors.empty:
        # search for junction dave name
        junctions = grid_data.hp_data.hp_junctions.copy()
        compressors["junction"] = compressors.node_id.apply(
            lambda x: junctions[junctions.scigrid_id == eval(x)[0]].iloc[0].dave_name
        )
        # set grid level number
        compressors["pressure_level"] = 1
        compressors["max_cap_M_m3_per_d"] = compressors.param.apply(
            lambda x: eval(x)["max_cap_M_m3_per_d"]
        )
        compressors["max_pressure_bar"] = compressors.param.apply(
            lambda x: eval(x)["max_pressure_bar"]
        )
        # update progress
        pbar.update(40)
        # add dave name
        compressors.reset_index(drop=True, inplace=True)
        compressors.insert(
            0, "dave_name", Series(list(map(lambda x: f"compressor_1_{x}", compressors.index)))
        )
        # set crs
        compressors.set_crs(dave_settings["crs_main"], inplace=True)
        # add hp junctions to grid data
        grid_data.components_gas.compressors = concat(
            [grid_data.components_gas.compressors, compressors], ignore_index=True
        )
        # update progress
        pbar.update(20)
    else:
        # update progress
        pbar.update(60)
    # close progress bar
    pbar.close()


def create_sinks(grid_data, scigrid_consumers):
    """
    This function adds the data for gas consumers
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create sinks:                      ",
        position=0,
        bar_format=dave_settings["bar_format"],
    )
    # get sink data
    sinks = scigrid_consumers.copy()
    # prepare data
    sinks.rename(columns={"id": "scigrid_id", "name": "scigrid_name"}, inplace=True)
    sinks["source"] = "scigridgas"
    # intersection with target area
    sinks = overlay(sinks, grid_data.area, how="intersection")
    keys = grid_data.area.keys().tolist()
    keys.remove("geometry")
    sinks = sinks.drop(columns=(keys))
    # update progress
    pbar.update(40)
    if not sinks.empty:
        # search for junction dave name
        junctions = grid_data.hp_data.hp_junctions.copy()
        sinks["junction"] = sinks.node_id.apply(
            lambda x: junctions[junctions.scigrid_id == eval(x)[0]].iloc[0].dave_name
        )
        # set junction is_export to true if a sink is connected to
        sink_junctions = sinks.junction.to_list()
        for _, junction in grid_data.hp_data.hp_junctions.iterrows():
            if junction.dave_name in sink_junctions:
                grid_data.hp_data.hp_junctions.at[junction.name, "is_export"] = True
        # set grid level number
        sinks["pressure_level"] = 1
        # get some relevant parameters out from scigrid param and write in single parameter
        sinks["max_demand_M_m3_per_d"] = sinks.param.apply(
            lambda x: eval(x)["max_demand_M_m3_per_d"]
        )
        # update progress
        pbar.update(40)
        # add dave name
        sinks.reset_index(drop=True, inplace=True)
        sinks.insert(0, "dave_name", Series(list(map(lambda x: f"sink_1_{x}", sinks.index))))
        # set crs
        sinks.set_crs(dave_settings["crs_main"], inplace=True)
        # add hp junctions to grid data
        grid_data.components_gas.sinks = concat(
            [grid_data.components_gas.sinks, sinks], ignore_index=True
        )
        # update progress
        pbar.update(20)
    else:
        # update progress
        pbar.update(60)
    # close progress bar
    pbar.close()


def gas_components(grid_data, compressor, sink, source):
    """
    This function calls all the functions for creating the gas components in the wright order
    """
    # check if there are junctions in the considered area
    if not grid_data.hp_data.hp_junctions.empty:
        # read high pressure grid data from dave datapool (scigridgas igginl)
        if any([compressor, source, sink]):
            scigrid_data, meta_data = read_scigridgas_iggielgn()
            # add meta data
            if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
                grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        # add compressors
        if compressor:
            create_compressors(grid_data, scigrid_compressors=scigrid_data["compressors"])
        # add sinks
        if sink:
            create_sinks(grid_data, scigrid_consumers=scigrid_data["consumers"])
        # add sources
        if source:
            create_sources(grid_data, scigrid_productions=scigrid_data["productions"])
