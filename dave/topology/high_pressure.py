import geopandas as gpd
import pandas as pd
from tqdm import tqdm

from dave.datapool import read_gaslib, read_hp_data, read_scigridgas_iggielgn
from dave.settings import dave_settings


def gaslib_pipe_clustering():
    """
    This function is clustering the gaslib pipe data and calculate the avarage for the parameters.
    The pipesUsedForData parameter describt the number of pipes within the cluster
    """
    pipe_data = dict()
    # import gaslib data
    gaslib_data, meta_data_gaslib = read_gaslib()  # !!! implement meta data

    for pipe in gaslib_data["connections"]["pipe"]:
        lengthrounded = round(pipe["length"]["@value"], 1)
        diameter = pipe["diameter"]["@value"]
        roughness = pipe["roughness"]["@value"]
        pressure_max = pipe["pressureMax"]["@value"]

        if lengthrounded in pipe_data:
            pipe_data[lengthrounded]["pipesUsedForData"] += 1.0
            pipe_data[lengthrounded]["diameter"] += diameter
            pipe_data[lengthrounded]["diameter"] /= pipe_data[lengthrounded]["pipesUsedForData"]
            pipe_data[lengthrounded]["roughness"] += roughness
            pipe_data[lengthrounded]["roughness"] /= pipe_data[lengthrounded]["pipesUsedForData"]
            pipe_data[lengthrounded]["pressureMax"] += pressure_max
            pipe_data[lengthrounded]["pressureMax"] /= pipe_data[lengthrounded]["pipesUsedForData"]
        else:
            pipe_data[lengthrounded] = {
                "diameter": diameter,
                "roughness": roughness,
                "pressureMax": pressure_max,
                "pipesUsedForData": 1.0,
            }
    return pipe_data


def create_hp_topology(grid_data):
    """
    This function creates a dictonary with all relevant parameters for the
    high pressure level

    INPUT:
        **grid_data** (dict) - all Informations about the grid area

    OUTPUT:
        Writes data in the DaVe dataset
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create high pressure topology:     ",
        position=0,
        bar_format=dave_settings()["bar_format"],
    )
    # read high pressure grid data from dave datapool (scigridgas igginl)
    scigrid_data, meta_data = read_scigridgas_iggielgn()
    # add meta data
    if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
        grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
    # update progress
    pbar.update(20)
    # create hp junctions (nodes)
    hp_junctions = scigrid_data["nodes"]
    # prepare data
    hp_junctions.rename(columns={"id": "scigrid_id", "name": "scigrid_name"}, inplace=True)
    hp_junctions["source"] = "scigridgas"
    # intersection with target area
    hp_junctions = gpd.overlay(hp_junctions, grid_data.area, how="intersection")
    keys = grid_data.area.keys().tolist()
    keys.remove("geometry")
    hp_junctions = hp_junctions.drop(columns=(keys))
    # extract relevant scigrid parameters
    # hp_junctions["entsog_key"] = hp_junctions.param.apply(lambda x: eval(x)["entsog_key"])
    hp_junctions.param.apply(
        lambda x: None if "entsog_key" not in eval(x) else eval(x)["entsog_key"]
    )
    # set grid level number
    hp_junctions["pressure_level"] = 1
    # update progress
    pbar.update(20)
    # consider data only if there are more than one junction in the target area
    if len(hp_junctions) > 1:
        # add dave name
        hp_junctions.reset_index(drop=True, inplace=True)
        hp_junctions.insert(
            0, "dave_name", pd.Series(list(map(lambda x: f"junction_1_{x}", hp_junctions.index)))
        )
        # set crs
        hp_junctions.set_crs(dave_settings()["crs_main"], inplace=True)
        # add hp junctions to grid data
        grid_data.hp_data.hp_junctions = grid_data.hp_data.hp_junctions.append(hp_junctions)
        # update progress
        pbar.update(20)
        # --- create hp pipes
        hp_pipes = scigrid_data["pipe_segments"]
        # filter relevant pipelines by checking if both endpoints are in the target area
        hp_junctions_ids = hp_junctions.scigrid_id.tolist()
        hp_pipes["from_junction"] = hp_pipes.node_id.apply(lambda x: eval(x)[0])
        hp_pipes["to_junction"] = hp_pipes.node_id.apply(lambda x: eval(x)[1])
        hp_pipes = hp_pipes[
            (hp_pipes.from_junction.isin(hp_junctions_ids))
            & (hp_pipes.to_junction.isin(hp_junctions_ids))
        ]
        # prepare data
        hp_pipes.rename(columns={"id": "scigrid_id", "name": "scigrid_name"}, inplace=True)
        hp_pipes["source"] = "scigridgas"
        hp_pipes["pressure_level"] = 1
        # extract relevant scigrid parameters
        hp_pipes["diameter_mm"] = hp_pipes.param.apply(lambda x: eval(x)["diameter_mm"])
        hp_pipes["is_H_gas"] = hp_pipes.param.apply(
            lambda x: True if eval(x)["is_H_gas"] == 1 else False
        )
        hp_pipes["is_bothDirection"] = hp_pipes.param.apply(
            lambda x: True if eval(x)["is_bothDirection"] == 1 else False
        )
        hp_pipes["length_km"] = hp_pipes.param.apply(lambda x: eval(x)["length_km"])
        hp_pipes["max_cap_M_m3_per_d"] = hp_pipes.param.apply(
            lambda x: eval(x)["max_cap_M_m3_per_d"]
        )
        hp_pipes["max_pressure_bar"] = hp_pipes.param.apply(lambda x: eval(x)["max_pressure_bar"])
        hp_pipes["operator_name"] = hp_pipes.param.apply(
            lambda x: "" if "operator_name" not in eval(x) else eval(x)["operator_name"]
        )
        # update progress
        pbar.update(20)
        # change pipeline junction names from scigrid id to dave name
        hp_pipes["from_junction"] = hp_pipes.from_junction.apply(
            lambda x: hp_junctions[hp_junctions.scigrid_id == x].iloc[0].dave_name
        )
        hp_pipes["to_junction"] = hp_pipes.to_junction.apply(
            lambda x: hp_junctions[hp_junctions.scigrid_id == x].iloc[0].dave_name
        )
        # get gaslib data clustered
        gaslib_pipe_data = gaslib_pipe_clustering()
        gaslib_pipe_data_sorted = sorted(gaslib_pipe_data, key=float)
        # add roughness from gaslib data to nearest scigrid pipe by length
        nearestpipelengthgaslib = hp_pipes.length_km.apply(
            lambda y: min(gaslib_pipe_data_sorted, key=lambda x: abs(x - y))
        )
        hp_pipes["roughness"] = nearestpipelengthgaslib.apply(
            lambda x: gaslib_pipe_data[x]["roughness"]
        )

        # add dave name
        hp_pipes.reset_index(drop=True, inplace=True)
        hp_pipes.insert(
            0, "dave_name", pd.Series(list(map(lambda x: f"pipe_1_{x}", hp_pipes.index)))
        )
        # set crs
        hp_pipes.set_crs(dave_settings()["crs_main"], inplace=True)
        # add pipes to grid data
        grid_data.hp_data.hp_pipes = grid_data.hp_data.hp_pipes.append(hp_pipes)
        # update progress
        pbar.update(20)
    # close progress bar
    pbar.close()


def create_lkd_eu(grid_data):
    """
    This function creates a dictonary with all relevant parameters for the
    high pressure level based on the lkd_eu dataset.

    It is deprecated because the lkd_eu dataset is also in the scigridgas dataset implemented and
    this one will be used for the hp level creation

    INPUT:
        **grid_data** (dict) - all Informations about the grid area

    OUTPUT:
        Writes data in the DaVe dataset
    """
    # read high pressure grid data from dave datapool
    hp_data, meta_data = read_hp_data()
    # add meta data
    if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
        grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
    source = "Paper: Electricity, Heat, and Gas Sector Data for Modeling the German System"
    # --- create hp junctions (nodes)
    hp_junctions = hp_data["hp_nodes"]
    # prepare data
    hp_junctions.rename(
        columns={
            "NODE_ID": "original_id",
            "NAME": "original_name",
            "OPERATOR": "operator",
            "ENTRY": "entry",
            "EXIT": "exit",
            "H_L_CONVER": "h_l_converter",
            "NUTS_3": "nuts_3",
            "ENTSOG_NAM": "entsog_name",
            "ENTSOG_KEY": "entsog_key",
        },
        inplace=True,
    )
    hp_junctions.drop(
        columns=(
            [
                "OPERATOR_Z",
                "COMPRESSOR",
                "COMP_UNITS",
                "NUTS_2",
                "NUTS_1",
                "NUTS_0",
                "X",
                "Y",
                "CROSSBORDE",
                "MARKETAREA",
                "UGS",
                "PROD",
            ]
        ),
        inplace=True,
    )
    hp_junctions["reference_year"] = 2015
    hp_junctions["source"] = source
    hp_junctions["pressure_level"] = 1
    hp_junctions["original_id"] = hp_junctions.original_id.astype("int32")
    # intersection with target area
    hp_junctions = gpd.overlay(hp_junctions, grid_data.area, how="intersection")
    keys = grid_data.area.keys().tolist()
    keys.remove("geometry")
    hp_junctions.drop(columns=(keys), inplace=True)
    # consider data only if there are more than one junction in the target area
    if len(hp_junctions) > 1:
        # add dave name
        hp_junctions.reset_index(drop=True, inplace=True)
        hp_junctions.insert(
            0, "dave_name", pd.Series(list(map(lambda x: f"junction_1_{x}", hp_junctions.index)))
        )
        # add hp junctions to grid data
        grid_data.hp_data.hp_junctions = grid_data.hp_data.hp_junctions.append(hp_junctions)
        # --- create hp pipes
        hp_pipes = hp_data["hp_pipelines"]
        # filter relevant and real pipelines by checking if both endpoints are in the target area
        hp_junctions_ids = hp_junctions.original_id.tolist()
        hp_pipes = hp_pipes[
            (hp_pipes.START_POIN.isin(hp_junctions_ids))
            & (hp_pipes.END_POINT.isin(hp_junctions_ids))
            & (hp_pipes.VIRTUAL != "1")
        ]
        # prepare data
        hp_pipes = hp_pipes.rename(
            columns={
                "PIPE_ID": "original_id",
                "NAME": "original_name",
                "GASQUALITY": "gasquality",
                "LENGTH_km": "length_km",
                "DIAMETER_mm": "diameter_mm",
                "CLASS": "class",
                "PRESSURE_bar": "pressure_bar",
                "DIAM_EST_mm": "diameter_estimated",
                "CLASS_EST": "class_estimated",
                "PRESS_EST_bar": "pressure_estimated",
                "CAPACITY_gwh_per_d": "capacity_gwh_per_d",
                "OPERATOR": "operator",
                "START_POIN": "from_junction",
                "END_POINT": "to_junction",
            }
        )
        hp_pipes.drop(columns=(["VIRTUAL"]), inplace=True)
        hp_pipes["reference_year"] = 2015
        hp_pipes["source"] = source
        hp_pipes["pressure_level"] = 1
        # change pipeline junction names from id to dave name
        from_junction_new = []
        to_junction_new = []
        for _, pipe in hp_pipes.iterrows():
            from_junction_dave = (
                hp_junctions[hp_junctions.original_id == pipe.from_junction].iloc[0].dave_name
            )
            to_junction_dave = (
                hp_junctions[hp_junctions.original_id == pipe.to_junction].iloc[0].dave_name
            )
            from_junction_new.append(from_junction_dave)
            to_junction_new.append(to_junction_dave)
        hp_pipes["from_junction"] = from_junction_new
        hp_pipes["to_junction"] = to_junction_new
        # add dave name
        hp_pipes.reset_index(drop=True, inplace=True)
        hp_pipes.insert(
            0, "dave_name", pd.Series(list(map(lambda x: f"pipe_1_{x}", hp_pipes.index)))
        )
        # add hd lines to grid data
        grid_data.hp_data.hp_pipes = grid_data.hp_data.hp_pipes.append(hp_pipes)
