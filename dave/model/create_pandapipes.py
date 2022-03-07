import pandapipes as ppi
import pandas as pd
from shapely.geometry import MultiLineString
from tqdm import tqdm

from dave.io import ppi_to_json
from dave.settings import dave_settings
from dave.toolbox import multiline_coords


def create_pandapipes(grid_data, api_use, output_folder):
    """
    This function creates a pandapipes network based an the DaVe dataset

    INPUT:
        **grid_data** (attrdict) - calculated grid data from dave

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
    net = ppi.create_empty_network()
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
    if not all_junctions.empty:
        all_junctions.rename(columns={"dave_name": "name"}, inplace=True)
        all_junctions.reset_index(drop=True, inplace=True)
        # write junctions into pandapipes structure
        net.junction = pd.concat([net.junction, all_junctions], ignore_index=True)
        net.junction_geodata["x"] = all_junctions.geometry.apply(lambda x: x.coords[:][0][0])
        net.junction_geodata["y"] = all_junctions.geometry.apply(lambda x: x.coords[:][0][1])
        # check necessary parameters and add pandapipes standart if needed
        net.junction["type"] = (
            "junction"
            if all(net.junction.type.isna())
            else net.junction.type.apply(lambda x: "junction" if pd.isna(x) else x)
        )
        net.junction["in_service"] = (
            bool(True)
            if all(net.junction.in_service.isna())
            else net.junction.in_service.apply(lambda x: bool(True) if pd.isna(x) else x)
        )
        net.junction["tfluid_k"] = (
            dave_settings()["hp_pipes_tfluid_k"]
            if all(net.junction.tfluid_k.isna())
            else net.junction.tfluid_k.apply(
                lambda x: dave_settings()["hp_pipes_tfluid_k"] if pd.isna(x) else x
            )
        )
        # !!! set nominal pressure to the lowest maximal pressure of the pipelines
        net.junction.pn_bar = grid_data.hp_data.hp_pipes.max_pressure_bar.min()
    # update progress
    pbar.update(25)

    # --- create pipes
    # create pipes hp
    pipes_hp = grid_data.hp_data.hp_pipes
    if not pipes_hp.empty:
        pipes_hp.rename(columns={"dave_name": "name"}, inplace=True)
        # conver diameter from mm to m
        pipes_hp["diameter_m"] = pipes_hp.diameter_mm.apply(lambda x: x / 1000)
        pipes_hp.drop(columns=["diameter_mm"])
        # change from/to junction names to ids
        pipes_hp["from_junction"] = pipes_hp.from_junction.apply(
            lambda x: net.junction[net.junction["name"] == x].index[0]
        )
        pipes_hp["to_junction"] = pipes_hp.to_junction.apply(
            lambda x: net.junction[net.junction["name"] == x].index[0]
        )
        # geodata
        coords_hp = pd.DataFrame(
            {
                "coords": pipes_hp.geometry.apply(
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
        coords_hp = pd.DataFrame([])
    # TODO: mp and lp, maybe other handling due to better data quality...
    pipes_mp = pd.DataFrame([])
    pipes_lp = pd.DataFrame([])

    coords_mp = pd.DataFrame([])
    coords_lp = pd.DataFrame([])

    # write pipeline data into pandapipes structure
    net.pipe = pd.concat([net.pipe, pipes_hp, pipes_mp, pipes_lp], ignore_index=True)
    net.pipe_geodata = pd.concat(
        [net.pipe_geodata, coords_hp, coords_mp, coords_lp], ignore_index=True
    )
    # check necessary parameters and add pandapipes standard if needed
    net.pipe["type"] = (
        "pipe"
        if all(net.pipe.type.isna())
        else net.pipe.type.apply(lambda x: "pipe" if pd.isna(x) else x)
    )
    net.pipe["in_service"] = (
        bool(True)
        if all(net.pipe.in_service.isna())
        else net.pipe.in_service.apply(lambda x: bool(True) if pd.isna(x) else x)
    )
    net.pipe["text_k"] = (
        float(293)
        if all(net.pipe.text_k.isna())
        else net.pipe.text_k.apply(lambda x: float(293) if pd.isna(x) else x)
    )
    net.pipe["sections"] = (
        int(1)
        if all(net.pipe.sections.isna())
        else net.pipe.sections.apply(lambda x: int(1) if pd.isna(x) else x)
    )
    net.pipe["std_type"] = (
        None
        if all(net.pipe.std_type.isna())
        else net.pipe.std_type.apply(lambda x: None if pd.isna(x) else x)
    )
    net.pipe["k_mm"] = (
        dave_settings()["hp_pipes_k_mm"]
        if all(net.pipe.k_mm.isna())
        else net.pipe.k_mm.apply(lambda x: dave_settings()["hp_pipes_k_mm"] if pd.isna(x) else x)
    )
    net.pipe["loss_coefficient"] = (
        float(0)
        if all(net.pipe.loss_coefficient.isna())
        else net.pipe.loss_coefficient.apply(lambda x: float(0) if pd.isna(x) else x)
    )
    net.pipe["alpha_w_per_m2k"] = (
        float(0)
        if all(net.pipe.alpha_w_per_m2k.isna())
        else net.pipe.alpha_w_per_m2k.apply(lambda x: float(0) if pd.isna(x) else x)
    )
    net.pipe["qext_w"] = (
        float(0)
        if all(net.pipe.qext_w.isna())
        else net.pipe.qext_w.apply(lambda x: float(0) if pd.isna(x) else x)
    )
    # update progress
    pbar.update(25)

    # --- create sink
    sinks = grid_data.components_gas.sinks
    # write sink data into pandapipes structure
    if not sinks.empty:
        sinks.rename(columns={"dave_name": "name"}, inplace=True)
        # change junction names to ids
        sinks["junction"] = sinks.junction.apply(
            lambda x: net.junction[net.junction["name"] == x].index[0]
        )
        _ = ppi.create_sinks(net,
                             sinks.pop("junction"),
                             mdot_kg_per_s=0.1,  # !!! dummy value has to change
                             scaling=1.0,
                             name=sinks.pop("name"),
                             in_service=True,
                             type="sink",
                             **sinks
                             )
    # update progress
    pbar.update(10)

    # --- create source
    sources = grid_data.components_gas.sources
    # write sink data into pandapipes structure
    if not sources.empty:
        sources.rename(columns={"dave_name": "name"}, inplace=True)
        # change junction names to ids
        sources["junction"] = sources.junction.apply(
            lambda x: net.junction[net.junction["name"] == x].index[0]
        )
        _ = ppi.create_sources(net,
                               sources.pop("junction"),
                               mdot_kg_per_s=0.1,  # !!! dummy value has to change
                               scaling=1.0,
                               name=sources.pop("name"),
                               in_service=True,
                               type="sink",
                               **sources
                               )
    # update progress
    pbar.update(10)

    # --- create external grid
    # !!! ToDo
    # update progress
    pbar.update(10)

    # --- create compressors
    # !!! ToDo
    # update progress
    pbar.update(10)

    # --- create valves
    valves = grid_data.components_gas.valves
    # write valve data into pandapipes structure
    if not valves.empty:
        valves.rename(columns={"dave_name": "name"}, inplace=True)
        # change from/to junction names to ids
        valves["from_junction"] = valves.from_junction.apply(
            lambda x: net.junction[net.junction["name"] == x].index[0]
        )
        valves["to_junction"] = valves.to_junction.apply(
            lambda x: net.junction[net.junction["name"] == x].index[0]
        )
        valves["diameter_m"] = valves.diameter_mm.apply(lambda x: x / 1000)
        valves.drop(columns=["diameter_mm"], inplace=True)
        net.valve = valves
        # check necessary parameters and add pandapipes standard if needed
        net.valve["loss_coefficient"] = float(0)
        net.valve["type"] = "valve"
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
