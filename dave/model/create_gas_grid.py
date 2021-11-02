import pandapipes as ppi
import pandas as pd
from shapely.geometry import MultiLineString
from shapely.ops import linemerge
from tqdm import tqdm

from dave.settings import dave_settings


def multiline_coords(line_geometry):
    """
    This function extracts the coordinates from a MultiLineString
    """
    merged_line = linemerge(line_geometry)
    # sometimes line merge can not merge the lines correctly
    line_coords = (
        [line.coords[:] for line in merged_line]
        if isinstance(merged_line, MultiLineString)
        else merged_line.coords[:]
    )
    return line_coords


def create_gas_grid(grid_data):
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
        net.junction = net.junction.append(all_junctions)
        net.junction_geodata["x"] = all_junctions.geometry.apply(lambda x: x.coords[:][0][0])
        net.junction_geodata["y"] = all_junctions.geometry.apply(lambda x: x.coords[:][0][1])
        # check necessary parameters and add pandapipes standart if needed
        net.junction["type"] = (
            "junction"
            if all(net.bus.type.isna())
            else net.junction.type.apply(lambda x: "junction" if pd.isna(x) else x)
        )
        net.junction["in_service"] = (
            bool(True)
            if all(net.junction.in_service.isna())
            else net.junction.in_service.apply(lambda x: bool(True) if pd.isna(x) else x)
        )
        net.junction["tfluid_k"] = (
            float(320)
            if all(net.junction.tfluid_k.isna())
            else net.junction.tfluid_k.apply(lambda x: float(320) if pd.isna(x) else x)
        )
    # update progress
    pbar.update(15)

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
    net.pipe = net.pipe.append(pd.concat([pipes_hp, pipes_mp, pipes_lp]), ignore_index=True)
    net.pipe_geodata = net.pipe_geodata.append(
        pd.concat([coords_hp, coords_mp, coords_lp]), ignore_index=True
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
        float(0.1)
        if all(net.pipe.k_mm.isna())
        else net.pipe.k_mm.apply(lambda x: float(0.1) if pd.isna(x) else x)
    )
    net.pipe["loss_coefficient"] = (
        float(0)
        if all(net.loss_coefficient.k_mm.isna())
        else net.loss_coefficient.k_mm.apply(lambda x: float(0) if pd.isna(x) else x)
    )
    net.pipe["alpha_w_per_m2k"] = (
        float(0)
        if all(net.alpha_w_per_m2k.k_mm.isna())
        else net.alpha_w_per_m2k.k_mm.apply(lambda x: float(0) if pd.isna(x) else x)
    )
    net.pipe["qext_w"] = (
        float(0)
        if all(net.pipe.qext_w.isna())
        else net.pipe.qext_w.apply(lambda x: float(0) if pd.isna(x) else x)
    )
    # update progress
    pbar.update(20)
