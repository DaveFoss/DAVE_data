# Copyright (c) 2022-2024 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from os import environ, makedirs, path
from timeit import default_timer
from warnings import catch_warnings, simplefilter

environ["USE_PYGEOS"] = "0"  # use shapely 2.0 instead of pygeos at geopandas

# imports from dave
from dave_data.archiv_io import from_archiv, to_archiv
from dave_data.components.gas_components import gas_components
from dave_data.components.loads import create_loads
from dave_data.components.power_plants import (
    create_conventional_powerplants,
    create_power_plant_lines,
    create_renewable_powerplants,
)
from src.dave_data.components.transformers import create_transformers
from dave_data.geography import target_area
from src.dave_data.model_utils import clean_up_data
from dave_data.settings import dave_settings
from dave_data.toolbox import create_interim_area
from dave_data.topology.extra_high_voltage import create_ehv_topology
from src.dave_data.topology.high_pressure import create_hp_topology
from src.dave_data.topology.high_voltage import create_hv_topology
from dave_data.topology.low_voltage import create_lv_topology
from dave_data.topology.medium_voltage import create_mv_topology
from dave_data.dave_structure import create_empty_dataset
from dave_data.io.file_io import to_gpkg, to_hdf, to_json
from dave_data.converter.create_gaslib import create_gaslib
from dave_data.converter.create_mynts import create_mynts
from dave_data.converter.create_pandapipes import create_pandapipes
from dave_data.converter.create_pandapower import create_pandapower


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
        roads, roads_plot, buildings = False, False, False
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
    archiv_dir = dave_settings["dave_dir"] + "\\datapool\\dave_archiv\\"
    if not path.exists(archiv_dir):
        makedirs(archiv_dir)
    with catch_warnings():
        # filter warnings because of the PerformanceWarning from pytables at the geometry type
        simplefilter("ignore")
        # save dataset to archiv
        to_archiv(grid_data)


def save_dataset_to_user_folder(grid_data, output_format, output_folder, api_use):
    """
    This function saves the DAVE dataset to an output folder.

    Input:
        **grid_data** (attrdict) - dave attrdict with empty tables
        **output_format** (string, default 'json') - this parameter defines the output format. \
            Available formats are currently: 'json', 'hdf' and 'gpkg' \n
        **output_folder** (string, default user desktop) - absolute path to the folder where the \
            generated data should be saved. if for this path no folder exists, dave will be \
                create one \n
        **api_use** (boolean, default True) - if true, the resulting data will not stored in a \
            local folder
    OUTPUT:
        **grid_data** (attrdict) - grid_data as a attrdict in dave structure \n
    """
    if not api_use:
        with catch_warnings():
            # filter warnings because of the PerformanceWarning from pytables at the geometry type
            simplefilter("ignore")
            if output_format == "json":
                to_json(grid_data, file_path=output_folder + "\\" + "dave_dataset.json")
            elif output_format == "hdf":
                to_hdf(grid_data, file_path=output_folder + "\\" + "dave_dataset.h5")
            elif output_format == "gpkg":
                to_gpkg(grid_data, file_path=output_folder + "\\" + "dave_dataset.gpkg")


def create_grid(
    postalcode=None,
    town_name=None,
    federal_state=None,
    nuts_region=None,
    own_area=None,
    geodata=[],
    power_levels=[],
    gas_levels=[],
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
    building_height=False,
    census=[],
    heat=[],
    output_folder=dave_settings["dave_output_dir"],
    output_format="json",
    api_use=True,
):
    """
    This is the main function of dave_data. This function generates automaticly grid models for power
    and gas networks in the defined target area

    INPUT:
        One of these parameters must be set: \n
        **postalcode** (List of strings) - numbers of the target postalcode areas. it could also \
            be choose ['ALL'] for all postalcode areas in germany \n
        **town_name** (List of strings) - names of the target towns it could also be choose \
            ['ALL'] for all citys in germany \n
        **federal_state** (List of strings) - names of the target federal states it could also be \
            choose ['ALL'] for all federal states in germany \n
        **nuts_region** (tuple(List of strings, string)) - this tuple includes first a list of the \
            target nuts regions codes (independent from nuts level). It could also be choose ['ALL'] \
            for all nuts regions in europe. The second tuple parameter defines the nuts \
            year as string. The year options are 2013, 2016 and 2021. \n
        **own_area** (string / Polygon) - First Option for this parameter is to hand over a string \
            which could be the absolute path to a shape file which includes own target area \
            (e.g. "C:/Users/name/test/test.shp") or a JSON string with the area information. The \
            second option is to hand over a shapely Polygon which defines the area \n

    OPTIONAL:
        **geodata** (list, default []) - this parameter defines which geodata should be considered.\
            options: 'roads','roads_plot','buildings','landuse', 'railways', 'waterways', []. \
                there could be choose: one/multiple geoobjects or 'ALL' \n
        **power_levels** (list, default []) - this parameter defines which power levels should be \
            considered. options: 'ehv','hv','mv','lv', []. there could be choose: one/multiple \
                level(s) or 'ALL' \n
        **gas_levels** (list, default []) - this parameter defines which gas levels should be \
            considered. options: 'hp' and []. there could be choose: one/multiple level(s) \
            or 'ALL' \n
        **convert_power** (list, default []) - this parameter defines in witch formats the power \
            grid data should be converted. Available formats are currently: 'pandapower' \n
        **convert_gas** (list, default []) - this parameter defines in witch formats the gas \
            grid data should be converted. Available formats are currently: 'pandapipes', 'gaslib', \
            'mynts' \n
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
        **output_folder** (string, default user desktop) - absolute path to the folder where the \
            generated data should be saved. if for this path no folder exists, dave will be \
                create one \n
        **output_format** (string, default 'json') - this parameter defines the output format. \
            Available formats are currently: 'json', 'hdf' and 'gpkg' \n
        **api_use** (boolean, default True) - if true, the resulting data will not stored in a \
            local folder

    OUTPUT:
        **grid_data** (attrdict) - grid_data as a attrdict in dave structure \n
        **net_power** \n
        **net_pipes** \n

    EXAMPLE:
        from dave_data.create import create_grid

        grid_data  = create_grid(town_name=['Kassel', 'Baunatal'], power_levels=['hv', 'mv'],
                                 gas_levels=['HP'], plot=False, convert = False)

    """
    # start runtime
    _start_time = default_timer()

    # create dave output folder for DaVe dataset, plotting and converted model
    if not api_use:
        if not path.exists(output_folder):
            makedirs(output_folder)

    # create empty datastructure
    grid_data = create_empty_dataset()

    # format level inputs
    power_levels, gas_levels = format_input_levels(power_levels, gas_levels)
    combine_areas = list(map(str.lower, combine_areas))

    # create geographical informations
    geodata = list(map(str.lower, geodata))
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
        roads=bool("roads" in geodata or "ALL" in geodata or roads_l),
        roads_plot=bool("roads_plot" in geodata or "ALL" in geodata or roads_plot_l),
        buildings=bool("buildings" in geodata or "ALL" in geodata or buildings_l),
        landuse=bool("landuse" in geodata or "ALL" in geodata or landuse_l),
        railways=bool("railways" in geodata or "ALL" in geodata),
        waterways=bool("waterways" in geodata or "ALL" in geodata),
    )
    # save interim status of the informations in user folder
    save_dataset_to_user_folder(grid_data, output_format, output_folder, api_use)

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
                # save interim status of the informations in user folder
                save_dataset_to_user_folder(grid_data, output_format, output_folder, api_use)
            elif level == "hv":
                create_hv_topology(grid_data)
                # save interim status of the informations in user folder
                save_dataset_to_user_folder(grid_data, output_format, output_folder, api_use)
            elif level == "mv":
                create_mv_topology(grid_data)
                # save interim status of the informations in user folder
                save_dataset_to_user_folder(grid_data, output_format, output_folder, api_use)
            elif level == "lv":
                create_lv_topology(grid_data)
                # save interim status of the informations in user folder
                save_dataset_to_user_folder(grid_data, output_format, output_folder, api_use)
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
                # save interim status of the informations in user folder
                save_dataset_to_user_folder(grid_data, output_format, output_folder, api_use)
            # add renewable powerplants
            if renewable_powerplants:
                create_renewable_powerplants(grid_data)
                # save interim status of the informations in user folder
                save_dataset_to_user_folder(grid_data, output_format, output_folder, api_use)
            # add conventional powerplants
            if conventional_powerplants:
                create_conventional_powerplants(grid_data)
                # save interim status of the informations in user folder
                save_dataset_to_user_folder(grid_data, output_format, output_folder, api_use)
            # create lines for power plants with a grid node far away
            if renewable_powerplants or conventional_powerplants:
                create_power_plant_lines(grid_data)
                # save interim status of the informations in user folder
                save_dataset_to_user_folder(grid_data, output_format, output_folder, api_use)
            # add loads
            if loads:
                create_loads(grid_data)
                # save interim status of the informations in user folder
                save_dataset_to_user_folder(grid_data, output_format, output_folder, api_use)
        # --- create desired gas grid levels
        for level in gas_levels:
            # temporary extend grid area to combine not connected areas
            if level in combine_areas:
                # temporary use of extended grid area
                grid_data.area = combined_area
            if level == "hp":
                create_hp_topology(grid_data)
                # save interim status of the informations in user folder
                save_dataset_to_user_folder(grid_data, output_format, output_folder, api_use)
            else:
                print("no gas level was choosen or their is a failure in the input value.")
                print(f"the input for the gas levels was: {gas_levels}")
                print("-----------------------------------------------")
            # replace grid area with the origin one for further steps
            if level in combine_areas:
                grid_data.area = origin_area
        # create gas grid components
        if gas_levels:
            gas_components(grid_data, compressors, sinks, sources)
            # save interim status of the informations in user folder
            save_dataset_to_user_folder(grid_data, output_format, output_folder, api_use)

        # clean up power and gas grid data
        clean_up_data(grid_data)
    else:
        # read dataset from archiv
        grid_data = from_archiv(f"{file_name}.h5")

    # save DaVe dataset to archiv
    if not grid_data.target_input.iloc[0].typ == "own area":
        # this function is temporary taken out for development
        # save_dataset_to_archiv(grid_data)
        pass

    # save informations in user folder
    save_dataset_to_user_folder(grid_data, output_format, output_folder, api_use)

    # convert power model
    net_power = None
    if convert_power:
        if "pandapower" in convert_power:
            net_power = create_pandapower(
                grid_data, opt_model=opt_model, output_folder=output_folder
            )

    # convert gas model
    net_gas = None
    if convert_gas:
        if "pandapipes" in convert_gas:
            net_gas = create_pandapipes(grid_data, output_folder=output_folder)
        if "gaslib" in convert_gas:
            create_gaslib(
                grid_data, output_folder=output_folder
            )  # !!! how to handle net_gas at multiple conversions
        if "mynts" in convert_gas:
            create_mynts(grid_data, basefilepath=output_folder)

    # show general informations from the generating process
    if not api_use:
        # print output folder
        print(f"\nSave DaVe output data at the following path: {output_folder}")
        # return runtime
        _stop_time = default_timer()
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
