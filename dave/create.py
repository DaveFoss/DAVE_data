import os
import timeit
import warnings

import geopandas as gpd
import pandas as pd

# imports from dave
from dave import __version__
from dave.components import (
    create_conventional_powerplants,
    create_loads,
    create_power_plant_lines,
    create_renewable_powerplants,
    create_transformers,
    gas_components,
)
from dave.dave_structure import davestructure
from dave.geography import target_area
from dave.io import from_archiv, to_archiv, to_hdf, to_json
from dave.model import create_pandapipes, create_pandapower
from dave.plotting import plot_geographical_data, plot_grid_data, plot_landuse
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
                    "sinks": gpd.GeoDataFrame([]),
                    "sources": gpd.GeoDataFrame([]),
                    "storages_gas": gpd.GeoDataFrame([]),
                    "valves": gpd.GeoDataFrame([]),
                }
            ),
            # auxillary
            "dave_version": __version__,
            "meta_data": {},
        }
    )
    return grid_data


def format_input_levels(power_levels, gas_levels):
    """
    This function formats the power and gas levels to get the right format for the dave processing
    """
    # set level inputs to upper strings
    power_levels = list(map(str.lower, power_levels))
    gas_levels = list(map(str.lower, gas_levels))
    # convert input value 'ALL'
    if power_levels == ["all"]:
        power_levels = ["ehv", "hv", "mv", "lv"]
    if gas_levels == ["all"]:
        gas_levels = ["hp", "mp", "lp"]
    # sort level inputs
    order_power = ["ehv", "hv", "mv", "lv"]
    power_sort = sorted(list(map(order_power.index, power_levels)))
    power_levels = list(map(lambda x: order_power[x], power_sort))
    order_gas = ["hp", "mp", "lp"]
    gas_sort = sorted(list(map(order_gas.index, gas_levels)))
    gas_levels = list(map(lambda x: order_gas[x], gas_sort))
    return power_levels, gas_levels


def geo_info_needs(power_levels, gas_levels, loads):
    """
    This function decides which geographical informations are necessary for the different grid
    levels
    """
    # check power and gas level and set decision for geographical parameters
    if ("lv" in power_levels) or ("lp" in gas_levels):
        roads, roads_plot, buildings, landuse = True, True, True, True
    elif ("mv" in power_levels) or ("mp" in gas_levels):
        roads, roads_plot, buildings = True, True, False
        landuse = bool(loads)  # landuse is needed for load calculation
    else:  # for ehv, hv and hp
        roads, roads_plot, buildings = False, False, False
        landuse = bool(loads and power_levels)  # landuse is needed for load calculation
    return roads, roads_plot, buildings, landuse


def save_dataset_to_archiv(grid_data):
    """
    This function saves the dave dataset in the own archiv.
    Hint: datasets based on own area definitions will not be saved
    """
    print("Save DaVe dataset to archiv")
    print("----------------------------------")
    # check if archiv folder exists otherwise create one
    archiv_dir = dave_settings()["dave_dir"] + "\\datapool\\dave_archiv\\"
    if not os.path.exists(archiv_dir):
        os.makedirs(archiv_dir)
    with warnings.catch_warnings():
        # filter warnings because of the PerformanceWarning from pytables at the geometry type
        warnings.simplefilter("ignore")
        # save dataset to archiv
        file_name = to_archiv(grid_data)


def create_grid(
    postalcode=None,
    town_name=None,
    federal_state=None,
    nuts_region=None,
    own_area=None,
    roads=False,
    roads_plot=False,
    buildings=False,
    landuse=False,
    power_levels=[],
    gas_levels=[],
    plot=True,
    convert_power=[],
    convert_gas=[],
    opt_model=True,
    combine_areas=[],
    transformers=True,
    renewable_powerplants=True,
    conventional_powerplants=True,
    loads=True,
    compressors=True,
    sinks=True,
    sources=True,
    storages_gas=True,
    valves=True,
    output_folder=dave_settings()["dave_output_dir"],
    output_format="json",
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
        **roads** (bool, default False) - if true, road information are added to the grid \
            model which are grid relevant \n
        **roads_plot** (bool, default False) - if true, road information are added to the grid \
            model which are only for a better orientation in the plotting \n
        **buildings** (bool, default False) - if true, building information are added to the grid \
            model \n
        **landuse** (bool, default False) - if true, landuse information are added to the grid \
            model \n
        **power_levels** (list, default []) - this parameter defines which power levels should be \
            considered. options: 'ehv','hv','mv','lv', []. there could be choose: one/multiple \
                level(s) or 'ALL' \n
        **gas_levels** (list, default []) - this parameter defines which gas levels should be \
            considered. options: 'hp','mp','lp', []. there could be choose: one/multiple level(s) \
            or 'ALL' \n
        **plot** (boolean, default True) - if this value is true dave creates plottings \
            automaticly \n
        **convert_power** (list, default []) - this parameter defines in witch formats the power \
            grid data should be converted. Available formats are currently: 'pandapower' \n
        **convert_gas** (list, default []) - this parameter defines in witch formats the gas \
            grid data should be converted. Available formats are currently: 'pandapipes' \n
        **opt_model** (boolean, default True) - if this value is true dave will be use the optimal \
            power flow calculation to get no boundary violations. Currently a experimental feature \
                and only available for pandapower \n
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
        **sinks** (boolean, default True) - if true, gas sinks are added to the grid model \n
        **sources** (boolean, default True) - if true, gas sources are added to the grid model \n
        **storages_gas** (boolean, default True) - if true, gas storages are added to the grid \
            model \n
        **valves** (boolean, default True) - if true, gas valves are added to the grid model \n
        **output_folder** (string, default user desktop) - absolute path to the folder where the \
            generated data should be saved. if for this path no folder exists, dave will be \
                create one \n
        **output_format** (string, default 'json') - this parameter defines the output format. \
            Available formats are currently: 'json' and 'hdf' \n
        **api_use** (boolean, default True) - if true, the resulting data will not stored in a \
            local folder

    OUTPUT:
        **grid_data** (attrdict) - grid_data as a attrdict in dave structure \n
        **net_power** \n
        **net_pipes** \n

    EXAMPLE:
        from dave.create import create_grid

        grid_data  = create_grid(town_name=['Kassel', 'Baunatal'], power_levels=['hv', 'mv'],
                                 gas_levels=['HP'], plot=False, convert = False)

    """
    # start runtime
    _start_time = timeit.default_timer()

    # create empty datastructure
    grid_data = create_empty_dataset()

    # format level inputs
    power_levels, gas_levels = format_input_levels(power_levels, gas_levels)
    combine_areas = list(map(str.lower, combine_areas))

    # create target area informations
    roads_l, roads_plot_l, buildings_l, landuse_l = geo_info_needs(power_levels, gas_levels, loads)
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
        roads=bool(roads or roads_l),
        roads_plot=bool(roads_plot or roads_plot_l),
        buildings=bool(buildings or buildings_l),
        landuse=bool(landuse or landuse_l),
    ).target()

    # --- collect data for the requested dataset
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
            if level == "ehv":
                create_ehv_topology(grid_data)
            elif level == "hv":
                create_hv_topology(grid_data)
            elif level == "mv":
                create_mv_topology(grid_data)
            elif level == "lv":
                create_lv_topology(grid_data)
            else:
                print("no voltage level was choosen or their is a failure in the input value.")
                print(f"the input for the power levels was: {power_levels}")
                print("---------------------------------------------------")
            # replace grid area with the origin one for further steps
            if level in combine_areas:
                grid_data.area = origin_area
        # --- create power grid components
        if power_levels:
            # add transformers
            if transformers:
                create_transformers(grid_data)
            # add renewable powerplants
            if renewable_powerplants:
                create_renewable_powerplants(grid_data)
            # add conventional powerplants
            if conventional_powerplants:
                create_conventional_powerplants(grid_data)
            # create lines for power plants with a grid node far away
            if renewable_powerplants or conventional_powerplants:
                create_power_plant_lines(grid_data)
            # add loads
            if loads:
                create_loads(grid_data)
        # --- create desired gas grid levels
        for level in gas_levels:
            # temporary extend grid area to combine not connected areas
            if level in combine_areas:
                # temporary use of extended grid area
                grid_data.area = combined_area
            if level == "hp":
                create_hp_topology(grid_data)
            elif level == "mp":
                create_mp_topology(grid_data)
            elif level == "lp":
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
            gas_components(grid_data, compressors, sinks, sources, storages_gas, valves)
    else:
        # read dataset from archiv
        grid_data = from_archiv(f"{file_name}.h5")

    # save DaVe dataset to archiv
    if not grid_data.target_input.iloc[0].typ == "own area":
        # this function is temporary taken out for development
        # save_dataset_to_archiv(grid_data)
        pass

    # save informations in user folder
    if not api_use:
        # create dave output folder on desktop for DaVe dataset, plotting and converted model
        print(f"\nSave DaVe output data at the following path: {output_folder}")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        # save DaVe dataset to the output folder but not in api modus
        with warnings.catch_warnings():
            # filter warnings because of the PerformanceWarning from pytables at the geometry type
            warnings.simplefilter("ignore")
            if output_format == "json":
                to_json(grid_data, file_path=output_folder + "\\" + "dave_dataset.json")
            elif output_format == "hdf":
                to_hdf(grid_data, dataset_path=output_folder + "\\" + "dave_dataset.h5")

    # plot informations
    if plot:
        if "lv" in power_levels:
            plot_geographical_data(grid_data, api_use, output_folder)
        plot_grid_data(grid_data, api_use, output_folder)
        # plot_landuse(grid_data, api_use, output_folder)

    # convert power model
    if convert_power and power_levels:
        if "pandapower" in convert_power:
            net_power = create_pandapower(
                grid_data, opt_model=opt_model, api_use=api_use, output_folder=output_folder
            )
    else:
        net_power = None
    # convert gas model
    if convert_gas and gas_levels:
        if "pandapipes" in convert_gas:
            net_gas = create_pandapipes(grid_data, api_use=api_use, output_folder=output_folder)
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
