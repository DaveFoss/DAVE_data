import geopandas as gpd
import pandas as pd
from tqdm import tqdm

from dave.datapool import read_scigridgas_iggielgn
from dave.settings import dave_settings


def sources(grid_data, scigrid_prductions):
    """
    This function adds the data for gas production
    """
    # read_scigridgas_iggielgn()
    pass


def compressors(grid_data, scigrid_compressors):
    """
    This function adds the data for gas compressors
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create compressors:                ",
        position=0,
        bar_format=dave_settings()["bar_format"],
    )
    # get compressor data
    compressors = scigrid_compressors.copy()
    # prepare data
    compressors.rename(columns={"id": "scigrid_id", "name": "scigrid_name"}, inplace=True)
    compressors["source"] = "scigridgas"
    # intersection with target area
    compressors = gpd.overlay(compressors, grid_data.area, how="intersection")
    keys = grid_data.area.keys().tolist()
    keys.remove("geometry")
    compressors = compressors.drop(columns=(keys))
    # update progress
    pbar.update(40)
    # search for junction dave name
    junctions = grid_data.hp_data.hp_junctions.copy()
    compressors["junction"] = compressors.node_id.apply(
        lambda x: junctions[junctions.scigrid_id == eval(x)[0]].iloc[0].dave_name
    )
    # set grid level number
    compressors["pressure_level"] = 1
    # update progress
    pbar.update(40)
    # add dave name
    compressors.reset_index(drop=True, inplace=True)
    compressors.insert(
        0, "dave_name", pd.Series(list(map(lambda x: f"compressor_1_{x}", compressors.index)))
    )
    # set crs
    compressors.set_crs(dave_settings()["crs_main"], inplace=True)
    # add hp junctions to grid data
    grid_data.components_gas.compressors = grid_data.components_gas.compressors.append(compressors)
    # update progress
    pbar.update(20)
    # close progress bar
    pbar.close()


def storages_gas(grid_data, scigrid_storages):
    pass
    # gas storages in germany
    # read_gas_storage_ugs()
    # read_scigridgas_iggielgn()


def sinks(grid_data, scigrid_consumers):
    """
    This function adds the data for gas consumers
    """
    # read_scigridgas_iggielgn() consumers
    pass


def valves(grid_data):
    """
    This function adds the data for valves between junctions
    """
    # At this time there are no data source for valves availible
    pass


def gas_components(grid_data, compressor, sink, source, storage_gas, valve):
    """
    This function calls all the functions for creating the gas components in the wright order
    """
    # read high pressure grid data from dave datapool (scigridgas igginl)
    if any([compressor, source, sink, storage_gas]):
        scigrid_data, meta_data = read_scigridgas_iggielgn()
        # add meta data
        if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
            grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
    # add compressors
    if compressor:
        compressors(grid_data, scigrid_compressors=scigrid_data["compressors"])
    # add sinks
    if sink:
        sinks(grid_data, scigrid_consumers=scigrid_data["consumers"])
    # add sources
    if source:
        sources(grid_data, scigrid_prductions=scigrid_data["productions"])
    # add storages
    if storage_gas:
        storages_gas(grid_data, scigrid_storages=scigrid_data["storages"])
    # add valves
    if valve:
        valves(grid_data)
