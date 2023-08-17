# Copyright (c) 2022-2023 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import pandapipes as ppi
import pandas as pd
from shapely.geometry import MultiLineString
from tqdm import tqdm

from dave.io.file_io import ppi_to_json
from dave.settings import dave_settings
from dave.toolbox import multiline_coords


def create_pandapipes(grid_data, api_use, output_folder, fluid=None, idx_ref="dave_name"):
    """
    This function creates a pandapipes network based an the DaVe dataset

    INPUT:
        **grid_data** (attrdict) - calculated grid data from dave
        **api_use** (boolean, default True) - if true, the resulting data will not stored in a \
            local folder
        **output_folder** (string, default user desktop) - absolute path to the folder where the \
            generated data should be saved. if for this path no folder exists, dave will be \
                create one \n
    
    OPTIONAL:
        **idx_ref** (str, default='dave_name') - defines parameter which should use as referenz \
            for setting the indices
        **fluid** (str, default=None) - A fluid that can be added to the net from the start. A \
            fluid is required for pipeflow calculations. Existing fluids in pandapipes are “hgas”, \
            “lgas”, “hydrogen”, “methane”, “water”, “air” \n

    OUTPUT:
        **net** (attrdict) - pandapipes attrdict with grid data
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create pandapipes network:         ",
        position=0,
        bar_format=dave_settings()["bar_format"],
    )
    # create empty network
    net = ppi.create_empty_network(fluid=fluid)
    # add dave version
    net["dave_version"] = grid_data.dave_version

    # --- create junctions
    # collect junction informations and aggregate them
    all_junctions = pd.concat(
        [
            grid_data.hp_data.hp_junctions,
            grid_data.mp_data.mp_junctions,
            grid_data.lp_data.lp_junctions,
        ]
    )
    all_junctions.reset_index(drop=True, inplace=True)

    if not all_junctions.empty:
        # create junction name
        if "dave_name" in all_junctions.keys():
            all_junctions.rename(columns={"dave_name": "name"}, inplace=True)
        else:
            all_junctions.insert(
                0, "name", pd.Series(list(map(lambda x: f"junction_{x}", all_junctions.index)))
            )
        # !!! set nominal pressure to the lowest maximal pressure of the pipelines (has to be changed for multiple pressure levles)
        all_junctions["pn_bar"] = grid_data.hp_data.hp_pipes.max_pressure_bar.min()
        # all_junctions.reset_index(drop=True, inplace=True)
        # create junctions
        ppi.create_junctions(
            net,  # TODO: failure because of index by finding from and to bus
            nr_junctions=len(all_junctions),
            pn_bar=all_junctions["pn_bar"],
            tfluid_k=(
                dave_settings()["hp_pipes_tfluid_k"]
                if "tfluid_k" not in all_junctions.keys() or all(all_junctions.tfluid_k.isna())
                else all_junctions.tfluid_k.apply(
                    lambda x: dave_settings()["hp_pipes_tfluid_k"] if pd.isna(x) else x
                )
            ),
            height_m=all_junctions["height_m"],
            name=all_junctions["name"],
            in_service=(
                bool(True)
                if "in_service" not in all_junctions.keys() or all(all_junctions.in_service.isna())
                else all_junctions.in_service.apply(lambda x: bool(True) if pd.isna(x) else x)
            ),
            type=(
                "junction"
                if "type" not in all_junctions.keys() or all(all_junctions.type.isna())
                else all_junctions.type.apply(lambda x: "junction" if pd.isna(x) else x)
            ),
            geodata=all_junctions.geometry.apply(
                lambda x: (x.coords[:][0][0], x.coords[:][0][1])
            ).to_list(),
        )
        # add additional information
        # net.junction.insert(len(net.junction.columns), "source_name", all_junctions['source_name'])
        net.junction["source_name"] = all_junctions["source_name"]
        net.junction["source_id"] = all_junctions["source_id"]
        net.junction["source"] = all_junctions["source"]
        net.junction["geometry"] = all_junctions["geometry"]
    map_junctions_simone_id_to_pandapipes_id = dict(zip(net.junction.source_id.values,
                                                        net.junction.index))
    # update progress
    pbar.update(25)

    # --- create pipes
    # collect junction informations and aggregate them
    all_pipes = pd.concat(
        [
            grid_data.hp_data.hp_pipes,
            grid_data.mp_data.mp_pipes,
            grid_data.lp_data.lp_pipes,
        ],
        ignore_index=True,
    )

    if not all_pipes.empty:
        # change from/to junction names to ids
        if "from_junction" in all_pipes.keys():
            all_pipes["from_junction"] = all_pipes.from_junction.apply(
                lambda x: net.junction[net.junction[idx_ref] == x].index[0]
            )
        if "to_junction" in all_pipes.keys():
            all_pipes["to_junction"] = all_pipes.to_junction.apply(
                lambda x: net.junction[net.junction[idx_ref] == x].index[0]
            )
        # create pipeline names
        if "dave_name" in all_pipes.keys():
            all_pipes.rename(columns={"dave_name": "name"}, inplace=True)
        else:
            all_pipes.insert(
                0, "name", pd.Series(list(map(lambda x: f"pipe_{x}", all_pipes.index)))
            )
        # conver diameter from mm to m
        all_pipes["diameter_m"] = all_pipes.diameter_mm.apply(lambda x: x / 1000)
        all_pipes.drop(columns=["diameter_mm"])
        # geodata
        all_pipes_coords = pd.DataFrame(
            {
                "coords": all_pipes.geometry.apply(
                    lambda x: [
                        list(coords)
                        for coords in (
                            multiline_coords(x) if isinstance(x, MultiLineString) else x.coords[:]
                        )
                    ]
                )
            }
        )
    else:
        all_pipes_coords = pd.DataFrame([])
    # create pipelines
    ppi.create_pipes_from_parameters(
        net,
        from_junctions=all_pipes["from_junction"],
        to_junctions=all_pipes["to_junction"],
        length_km=all_pipes["length_km"],
        diameter_m=all_pipes["diameter_m"],
        k_mm=(
            dave_settings()["hp_pipes_k_mm"]
            if "roughness_mm" not in all_pipes.keys() or all(all_pipes.roughness_mm.isna())
            else all_pipes.roughness_mm.apply(
                lambda x: dave_settings()["hp_pipes_k_mm"] if pd.isna(x) else x
            )
        ),
        loss_coefficient=(
            float(0)
            if "loss_coefficient" not in all_pipes.keys() or all(all_pipes.loss_coefficient.isna())
            else all_pipes.loss_coefficient.apply(lambda x: float(0) if pd.isna(x) else x)
        ),
        sections=(
            int(1)
            if "sections" not in all_pipes.keys() or all(all_pipes.sections.isna())
            else all_pipes.sections.apply(lambda x: int(1) if pd.isna(x) else x)
        ),
        alpha_w_per_m2k=(
            float(0)
            if "alpha_w_per_m2k" not in all_pipes.keys() or all(all_pipes.alpha_w_per_m2k.isna())
            else all_pipes.alpha_w_per_m2k.apply(lambda x: float(0) if pd.isna(x) else x)
        ),
        text_k=(
            float(293)
            if "text_k" not in all_pipes.keys() or all(all_pipes.text_k.isna())
            else all_pipes.text_k.apply(lambda x: float(293) if pd.isna(x) else x)
        ),
        qext_w=(
            float(0)
            if "qext_w" not in all_pipes.keys() or all(all_pipes.qext_w.isna())
            else all_pipes.qext_w.apply(lambda x: float(0) if pd.isna(x) else x)
        ),
        name=all_pipes["name"],
        geodata=all_pipes_coords.coords,
        in_service=(
            bool(True)
            if "in_service" not in all_pipes.keys() or all(all_pipes.in_service.isna())
            else all_pipes.in_service.apply(lambda x: bool(True) if pd.isna(x) else x)
        ),
        type=(
            "pipe"
            if "type" not in all_pipes.keys() or all(net.pipe.type.isna())
            else net.pipe.type.apply(lambda x: "pipe" if pd.isna(x) else x)
        ),
    )
    # add additional information
    net.pipe["source_name"] = all_pipes["source_name"]
    net.pipe["source_id"] = all_pipes["source_id"]
    net.pipe["source"] = all_pipes["source"]
    net.pipe["max_pressure_bar"] = all_pipes["max_pressure_bar"]
    net.pipe["geometry"] = all_pipes["geometry"]
    # update progress
    pbar.update(25)

    # --- create sink
    sinks = grid_data.components_gas.sinks
    # write sink data into pandapipes structure
    if not sinks.empty:
        sinks.rename(columns={idx_ref: "name"}, inplace=True)
        # change junction names to ids
        sinks["junction"] = sinks.junction.apply(
            lambda x: net.junction[net.junction["name"] == x].index[0]
        )
        # create sink names
        if "dave_name" in sinks.keys():
            sinks.rename(columns={"dave_name": "name"}, inplace=True)
        else:
            sinks.insert(0, "name", pd.Series(list(map(lambda x: f"sink_{x}", sinks.index))))
        # create sinks
        ppi.create_sinks(
            net,
            junctions=sinks["junction"],
            mdot_kg_per_s=float(0.1),  # !!! dummy value has to change, also check if value is there
            scaling=float(1),
            name=sinks["name"],
            in_service=True,
            type="sink",
        )
    # update progress
    pbar.update(10)

    # --- create source
    sources = grid_data.components_gas.sources
    # write sink data into pandapipes structure
    if not sources.empty:
        sources.rename(columns={idx_ref: "name"}, inplace=True)
        # change junction names to ids
        sources["junction"] = sources.junction.apply(
            lambda x: net.junction[net.junction[idx_ref] == x].index[0]
        )
        # create source names
        if "dave_name" in sources.keys():
            sources.rename(columns={"dave_name": "name"}, inplace=True)
        else:
            sources.insert(0, "name", pd.Series(list(map(lambda x: f"source_{x}", sources.index))))

        # create sinks
        ppi.create_sources(
            net,
            junctions=sources["junction"],
            mdot_kg_per_s=float(0.1),  # !!! dummy value has to change, also check if value is there
            scaling=float(1),
            name=sources["name"],
            in_service=True,
            type="source",
        )
        net.source = sources
        # check necessary parameters and add pandapipes standard if needed
        net.source["mdot_kg_per_s"] = float(0.1)  # !!! dummy value has to change
        net.source["scaling"] = float(1)
        net.source["in_service"] = True
        net.source["type"] = "source"
    # update progress
    pbar.update(10)

    # --- create compressors
    compressors = grid_data.components_gas.compressors
    compressors.index = compressors.index.astype(int)
    compressors["from_junction_simone_id"] = compressors["from_junction"]
    compressors["to_junction_simone_id"] = compressors["to_junction"]
    compressors["from_junction"] = compressors["from_junction_simone_id"].map(
        map_junctions_simone_id_to_pandapipes_id)
    compressors["to_junction"] = compressors["to_junction_simone_id"].map(
        map_junctions_simone_id_to_pandapipes_id)
    if not compressors.empty:
        # write compressor data into pandapipes structure
        # if "compressor" in net.keys():
        #     net.compressor = pd.concat([net.compressor, compressors], ignore_index=True)
        # else:
        #     net.compressor = compressors
        for _, c in compressors.iterrows():
            _ = ppi.create_compressor(net,
                                      c["from_junction"],
                                      c["to_junction"],
                                      pressure_ratio=c.get("pressure_ratio", 1),
                                      **c.drop(["from_junction", "to_junction", "pressure_ratio"],
                                               errors="ignore") # ignore if pressure_ratio is not found
                                      )
        # check necessary parameters and add pandapipes standard if needed
        # net.compressor["pressure_ratio"] = float(1)
        # net.compressor["in_service"] = True
        # net.compressor["pressure_ratio"] = (
        #     float(1)
        #     if all(net.compressor.pressure_ratio.isna())
        #     else net.compressor.pressure_ratio.apply(lambda x: bool(True) if pd.isna(x) else x)
        # )
        # net.compressor["in_service"] = (
        #     bool(True)
        #     if all(net.compressor.in_service.isna())
        #     else net.compressor.in_service.apply(lambda x: bool(True) if pd.isna(x) else x)
        # )
        assert net.compressor.from_junction.isin(net.junction.index).all(), \
            "some compressors are connected to non-existing junctions!"
        assert net.compressor.to_junction.isin(net.junction.index).all(), \
            "some compressors are connected to non-existing junctions!"
    # update progress
    pbar.update(10)

    # --- create valves
    valves = grid_data.components_gas.valves
    valves.index = valves.index.astype(int)
    valves["from_junction_simone_id"] = valves["from_junction"]
    valves["to_junction_simone_id"] = valves["to_junction"]
    valves["from_junction"] = valves["from_junction_simone_id"].map(
                                map_junctions_simone_id_to_pandapipes_id)
    valves["to_junction"] = valves["to_junction_simone_id"].map(
                                map_junctions_simone_id_to_pandapipes_id)
    # valves["opened"] = valves["opened"].astype(bool)
    # write valve data into pandapipes structure
    if not valves.empty:
        valves.rename(columns={idx_ref: "name"}, inplace=True)
        # change from/to junction names to ids
        # if "from_junction" in valves.keys():
        # # if not "from_junction" in valves.keys():
        #     valves["from_junction"] = valves.from_junction.apply(
        #         lambda x: net.junction[net.junction["name"] == x].index[0]
        #     )
        # if "to_junction" in valves.keys():
        # # if not "to_junction" in valves.keys():
        #     valves["to_junction"] = valves.to_junction.apply(
        #         lambda x: net.junction[net.junction["name"] == x].index[0]
        #     )
        valves["diameter_m"] = valves.diameter_mm.apply(lambda x: x / 1000)
        valves.drop(columns=["diameter_mm"], inplace=True)
        _ = ppi.create_valves(net,
                              from_junctions=valves["from_junction"],
                              to_junctions=valves["to_junction"],
                              diameter_m=valves["diameter_m"],
                              **valves.drop(["from_junction", "to_junction", "diameter_m"], axis=1)
                              )
        # net.valve = valves
        # check necessary parameters and add pandapipes standard if needed
        # net.valve["loss_coefficient"] = float(0)
        # net.valve["type"] = "valve"
        assert net.valve.from_junction.isin(net.junction.index).all(), \
            "some valves are connected to non-existing junctions!"
        assert net.valve.to_junction.isin(net.junction.index).all(), \
            "some valves are connected to non-existing junctions!"
    # update progress
    pbar.update(10)

    # --- create external grid
    # !!! ToDo: Wenn keine Daten vorhanden, dann muss ein definiert werden
    # update progress
    pbar.update(10)

    # close progress bar
    pbar.close()
    # run pandapower model processing
    net = gas_processing(net)
    # save grid model in the dave output folder
    if not api_use:
        file_path = output_folder + "\\dave_pandapipes.json"
        ppi_to_json(net, file_path)
    return net


def gas_processing(net_gas):
    """
    This function run a diagnosis of the pandapipes network and clean up occurring failures.
    Furthermore the grid will be adapt so all boundarys be respected.

    INPUT:
        **net** (attrdict) - pandapipes attrdict

    OUTPUT:
        **net** (attrdict) - A cleaned up and if necessary optimized pandapipes attrdict
    """
    return net_gas
    # hier wird das Gasnetzmodell nach dem es in pandapipes erstellt wurde, aufbereitet damit ein
    # lastfluss konvergiert und sonstige Fehler bereinigen
