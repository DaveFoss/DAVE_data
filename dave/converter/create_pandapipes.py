# Copyright (c) 2022-2024 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from pandapipes import (
    create_compressor,
    create_empty_network,
    create_ext_grids,
    create_junctions,
    create_pipes_from_parameters,
    create_sinks,
    create_sources,
    create_valves,
)
from pandas import DataFrame, Series, concat, isna
from shapely.geometry import MultiLineString
from tqdm import tqdm

from dave.io.file_io import ppi_to_json
from dave.settings import dave_settings
from dave.toolbox import multiline_coords


def create_pandapipes(grid_data, output_folder=None, fluid=None, idx_ref="dave_name"):
    """
    This function creates a pandapipes network based an the DaVe dataset

    INPUT:
        **grid_data** (attrdict) - calculated grid data from dave \n
        
    
    OPTIONAL:
        **output_folder** (str, default=None) - patht to the location where the results will be saved \n
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
        bar_format=dave_settings["bar_format"],
    )
    # create empty network
    net = create_empty_network(fluid=fluid)
    # add dave version
    net["dave_version"] = grid_data.dave_version

    # --- create junctions
    # collect junction informations and aggregate them
    all_junctions = concat(
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
                0, "name", Series(list(map(lambda x: f"junction_{x}", all_junctions.index)))
            )  # TODO: hier fehlt noch das pressure level
        # !!! set nominal pressure to the lowest maximal pressure of the pipelines (has to be changed for multiple pressure levles)
        all_junctions["pn_bar"] = grid_data.hp_data.hp_pipes.max_pressure_bar.min()
        # all_junctions.reset_index(drop=True, inplace=True)
        # create junctions
        create_junctions(
            net,  # TODO: failure because of index by finding from and to bus
            nr_junctions=len(all_junctions),
            pn_bar=all_junctions["pn_bar"],
            tfluid_k=(
                dave_settings["hp_pipes_tfluid_k"]
                if "tfluid_k" not in all_junctions.keys() or all(all_junctions.tfluid_k.isna())
                else all_junctions.tfluid_k.apply(
                    lambda x: dave_settings["hp_pipes_tfluid_k"] if isna(x) else x
                )
            ),
            height_m=all_junctions["height_m"],
            name=all_junctions["name"],
            in_service=(
                bool(True)
                if "in_service" not in all_junctions.keys() or all(all_junctions.in_service.isna())
                else all_junctions.in_service.apply(lambda x: bool(True) if isna(x) else x)
            ),
            type=(
                "junction"
                if "type" not in all_junctions.keys() or all(all_junctions.type.isna())
                else all_junctions.type.apply(lambda x: "junction" if isna(x) else x)
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
        if "res_simone_p_barg" in all_junctions.keys():
            net.junction["res_simone_p_barg"] = all_junctions["res_simone_p_barg"]
        if "res_simone_q_eff_mw" in all_junctions.keys():
            net.junction["res_simone_q_eff_mw"] = all_junctions["res_simone_q_eff_mw"]
    map_junctions_simone_id_to_pandapipes_id = dict(
        zip(net.junction.source_id.values, net.junction.index)
    )
    # update progress
    pbar.update(25)

    # --- create pipes
    all_pipes = concat(
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
            all_pipes.insert(0, "name", Series(list(map(lambda x: f"pipe_{x}", all_pipes.index))))
        # check for circle pipes and drop them
        circle_pipe = all_pipes.loc[all_pipes["from_junction"] == all_pipes["to_junction"]]
        if not circle_pipe.empty:
            print(
                f"\nWarning: pipes {circle_pipe.name.values} have the same from and to junctions and "
                f"are being dropped automatically.\n"
            )
            all_pipes.drop(index=circle_pipe.index, inplace=True)
        # check for zero length pipes and drop them
        zero_lenght = all_pipes.loc[all_pipes["length_km"] == 0]
        if not zero_lenght.empty:
            print(
                f"\nWarning: pipes {zero_lenght.name.values} have a length of 0.0 km and are being "
                f"dropped automatically.\n"
            )
            all_pipes.drop(index=zero_lenght.index, inplace=True)
        # conver diameter from mm to m
        all_pipes["diameter_m"] = all_pipes.diameter_mm.apply(lambda x: x / 1000)
        all_pipes.drop(columns=["diameter_mm"])
        # geodata
        all_pipes_coords = DataFrame(
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
        all_pipes_coords = DataFrame([])
    # create pipelines
    create_pipes_from_parameters(
        net,
        from_junctions=all_pipes["from_junction"],
        to_junctions=all_pipes["to_junction"],
        length_km=all_pipes["length_km"],
        diameter_m=all_pipes["diameter_m"],
        k_mm=(
            dave_settings["hp_pipes_k_mm"]
            if "roughness_mm" not in all_pipes.keys() or all(all_pipes.roughness_mm.isna())
            else all_pipes.roughness_mm.apply(
                lambda x: dave_settings["hp_pipes_k_mm"] if isna(x) else x
            )
        ),
        loss_coefficient=(
            float(0)
            if "loss_coefficient" not in all_pipes.keys() or all(all_pipes.loss_coefficient.isna())
            else all_pipes.loss_coefficient.apply(lambda x: float(0) if isna(x) else x)
        ),
        sections=(
            int(1)
            if "sections" not in all_pipes.keys() or all(all_pipes.sections.isna())
            else all_pipes.sections.apply(lambda x: int(1) if isna(x) else x)
        ),
        alpha_w_per_m2k=(
            float(0)
            if "alpha_w_per_m2k" not in all_pipes.keys() or all(all_pipes.alpha_w_per_m2k.isna())
            else all_pipes.alpha_w_per_m2k.apply(lambda x: float(0) if isna(x) else x)
        ),
        text_k=(
            float(293)
            if "text_k" not in all_pipes.keys() or all(all_pipes.text_k.isna())
            else all_pipes.text_k.apply(lambda x: float(293) if isna(x) else x)
        ),
        qext_w=(
            float(0)
            if "qext_w" not in all_pipes.keys() or all(all_pipes.qext_w.isna())
            else all_pipes.qext_w.apply(lambda x: float(0) if isna(x) else x)
        ),
        name=all_pipes["name"],
        geodata=all_pipes_coords.coords,
        in_service=(
            bool(True)
            if "in_service" not in all_pipes.keys() or all(all_pipes.in_service.isna())
            else all_pipes.in_service.apply(lambda x: bool(True) if isna(x) else x)
        ),
        type=(
            "pipe"
            if "type" not in all_pipes.keys() or all(net.pipe.type.isna())
            else net.pipe.type.apply(lambda x: "pipe" if isna(x) else x)
        ),
    )
    # add additional information
    for param in [
        "source_name",
        "source_id",
        "source",
        "max_pressure_bar",
        "geometry",
        "res_simone_p_barg",
        "res_simone_v_m",
    ]:
        if param in all_pipes.keys():
            net.pipe[param] = all_pipes[param]
    # update progress
    pbar.update(25)

    # --- create sink
    sinks = grid_data.components_gas.sinks
    # write sink data into pandapipes structure
    if not sinks.empty:
        sinks.rename(columns={idx_ref: "name"}, inplace=True)
        # change junction names to ids
        sinks["junction"] = sinks.junction.apply(
            lambda x: net.junction[net.junction[idx_ref] == x].index[0]
        )
        # create sink names
        sinks.reset_index(drop=True, inplace=True)
        if "dave_name" in sinks.keys():
            sinks.rename(columns={"dave_name": "name"}, inplace=True)
        else:
            sinks.insert(0, "name", Series(list(map(lambda x: f"sink_{x}", sinks.index))))
        # create sinks
        create_sinks(
            net,
            junctions=sinks["junction"],
            mdot_kg_per_s=sinks["mdot_kg_per_s"]
            if "mdot_kg_per_s" in sinks.keys()
            else float(0.1),  # !!! dummy value has to change
            scaling=float(1),
            name=sinks["name"],
            in_service=True,
            type="sink",
            **sinks.drop(["junction", "mdot_kg_per_s", "name"], axis=1),
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
        sources.reset_index(drop=True, inplace=True)
        if "dave_name" in sources.keys():
            sources.rename(columns={"dave_name": "name"}, inplace=True)
        else:
            sources.insert(0, "name", Series(list(map(lambda x: f"source_{x}", sources.index))))
        # create sinks
        create_sources(
            net,
            junctions=sources["junction"],
            mdot_kg_per_s=sources["mdot_kg_per_s"]
            if "mdot_kg_per_s" in sources.keys()
            else float(0.1),  # !!! dummy value has to change
            scaling=float(1),
            name=sources["name"],
            in_service=True,
            type="source",
            **sources.drop(["junction", "mdot_kg_per_s", "name"], axis=1),
        )
    # update progress
    pbar.update(10)

    # --- create compressors
    compressors = grid_data.components_gas.compressors
    compressors.index = compressors.index.astype(int)
    compressors["from_junction_simone_id"] = compressors["from_junction"]
    compressors["to_junction_simone_id"] = compressors["to_junction"]
    compressors["from_junction"] = compressors["from_junction_simone_id"].map(
        map_junctions_simone_id_to_pandapipes_id
    )
    compressors["to_junction"] = compressors["to_junction_simone_id"].map(
        map_junctions_simone_id_to_pandapipes_id
    )
    if not compressors.empty:
        # write compressor data into pandapipes structure
        for _, compressor in compressors.iterrows():
            _ = create_compressor(
                net,
                compressor["from_junction"],
                compressor["to_junction"],
                pressure_ratio=compressor.get("pressure_ratio", float(1)),
                in_service=compressor.get("in_service", True),
                **compressor.drop(
                    ["from_junction", "to_junction", "pressure_ratio", "in_service"],
                    errors="ignore",
                ),  # ignore if pressure_ratio is not found
            )
        assert net.compressor.from_junction.isin(
            net.junction.index
        ).all(), "some compressors are connected to non-existing junctions!"
        assert net.compressor.to_junction.isin(
            net.junction.index
        ).all(), "some compressors are connected to non-existing junctions!"
    # update progress
    pbar.update(10)

    # --- create valves
    valves = grid_data.components_gas.valves
    valves.index = valves.index.astype(int)
    valves["from_junction_simone_id"] = valves["from_junction"]
    valves["to_junction_simone_id"] = valves["to_junction"]
    valves["from_junction"] = valves["from_junction_simone_id"].map(
        map_junctions_simone_id_to_pandapipes_id
    )
    valves["to_junction"] = valves["to_junction_simone_id"].map(
        map_junctions_simone_id_to_pandapipes_id
    )
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
        _ = create_valves(
            net,
            from_junctions=valves["from_junction"],
            to_junctions=valves["to_junction"],
            diameter_m=valves["diameter_m"],
            opened=valves["opened"] if "opened" in valves.keys() else True,
            **valves.drop(["from_junction", "to_junction", "diameter_m", "opened"], axis=1),
        )
        # net.valve = valves
        # check necessary parameters and add pandapipes standard if needed
        # net.valve["loss_coefficient"] = float(0)
        # net.valve["type"] = "valve"
        assert net.valve.from_junction.isin(
            net.junction.index
        ).all(), "some valves are connected to non-existing junctions!"
        assert net.valve.to_junction.isin(
            net.junction.index
        ).all(), "some valves are connected to non-existing junctions!"
    # update progress
    pbar.update(10)

    # --- create external grid
    ext_grids = grid_data.hp_data.hp_junctions[grid_data.hp_data.hp_junctions["Pset_barg"].notna()]
    if ext_grids.empty:
        # create external grid on the first grid junction
        ext_grids = grid_data.hp_data.hp_junctions.head(1)
        ext_grids["Pset_barg"] = 50  # dummy value need to be changed
    create_ext_grids(
        net, junctions=ext_grids.index, t_k=float(283.15), p_bar=ext_grids["Pset_barg"]
    )
    # update progress
    pbar.update(10)

    # close progress bar
    pbar.close()
    # run pandapower model processing
    net = gas_processing(net)
    # save grid model in the dave output folder
    if output_folder:
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
