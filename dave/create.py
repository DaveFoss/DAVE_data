import os
import timeit
import warnings

import geopandas as gpd
import pandas as pd

from dave import __version__
from dave.components import gas_components, power_components

# imports from dave
from dave.dave_structure import davestructure
from dave.io import from_archiv, pp_to_json, ppi_to_json, to_archiv, to_hdf
from dave.model import create_gas_grid, create_power_grid, gas_processing, power_processing
from dave.plotting import plot_grid_data, plot_landuse, plot_target_area
from dave.settings import dave_settings
from dave.toolbox import create_interim_area
from dave.topology import (
    create_ehv_topology,
    create_hp_topology,
    create_hv_topology,
    create_lp_topology,
    create_lv_topology,
    create_mp_topology,
    create_mv_topology,
    target_area,
)


def create_empty_dataset():
    """
    This function initializes the dave datastructure.

    OUTPUT:
        **grid_data** (attrdict) - dave attrdict with empty tables

    EXAMPLE:
        grid_data = create_empty_dataset()

    """
    # define dave structure
    grid_data = davestructure(
        {
            # target data
            "area": gpd.GeoDataFrame([]),
            "target_input": pd.DataFrame(),
            "buildings": davestructure(
                {
                    "commercial": gpd.GeoDataFrame([]),
                    "for_living": gpd.GeoDataFrame([]),
                    "other": gpd.GeoDataFrame([]),
                }
            ),
            "roads": davestructure(
                {
                    "roads": gpd.GeoDataFrame([]),
                    "roads_plot": gpd.GeoDataFrame([]),
                    "road_junctions": gpd.GeoSeries([]),
                }
            ),
            "landuse": gpd.GeoDataFrame([]),
            # power grid data
            "ehv_data": davestructure(
                {"ehv_nodes": gpd.GeoDataFrame([]), "ehv_lines": gpd.GeoDataFrame([])}
            ),
            "hv_data": davestructure(
                {"hv_nodes": gpd.GeoDataFrame([]), "hv_lines": gpd.GeoDataFrame([])}
            ),
            "mv_data": davestructure(
                {"mv_nodes": gpd.GeoDataFrame([]), "mv_lines": gpd.GeoDataFrame([])}
            ),
            "lv_data": davestructure(
                {"lv_nodes": gpd.GeoDataFrame([]), "lv_lines": gpd.GeoDataFrame([])}
            ),
            "components_power": davestructure(
                {
                    "loads": gpd.GeoDataFrame([]),
                    "renewable_powerplants": gpd.GeoDataFrame([]),
                    "conventional_powerplants": gpd.GeoDataFrame([]),
                    "transformers": davestructure(
                        {
                            "ehv_ehv": gpd.GeoDataFrame([]),
                            "ehv_hv": gpd.GeoDataFrame([]),
                            "hv_mv": gpd.GeoDataFrame([]),
                            "mv_lv": gpd.GeoDataFrame([]),
                        }
                    ),
                    "substations": davestructure(
                        {
                            "ehv_hv": gpd.GeoDataFrame([]),
                            "hv_mv": gpd.GeoDataFrame([]),
                            "mv_lv": gpd.GeoDataFrame([]),
                        }
                    ),
                }
            ),
            # gas grid data
            "hp_data": davestructure(
                {"hp_junctions": gpd.GeoDataFrame([]), "hp_pipes": gpd.GeoDataFrame([])}
            ),
            "mp_data": davestructure(
                {"mp_junctions": gpd.GeoDataFrame([]), "mp_pipes": gpd.GeoDataFrame([])}
            ),
            "lp_data": davestructure(
                {"lp_junctions": gpd.GeoDataFrame([]), "lp_pipes": gpd.GeoDataFrame([])}
            ),
            "components_gas": davestructure(
                {
                    "compressors": gpd.GeoDataFrame([]),
                    "sources": gpd.GeoDataFrame([]),
                    "storages_gas": gpd.GeoDataFrame([]),
                }
            ),
            # auxillary
            "dave_version": __version__,
            "meta_data": {},
        }
    )
    return grid_data


def create_grid(
    postalcode=None,
    town_name=None,
    federal_state=None,
    nuts_region=None,
    own_area=None,
    power_levels=[],
    gas_levels=[],
    plot=True,
    convert=True,
    opt_model=True,
    combine_areas=[],
    transformers=True,
    renewable_powerplants=True,
    conventional_powerplants=True,
    loads=True,
    compressors=True,
    sources=True,
    storages_gas=True,
    valve=True,
    output_folder=dave_settings()["dave_output_dir"],
    api_use=True,
):
    """
    This is the main function of dave. This function generates automaticly grid models for power
    and gas networks in the defined target area

    INPUT:
        One of these parameters must be set: \n
        **postalcode** (List of strings) - numbers of the target postalcode areas. it could also \
            be choose ['ALL'] for all postalcode areas in germany \n
        **town_name** (List of strings) - names of the target towns it could also be choose \
            ['ALL'] for all citys in germany \n
        **federal_state** (List of strings) - names of the target federal states it could also be \
            choose ['ALL'] for all federal states in germany \n
        **nuts_region** (List of strings) - codes of the target nuts regions (independent from \
            nuts level). it could also be choose ['ALL'] for all nuts regions in europe \n
        **own_area** (string) - absolute path to a shape file which includes own target area \
            (e.g. "C:/Users/name/test/test.shp") \n

    OPTIONAL:
        **power_levels** (list, default []) - this parameter defines which power levels should be \
            considered. options: 'EHV','HV','MV','LV', []. there could be choose: one/multiple \
                level(s) or 'ALL' \n
        **gas_levels** (list, default []) - this parameter defines which gas levels should be \
            considered. options: 'HP','MP','LP', []. there could be choose: one/multiple level(s) \
            or 'ALL' \n
        **plot** (boolean, default True) - if this value is true dave creates plottings \
            automaticly \n
        **convert** (boolean, default True) - if this value is true dave will be convert the grid \
            automaticly to pandapower and pandapipes \n
        **opt_model** (boolean, default True) - if this value is true dave will be use the optimal \
            power flow calculation to get no boundary violations \n
        **combine_areas** (list, default []) - this parameter defines on which power levels not \
            connected areas should combined. options: 'EHV','HV','MV','LV', [] \n
        **transformers** (boolean, default True) - if true, transformers are added to the grid \
            model \n
        **renewable_powerplants** (boolean, default True) - if true, renewable powerplans are \
            added to the grid model \n
        **conventional_powerplants** (boolean, default True) - if true, conventional powerplans \
            are added to the grid model \n
        **loads** (boolean, default True) - if true, loads are added to the grid model \n
        **compressors** (boolean, default True) - if true, compressors are added to the grid \
            model \n
        **sources** (boolean, default True) - if true, gas sources are added to the grid model \n
        **storages_gas** (boolean, default True) - if true, gas storages are added to the grid \
            model \n
        **valve** (boolean, default True) - if true, gas valves are added to the grid model \n
        **output_folder** (string, default user desktop) - absolute path to the folder where the \
            generated data should be saved. if for this path no folder exists, dave will be \
                create one
        **api_use** (boolean, default True) - if true, the resulting data will not stored in a \
            local folder

    OUTPUT:
        **grid_data** (attrdict) - grid_data as a attrdict in dave structure \n
        **net_power** \n
        **net_pipes** \n

    EXAMPLE:
        from dave.create import create_grid

        grid_data  = create_grid(town_name=['Kassel', 'Baunatal'], power_levels=['HV', 'MV'],
                                 gas_levels=['HP'], plot=False, convert = False)

    """
    # start runtime
    _start_time = timeit.default_timer()
    # create empty datastructure
    grid_data = create_empty_dataset()
    #
    # --- adapt level inputs
    # set level inputs to upper strings
    power_levels = list(map(str.upper, power_levels))
    gas_levels = list(map(str.upper, gas_levels))
    combine_areas = list(map(str.upper, combine_areas))
    # convert input value 'ALL'
    if power_levels == ["ALL"]:
        power_levels = ["EHV", "HV", "MV", "LV"]
    if gas_levels == ["ALL"]:
        gas_levels = ["HP", "MP", "LP"]
    # sort level inputs
    order_power = ["EHV", "HV", "MV", "LV"]
    power_sort = sorted(list(map(order_power.index, power_levels)))
    power_levels = list(map(lambda x: order_power[x], power_sort))
    order_gas = ["HP", "MP", "LP"]
    gas_sort = sorted(list(map(order_gas.index, gas_levels)))
    gas_levels = list(map(lambda x: order_gas[x], gas_sort))
    # --- create target area informations
    if ("LV" in power_levels) or ("LP" in gas_levels):
        roads, roads_plot, buildings, landuse = True, True, True, True
    elif ("MV" in power_levels) or ("MP" in gas_levels):
        roads, roads_plot, buildings = True, True, False
        landuse = bool(loads)  # landuse is needed for load calculation
    else:  # for EHV, HV and HP
        roads, roads_plot, buildings = False, False, False
        landuse = bool(loads and power_levels)  # landuse is needed for load calculation
    file_exists, file_name = target_area(
        grid_data,
        power_levels=power_levels,
        gas_levels=gas_levels,
        postalcode=postalcode,
        town_name=town_name,
        federal_state=federal_state,
        nuts_region=nuts_region,
        own_area=own_area,
        buffer=0,
        roads=roads,
        roads_plot=roads_plot,
        buildings=buildings,
        landuse=landuse,
    ).target()
    if not file_exists:
        # create extended grid area to combine not connected areas
        if combine_areas:
            # save origin area
            origin_area = grid_data.area
            # hier dann die erstellung über funktion
            combined_area = create_interim_area(grid_data.area)
        # --- create desired power grid levels
        for level in power_levels:
            # temporary extend grid area to combine not connected areas
            if level in combine_areas:
                # temporary use of extended grid area
                grid_data.area = combined_area
            if level == "EHV":
                create_ehv_topology(grid_data)
            elif level == "HV":
                create_hv_topology(grid_data)
            elif level == "MV":
                create_mv_topology(grid_data)
            elif level == "LV":
                create_lv_topology(grid_data)
            else:
                print("no voltage level was choosen or their is a failure in the input value.")
                print(f"the input for the power levels was: {power_levels}")
                print("---------------------------------------------------")
            # replace grid area with the origin one for further steps
            if level in combine_areas:
                grid_data.area = origin_area
        # create power grid components
        if power_levels:
            power_components(
                grid_data, transformers, renewable_powerplants, conventional_powerplants, loads
            )
        # --- create desired gas grid levels
        for level in gas_levels:
            # temporary extend grid area to combine not connected areas
            if level in combine_areas:
                # temporary use of extended grid area
                grid_data.area = combined_area
            if level == "HP":
                create_hp_topology(grid_data)
            elif level == "MP":
                create_mp_topology(grid_data)
            elif level == "LP":
                create_lp_topology(grid_data)
            else:
                print("no gas level was choosen or their is a failure in the input value.")
                print(f"the input for the gas levels was: {gas_levels}")
                print("-----------------------------------------------")
            # replace grid area with the origin one for further steps
            if level in combine_areas:
                grid_data.area = origin_area
        # create gas grid components
        if gas_levels:
            gas_components(grid_data, compressors, sources, storages_gas, valve)
    else:
        # read dataset from archiv
        grid_data = from_archiv(f"{file_name}.h5")

    # create dave output folder on desktop for DaVe dataset, plotting and converted model
    if not api_use:
        print(f"\nSave DaVe output data at the following path: {output_folder}")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

    # save DaVe dataset to archiv and also in the output folder
    if not grid_data.target_input.iloc[0].typ == "own area":
        """this function is temporary taken out for development
        print('Save DaVe dataset to archiv')
        print('----------------------------------')
        # check if archiv folder exists otherwise create one
        archiv_dir = dave_settings()["dave_dir"] + '\\datapool\\dave_archiv\\'
        if not os.path.exists(archiv_dir):
            os.makedirs(archiv_dir)
        with warnings.catch_warnings():
            # filter warnings because of the PerformanceWarning from pytables at the geometry type
            warnings.simplefilter('ignore')
            # save dataset to archiv
            file_name = to_archiv(grid_data)
        """
    # save DaVe dataset to the output folder
    if not api_use:
        with warnings.catch_warnings():
            # filter warnings because of the PerformanceWarning from pytables at the geometry type
            warnings.simplefilter("ignore")
            to_hdf(grid_data, dataset_path=output_folder + "\\" + "dave_dataset.h5")

    # plot informations
    if plot:
        if "LV" in power_levels:
            plot_target_area(grid_data, api_use, output_folder)
        plot_grid_data(grid_data, api_use, output_folder)
        # plot_landuse(grid_data, api_use, output_folder)

    # convert into pandapower and pandapipes
    if convert and power_levels:
        net_power = create_power_grid(grid_data)
        net_power = power_processing(net_power, opt_model=opt_model)
        # save grid model in the dave output folder
        if not api_use:
            file_path = output_folder + "\\dave_power_grid.json"
            pp_to_json(net_power, file_path)
    else:
        net_power = None
    if convert and gas_levels:
        net_gas = create_gas_grid(grid_data)
        net_gas = gas_processing(net_gas)
        # save grid model in the dave output folder
        if not api_use:
            file_path = output_folder + "\\dave_gas_grid.json"
            ppi_to_json(net_gas, file_path)
    else:
        net_gas = None

    # return runtime
    _stop_time = timeit.default_timer()
    print("runtime = " + str(round((_stop_time - _start_time) / 60, 2)) + " min")

    # return data
    if net_power and net_gas:
        return grid_data, net_power, net_gas
    elif net_power:
        return grid_data, net_power
    elif net_gas:
        return grid_data, net_gas
    else:
        return grid_data
