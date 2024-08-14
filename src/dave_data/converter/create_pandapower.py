# Copyright (c) 2022-2024 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from pandapower import (
    available_std_types,
    create_buses,
    create_empty_network,
    create_ext_grid,
    create_gens,
    create_lines,
    create_loads,
    create_replacement_switch_for_branch,
    create_sgens,
    diagnostic,
    drop_buses,
    drop_lines,
    runopp,
    runpp,
)
from pandas import DataFrame, Series, concat, isna
from shapely.geometry import MultiLineString
from tqdm import tqdm

from dave_data.io.file_io import pp_to_json
from dave_data.settings import dave_settings
from dave_data.toolbox import multiline_coords


def create_pp_buses(net, buses):
    if "dave_name" in buses.keys():
        buses.rename(columns={"dave_name": "name"}, inplace=True)
    else:
        buses.insert(
            0, "name", Series(list(map(lambda x: f"node_{x}", buses.index)))
        )  # TODO: hier fehlt noch das voltage level
    if "voltage_kv" in buses.keys():
        buses.rename(columns={"voltage_kv": "vn_kv"}, inplace=True)
    # create buses
    create_buses(
        net,
        nr_buses=len(buses),
        vn_kv=buses["vn_kv"],
        name=buses["name"],
        type=(
            "b"
            if "type" not in buses.keys() or all(buses.type.isna())
            else buses.type.apply(lambda x: "b" if isna(x) else x)
        ),
        geodata=buses.geometry.apply(lambda x: (x.coords[:][0][0], x.coords[:][0][1])).to_list(),
        in_service=(
            bool(True)
            if "in_service" not in buses.keys() or all(buses.in_service.isna())
            else buses.in_service.apply(lambda x: bool(True) if isna(x) else x)
        ),
    )


def create_pp_ehvhv_lines(
    net, lines
):  # TODO: Umschreiben auf pp.create_lines und evt mit mvlv script (unten) mergen
    lines.rename(columns={"dave_name": "name"}, inplace=True)
    lines["from_bus"] = lines.from_bus.apply(lambda x: net.bus[net.bus["name"] == x].index[0])
    lines["to_bus"] = lines.to_bus.apply(lambda x: net.bus[net.bus["name"] == x].index[0])
    lines["type"] = lines.type.apply(lambda x: "ol" if isna(x) else x)
    # geodata
    coords_ehvhv = DataFrame(
        {
            "coords": lines.geometry.apply(
                lambda x: [
                    list(coords)
                    for coords in (
                        multiline_coords(x) if isinstance(x, MultiLineString) else x.coords[:]
                    )
                ]
            )
        }
    )
    # write line data into pandapower structure
    net.line = concat([net.line, lines], ignore_index=True)
    net.line_geodata = concat([net.line_geodata, coords_ehvhv], ignore_index=True)
    # check necessary parameters and add pandapower standard if needed  #TODO Der Teil kann raus, wenn die ehvhv lines auch über create lines gemacht werden
    net.line["in_service"] = (
        bool(True)
        if all(net.line.in_service.isna())
        else net.line.in_service.apply(lambda x: bool(True) if isna(x) else x)
    )
    net.line["df"] = (
        float(1)
        if all(net.line.df.isna())
        else net.line.df.apply(lambda x: float(1) if isna(x) else x)
    )
    net.line["parallel"] = (
        int(1)
        if all(net.line.parallel.isna())
        else net.line.parallel.apply(lambda x: int(1) if isna(x) else x)
    )
    net.line["std_type"] = (
        None
        if all(net.line.std_type.isna())
        else net.line.std_type.apply(lambda x: None if isna(x) else x)
    )
    net.line["g_us_per_km"] = (
        float(0)
        if all(net.line.g_us_per_km.isna())
        else net.line.g_us_per_km.apply(lambda x: float(0) if isna(x) else x)
    )


def create_pp_mvlv_lines(net, lines):
    # create line names
    if "dave_name" in lines.keys():
        lines.rename(columns={"dave_name": "name"}, inplace=True)
    else:
        lines.insert(
            0, "name", Series(list(map(lambda x: f"line_{x}", lines.index)))
        )  # TODO: hier fehlt noch das voltage level
    # create lines
    create_lines(
        net,
        from_buses=lines.from_bus.apply(lambda x: net.bus[net.bus["name"] == x].index[0]),
        to_buses=lines.to_bus.apply(lambda x: net.bus[net.bus["name"] == x].index[0]),
        length_km=lines["length_km"],
        std_type=lines.voltage_level.apply(
            lambda x: {
                5: dave_settings["mv_line_std_type"],
                7: dave_settings["lv_line_std_type"],
            }[x]
        ),
        name=lines["name"],
        geodata=lines.geometry.apply(lambda x: [list(coords) for coords in x.coords[:]]),
        df=(
            float(1)
            if "df" not in lines.keys() or all(lines.df.isna())
            else lines.df.apply(lambda x: float(1) if isna(x) else x)
        ),
        parallel=(
            int(1)
            if "parallel" not in lines.keys() or all(lines.parallel.isna())
            else lines.parallel.apply(lambda x: int(1) if isna(x) else x)
        ),
        in_service=(
            bool(True)
            if "in_service" not in lines.keys() or all(lines.in_service.isna())
            else lines.in_service.apply(lambda x: bool(True) if isna(x) else x)
        ),
    )


def create_pp_trafos(net, grid_data):  # TODO: Umschreiben auf pp.create_lines
    # pp funktionen
    # create_transformers_from_parameters

    # create ehv/ehv, ehv/hv transformers
    trafos_ehvhv = concat(
        [
            grid_data.components_power.transformers.ehv_ehv,
            grid_data.components_power.transformers.ehv_hv,
        ]
    )
    if not trafos_ehvhv.empty:
        trafos_ehvhv.rename(
            columns={
                "dave_name": "name",
                "s_nom_mva": "sn_mva",
                "voltage_kv_hv": "vn_hv_kv",
                "voltage_kv_lv": "vn_lv_kv",
                "phase_shift": "shift_degree",
            },
            inplace=True,
        )
        # trafo über parameter. Dafür müssen die Parameter noch berechnet werden
        # aber wie? wenn ich nur r,x,b, gegeben habe
        trafos_ehvhv["vkr_percent"] = dave_settings["trafo_vkr_percent"]  # dummy value
        trafos_ehvhv["vk_percent"] = dave_settings["trafo_vk_percent"]  # dummy value
        trafos_ehvhv["pfe_kw"] = dave_settings["trafo_pfe_kw"]  # dummy value accepted as ideal
        trafos_ehvhv["i0_percent"] = dave_settings[
            "trafo_i0_percent"
        ]  # dummy value accepted as ideal
        trafos_ehvhv["tap_phase_shifter"] = False  # dummy value accepted as ideal
        trafos_ehvhv["hv_bus"] = trafos_ehvhv.bus_hv.apply(
            lambda x: net.bus[net.bus["name"] == x].index[0]
        )
        trafos_ehvhv["lv_bus"] = trafos_ehvhv.bus_lv.apply(
            lambda x: net.bus[net.bus["name"] == x].index[0]
        )
    # create hv/mv, mv/lv transformers
    trafos_mvlv = concat(
        [
            grid_data.components_power.transformers.hv_mv,
            grid_data.components_power.transformers.mv_lv,
        ]
    )
    if not trafos_mvlv.empty:
        trafos_mvlv.rename(columns={"dave_name": "name"}, inplace=True)
        trafos_mvlv["hv_bus"] = trafos_mvlv.bus_hv.apply(
            lambda x: net.bus[net.bus["name"] == x].index[0]
        )
        trafos_mvlv["lv_bus"] = trafos_mvlv.bus_lv.apply(
            lambda x: net.bus[net.bus["name"] == x].index[0]
        )
        trafos_mvlv["std_type"] = trafos_mvlv.voltage_level.apply(
            lambda x: {
                4: dave_settings["hvmv_trafo_std_type"],
                6: dave_settings["mvlv_trafo_std_type"],
            }[x]
        )
        # add data from standart type
        std_trafo = available_std_types(net, element="trafo")
        trafos_mvlv["i0_percent"] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].i0_percent
        )
        trafos_mvlv["pfe_kw"] = trafos_mvlv.std_type.apply(lambda x: std_trafo.loc[x].pfe_kw)
        trafos_mvlv["vkr_percent"] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].vkr_percent
        )
        trafos_mvlv["sn_mva"] = trafos_mvlv.std_type.apply(lambda x: std_trafo.loc[x].sn_mva)
        trafos_mvlv["vn_lv_kv"] = trafos_mvlv.std_type.apply(lambda x: std_trafo.loc[x].vn_lv_kv)
        trafos_mvlv["vn_hv_kv"] = trafos_mvlv.std_type.apply(lambda x: std_trafo.loc[x].vn_hv_kv)
        trafos_mvlv["vk_percent"] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].vk_percent
        )
        trafos_mvlv["shift_degree"] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].shift_degree
        )
        trafos_mvlv["vector_group"] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].vector_group
        )
        trafos_mvlv["tap_side"] = trafos_mvlv.std_type.apply(lambda x: std_trafo.loc[x].tap_side)
        trafos_mvlv["tap_neutral"] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].tap_neutral
        )
        trafos_mvlv["tap_min"] = trafos_mvlv.std_type.apply(lambda x: std_trafo.loc[x].tap_min)
        trafos_mvlv["tap_max"] = trafos_mvlv.std_type.apply(lambda x: std_trafo.loc[x].tap_max)
        trafos_mvlv["tap_step_degree"] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].tap_step_degree
        )
        trafos_mvlv["tap_step_percent"] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].tap_step_percent
        )
        trafos_mvlv["tap_phase_shifter"] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].tap_phase_shifter
        )
    # write trafo data into pandapower structure
    net.trafo = concat([net.trafo, trafos_ehvhv, trafos_mvlv], ignore_index=True)
    # check necessary parameters and add pandapower standart if needed
    net.trafo["in_service"] = (
        bool(True)
        if all(net.trafo.in_service.isna())
        else net.trafo.in_service.apply(lambda x: bool(True) if isna(x) else x)
    )
    net.trafo["df"] = (
        float(1)
        if all(net.trafo.df.isna())
        else net.trafo.df.apply(lambda x: float(1) if isna(x) else x)
    )
    net.trafo["parallel"] = (
        int(1)
        if all(net.trafo.parallel.isna())
        else net.trafo.parallel.apply(lambda x: int(1) if isna(x) else x)
    )
    net.trafo["shift_degree"] = (
        float(0)
        if all(net.trafo.shift_degree.isna())
        else net.trafo.shift_degree.apply(lambda x: float(0) if isna(x) else x)
    )
    net.trafo["tap_phase_shifter"] = (
        bool(False)
        if all(net.trafo.tap_phase_shifter.isna())
        else net.trafo.tap_phase_shifter.apply(lambda x: bool(False) if isna(x) else x)
    )
    net.trafo["std_type"] = (
        None
        if all(net.trafo.std_type.isna())
        else net.trafo.std_type.apply(lambda x: None if isna(x) else x)
    )


def create_pp_sgens(net, sgens):
    if "name" in sgens.keys():
        sgens.rename(columns={"name": "plant_name"}, inplace=True)
    if "dave_name" in sgens.keys():
        sgens.rename(columns={"dave_name": "name"}, inplace=True)
    else:
        sgens.insert(
            0, "name", Series(list(map(lambda x: f"ren_powerplants_{x}", sgens.index)))
        )  # TODO: hier fehlt noch das voltage level
    if "generation_type" in sgens.keys():
        sgens.rename(columns={"generation_type": "type"}, inplace=True)
    # create sgens
    create_sgens(
        net,
        buses=sgens.bus.apply(lambda x: net.bus[net.bus["name"] == x].index[0]),
        p_mw=sgens.electrical_capacity_kw.apply(lambda x: float(x) / 1000),
        q_mvar=(
            float(0)
            if "q_mvar" not in sgens.keys() or all(sgens.q_mvar.isna())
            else sgens.q_mvar.apply(lambda x: float(0) if isna(x) else x)
        ),
        name=sgens["name"],
        scaling=(
            float(1)
            if "scaling" not in sgens.keys() or all(sgens.scaling.isna())
            else sgens.scaling.apply(lambda x: float(1) if isna(x) else x)
        ),
        type=(
            "wye"
            if "type" not in sgens.keys() or all(sgens.type.isna())
            else sgens.type.apply(lambda x: "wye" if isna(x) else x)
        ),
        in_service=(
            bool(True)
            if "in_service" not in sgens.keys() or all(sgens.in_service.isna())
            else sgens.in_service.apply(lambda x: bool(True) if isna(x) else x)
        ),
        current_source=(
            bool(True)
            if "current_source" not in sgens.keys() or all(sgens.current_source.isna())
            else sgens.current_source.apply(lambda x: bool(True) if isna(x) else x)
        ),
    )


def create_pp_gens(net, gens):
    if "name" in gens.keys():
        gens.rename(columns={"name": "plant_name"}, inplace=True)
    if "dave_name" in gens.keys():
        gens.rename(columns={"dave_name": "name"}, inplace=True)
    else:
        gens.insert(
            0,
            "name",
            Series(list(map(lambda x: f"con_powerplants_{x}", gens.index))),
        )  # TODO: hier fehlt noch das voltage level
    if "type" in gens.keys():
        gens.rename(columns={"type": "type_2"}, inplace=True)
    if "fuel" in gens.keys():
        gens.rename(columns={"fuel": "type"}, inplace=True)
    if "electrical_capacity_mw" in gens.keys():
        gens.rename(columns={"electrical_capacity_mw": "p_mw"}, inplace=True)

    create_gens(
        net,
        buses=gens.bus.apply(lambda x: net.bus[net.bus["name"] == x].index[0]),
        p_mw=gens["p_mw"],
        vm_pu=(
            float(1)
            if "vm_pu" not in gens.keys() or all(gens.vm_pu.isna())
            else gens.vm_pu.apply(lambda x: float(1) if isna(x) else x)
        ),
        name=gens["name"],
        scaling=(
            float(1)
            if "scaling" not in gens.keys() or all(gens.scaling.isna())
            else gens.scaling.apply(lambda x: float(1) if isna(x) else x)
        ),
        slack=(
            bool(False)
            if "slack" not in gens.keys() or all(gens.slack.isna())
            else gens.slack.apply(lambda x: bool(False) if isna(x) else x)
        ),
        in_service=(
            bool(True)
            if "in_service" not in gens.keys() or all(gens.in_service.isna())
            else gens.in_service.apply(lambda x: bool(True) if isna(x) else x)
        ),
    )


def create_pp_loads(net, loads):
    create_loads(
        net,
        buses=loads.bus.apply(lambda x: net.bus[net.bus["name"] == x].index[0]),
        p_mw=loads["p_mw"],
        q_mvar=(
            float(0)
            if "q_mvar" not in loads.keys() or all(loads.q_mvar.isna())
            else loads.q_mvar.apply(lambda x: float(0) if isna(x) else x)
        ),
        const_z_percent=(
            float(0)
            if "const_z_percent" not in loads.keys() or all(loads.const_z_percent.isna())
            else loads.const_z_percent.apply(lambda x: float(0) if isna(x) else x)
        ),
        const_i_percent=(
            float(0)
            if "const_i_percent" not in loads.keys() or all(loads.const_i_percent.isna())
            else loads.const_i_percent.apply(lambda x: float(0) if isna(x) else x)
        ),
        # sn_mva=nan, # TODO kann aus p und q abgeleitete werden
        name=loads["name"],
        scaling=(
            float(1)
            if "scaling" not in loads.keys() or all(loads.scaling.isna())
            else loads.scaling.apply(lambda x: float(1) if isna(x) else x)
        ),
        in_service=(
            bool(True)
            if "in_service" not in loads.keys() or all(loads.in_service.isna())
            else loads.in_service.apply(lambda x: bool(True) if isna(x) else x)
        ),
        type=(
            "wye"
            if "type" not in loads.keys() or all(loads.type.isna())
            else loads.type.apply(lambda x: "wye" if isna(x) else x)
        ),
    )


def create_pp_ext_grid(net, grid_data):
    if "ehv" in grid_data.target_input.power_levels[0] and not grid_data.ehv_data.ehv_nodes.empty:
        # check if their are convolutional power plants in the grid area
        if not net.gen.empty:
            # set gens with max p_mw as slack bus
            net.gen.at[net.gen[net.gen.p_mw == net.gen.p_mw.max()].index[0], "slack"] = True
        # in case there is no convolutional power plant
        else:
            # create a ext grid on the first ehv grid bus
            ext_id = create_ext_grid(
                net, bus=grid_data.ehv_data.ehv_nodes.iloc[0].name, name="ext_grid_1_0"
            )
            # additional Informations
            net.ext_grid.at[ext_id, "voltage_level"] = 1
    elif "hv" in grid_data.target_input.power_levels[0]:
        # !!! Todo: Solution for Case if there are no trafo in the data
        for i, trafo in grid_data.components_power.transformers.ehv_hv.iterrows():
            ext_id = create_ext_grid(
                net, bus=net.bus[net.bus["name"] == trafo.bus_hv].index[0], name=f"ext_grid_2_{i}"
            )
            # additional Informations
            net.ext_grid.at[ext_id, "voltage_level"] = 2
    elif "mv" in grid_data.target_input.power_levels[0]:
        for i, trafo in grid_data.components_power.transformers.hv_mv.iterrows():
            ext_id = create_ext_grid(
                net, bus=net.bus[net.bus["name"] == trafo.bus_hv].index[0], name=f"ext_grid_4_{i}"
            )
            # additional Informations
            net.ext_grid.at[ext_id, "voltage_level"] = 4
    elif "lv" in grid_data.target_input.power_levels[0]:
        for i, trafo in grid_data.components_power.transformers.mv_lv.iterrows():
            ext_id = create_ext_grid(
                net, bus=net.bus[net.bus["name"] == trafo.bus_hv].index[0], name=f"ext_grid_6_{i}"
            )
            # additional Informations
            net.ext_grid.at[ext_id, "voltage_level"] = 6


def create_pandapower(grid_data, opt_model, output_folder):
    """
    This function creates a pandapower network based an the DaVe dataset

    INPUT:
        **grid_data** (attrdict) - calculated grid data from dave \n
        **opt_model** (bool) - optimize model during model processing \n
        **output_folder** (str) - patht to the location where the results will be saved \n

    OUTPUT:
        **net** (attrdict) - pandapower attrdict with grid data \n
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create pandapower network:         ",
        position=0,
        bar_format=dave_settings["bar_format"],
    )
    # create empty network
    net = create_empty_network()
    # add dave version
    net["dave_version"] = grid_data.dave_version

    # --- create buses
    # collect bus informations and aggregate them
    all_buses = concat(
        [
            grid_data.ehv_data.ehv_nodes,
            grid_data.hv_data.hv_nodes,
            grid_data.mv_data.mv_nodes,
            grid_data.lv_data.lv_nodes,
        ]
    )
    all_buses.reset_index(drop=True, inplace=True)

    if not all_buses.empty:
        # create bus names
        create_pp_buses(net, all_buses)
    # update progress
    pbar.update(15)

    # --- create lines
    # create lines ehv + hv
    lines_ehvhv = concat([grid_data.ehv_data.ehv_lines, grid_data.hv_data.hv_lines])
    lines_ehvhv.reset_index(drop=True, inplace=True)
    if not lines_ehvhv.empty:
        create_pp_ehvhv_lines(net, lines_ehvhv)

    # create lines mv + lv
    lines_mvlv = concat([grid_data.mv_data.mv_lines, grid_data.lv_data.lv_lines])
    lines_mvlv.reset_index(drop=True, inplace=True)
    if not lines_mvlv.empty:
        create_pp_mvlv_lines(net, lines_mvlv)

    # update progress
    pbar.update(20)

    # ---create substations
    net["substations"] = DataFrame(
        concat(
            [
                grid_data.components_power.substations.ehv_hv,
                grid_data.components_power.substations.hv_mv,
                grid_data.components_power.substations.mv_lv,
            ]
        )
    )
    net.substations.reset_index(drop=True, inplace=True)
    # update progress
    pbar.update(5)

    # --- create transformers
    create_pp_trafos(net, grid_data)
    # update progress
    pbar.update(20)

    # ---create generators
    # create renewable powerplants
    if not grid_data.components_power.renewable_powerplants.empty:
        renewables = grid_data.components_power.renewable_powerplants
        renewables.reset_index(drop=True, inplace=True)
        create_pp_sgens(net, renewables)
    # update progress
    pbar.update(15)

    # create conventional powerplants
    if not grid_data.components_power.conventional_powerplants.empty:
        conventionals = grid_data.components_power.conventional_powerplants
        conventionals.reset_index(drop=True, inplace=True)
        create_pp_gens(net, conventionals)
    # update progress
    pbar.update(15)

    # --- create loads
    if not grid_data.components_power.loads.empty:
        loads = grid_data.components_power.loads.rename(
            columns={"dave_name": "name", "landuse": "type", "electrical_capacity_mw": "p_mw"}
        )
        loads.reset_index(drop=True, inplace=True)
        create_pp_loads(net, loads)
    # update progress
    pbar.update(10)

    # --- create ext_grid
    create_pp_ext_grid(net, grid_data)

    # --- add geodata as aditional informations
    net["buildings"] = concat(
        [grid_data.buildings.residential, grid_data.buildings.commercial, grid_data.buildings.other]
    )
    net["roads"] = grid_data.roads.roads
    net["railways"] = grid_data.railways
    net["waterways"] = grid_data.waterways
    net["landuse"] = grid_data.landuse

    # close progress bar
    pbar.close()
    # run pandapower model processing
    if not net.bus.empty:
        net = power_processing(net, opt_model=opt_model)
    # save pandapower model in the dave output folder
    file_path = output_folder + "\\dave_pandapower.json"
    pp_to_json(net, file_path)
    return net


def power_processing(
    net,
    opt_model=False,
    min_vm_pu=0.95,
    max_vm_pu=1.05,
    max_line_loading=100,
    max_trafo_loading=100,
):
    """
    This function run a diagnosis of the pandapower network and clean up occurring failures.
    Furthermore the grid will be adapt so all boundarys be respected.

    INPUT:
        **net** (attrdict) - pandapower attrdict \n

    OPTIONAL:
        **opt_model** (bool, default False) - If True the model will be optimized to respecting \
            defined grid limits \
        **min_vm_pu** (float, default 0.95) - minimal permissible node voltage in p.u. \n
        **max_vm_pu** (float, default 1.05) - maximum permissible node voltage in p.u. \n
        **max_line_loading** (int, default 100) - maximum permissible line loading in % \n
        **max_trafo_loading** (int, default 100) - maximum permissible transformer loading in % \n

    OUTPUT:
        **net** (attrdict) - A cleaned up and if necessary optimized pandapower attrdict
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="run pandapower model processing:   ",
        position=0,
        bar_format=dave_settings["bar_format"],
    )
    # run network diagnostic
    pp_diagnostic = diagnostic(net, report_style="None")
    # update progress
    pbar.update(15)
    # --- clean up failures detected by the diagnostic tool
    # delete disconected buses and the elements connected to them
    if "disconnected_elements" in pp_diagnostic.keys():
        for idx in range(len(pp_diagnostic["disconnected_elements"])):
            drop_buses(net, pp_diagnostic["disconnected_elements"][idx]["buses"])
            pbar.update(10 / len(pp_diagnostic["disconnected_elements"]))
        # run network diagnostic
        pp_diagnostic = diagnostic(net, report_style="None")
        # update progress
        pbar.update(15)
    else:
        # update progress
        pbar.update(25)
    # change lines with impedance close to zero to switches
    if "impedance_values_close_to_zero" in pp_diagnostic.keys():
        lines = pp_diagnostic["impedance_values_close_to_zero"][0]["line"]
        for line_index in lines:
            create_replacement_switch_for_branch(net, element_type="line", element_index=line_index)
            # update progress
            pbar.update(10 / len(lines))
        drop_lines(net, lines=lines)
        # run network diagnostic
        pp_diagnostic = diagnostic(net, report_style="None")
        # update progress
        pbar.update(15)
    else:
        # update progress
        pbar.update(25)
    # correct invalid values
    if "invalid_values" in diagnostic.keys():
        if "gen" in diagnostic["invalid_values"].keys():
            for gen in diagnostic["invalid_values"]["gen"]:
                if (gen[1] == "p_mw") and (gen[2] == "nan"):
                    net.gen.at[gen[0], "p_mw"] = 0
        if "line" in diagnostic["invalid_values"].keys():
            drop_lines_diag = []
            for line in drop_lines_diag["invalid_values"]["line"]:
                if (line[1] == "length_km") and (line[2] == 0):
                    create_replacement_switch_for_branch(
                        net, element_type="line", element_index=line[0]
                    )
                    drop_lines_diag.append(line[0])
            drop_lines(net, lines=drop_lines_diag)
        # update progress
        pbar.update(10)
        # run network diagnostic
        pp_diagnostic = diagnostic(net, report_style="None")
        # update progress
        pbar.update(15)
    else:
        # update progress
        pbar.update(25)
    # delete parallel switches
    if "parallel_switches" in pp_diagnostic.keys():
        for i in range(len(pp_diagnostic["parallel_switches"])):
            parallel_switches = pp_diagnostic["parallel_switches"][i]
            # keep the first switch and delete the other ones
            for j in range(1, len(parallel_switches)):
                net.switch = net.switch.drop([parallel_switches[j]])
            # update progress
            pbar.update(10 / len(diagnostic["parallel_switches"]))
    else:
        # update progress
        pbar.update(10)
    # close progress bar
    pbar.close()

    # --- optimize grid model
    if opt_model:
        pbar = tqdm(
            total=100,
            desc="run power grid optimization:       ",
            position=0,
            bar_format=dave_settings["bar_format"],
        )
        # run network diagnostic
        pp_diagnostic = diagnostic(net, report_style="None")
        # update progress
        pbar.update(20)
        # clean up overloads
        while "overload" in pp_diagnostic.keys():
            if (pp_diagnostic["overload"]["generation"]) and (net.sgen.scaling.min() >= 0.1):
                # scale down sgens about 10%
                net.sgen.scaling -= 0.1
                # run diagnostic after scale down for a new report
                pp_diagnostic = diagnostic(net, report_style="None")
            elif (diagnostic["overload"]["load"]) and (net.load.scaling.min() >= 0.1):
                # scale down sgens about 10%
                net.load.scaling -= 0.1
                # run diagnostic after scale down for a new report
                pp_diagnostic = diagnostic(net, report_style="None")
            else:
                break
        # update progress
        pbar.update(20)
        # check if pf converged and there are no violations, otherwise must use opf
        try:
            # run powerflow
            runpp(net, max_iteration=100)
            pf_converged = True
            # check boundarys
            if net.res_bus.vm_pu.min() < min_vm_pu:
                use_opf = True
                min_vm_pu_pf = net.res_bus.vm_pu.min()
            elif net.res_bus.vm_pu.max() > max_vm_pu:
                use_opf = True
                max_vm_pu_pf = net.res_bus.vm_pu.max()
            elif net.res_line.loading_percent.max() > max_line_loading:
                use_opf = True
                max_line_loading_pf = net.res_line.loading_percent.max()
            elif net.res_trafo.loading_percent.max() > max_trafo_loading:
                use_opf = True
                max_trafo_loading_pf = net.res_trafo.loading_percent.max()
            else:
                use_opf = False
                print("power flow converged and has no violations")
        except:
            use_opf = True
            pf_converged = False
            print("power flow did not converged")
        # update progress
        pbar.update(10)
        # optimize grid with opf
        if use_opf:
            # --- try opf to find optimized network to network constraints
            # set grid parameter boundrys
            net.bus["min_vm_pu"] = min_vm_pu
            net.bus["max_vm_pu"] = max_vm_pu
            net.line["max_loading_percent"] = max_line_loading
            net.trafo["max_loading_percent"] = max_trafo_loading
            # set flexibilities
            # for loads
            net.load["min_p_mw"] = 0
            net.load["max_p_mw"] = net.load.p_mw
            net.load["min_q_mvar"] = 0
            net.load["max_q_mvar"] = net.load.q_mvar
            net.load["controllable"] = True
            # for sgens
            net.sgen["min_p_mw"] = 0
            net.sgen["max_p_mw"] = net.sgen.p_mw
            net.sgen["min_q_mvar"] = 0
            net.sgen["max_q_mvar"] = 0
            net.sgen["controllable"] = True
            # for gens
            net.gen["min_vm_pu"] = min_vm_pu  # necessary for OPF
            net.gen["max_vm_pu"] = max_vm_pu  # necessary for OPF
            net.gen["min_p_mw"] = 0
            net.gen["max_p_mw"] = net.gen.p_mw
            # net.gen['min_q_mvar']
            # net.gen['max_q_mvar']
            net.gen["controllable"] = True
            # check if opf converged and the results are better as before
            try:
                # run optimal power flow
                runopp(net, verbose=True)
                # check results and compare with previous parameters
                if pf_converged:
                    min_bus = (net.res_bus.vm_pu.min() > min_vm_pu_pf) or (
                        net.res_bus.vm_pu.min() > min_vm_pu
                    )
                    max_bus = (net.res_bus.vm_pu.max() < max_vm_pu_pf) or (
                        net.res_bus.vm_pu.max() < max_vm_pu
                    )
                    max_line = (net.res_line.loading_percent.max() < max_line_loading_pf) or (
                        net.res_line.loading_percent.max() < max_line_loading
                    )
                    max_trafo = (net.res_trafo.loading_percent.max() < max_trafo_loading_pf) or (
                        net.res_trafo.loading_percent.max() < max_trafo_loading
                    )
                if (not pf_converged) or (min_bus and max_bus and max_line and max_trafo):
                    # save original parameters as installed power in grid model
                    net.sgen["p_mw_installed"] = net.sgen.p_mw
                    net.sgen["q_mvar_installed"] = net.sgen.q_mvar
                    net.load["p_mw_installed"] = net.load.p_mw
                    net.load["q_mvar_installed"] = net.load.q_mvar
                    net.gen["p_mw_installed"] = net.gen.p_mw
                    net.gen["sn_mva_installed"] = net.gen.sn_mva
                    net.gen["vm_pu_installed"] = net.gen.vm_pu
                    # set grid parameters to the calculated ones from the opf
                    net.sgen.p_mw = net.res_sgen.p_mw
                    net.sgen.q_mvar = net.res_sgen.q_mvar
                    net.load.p_mw = net.res_load.p_mw
                    net.load.q_mvar = net.res_load.q_mvar
                    net.gen.p_mw = net.res_gen.p_mw
                    net.gen.sn_mva = (net.res_gen.p_mw**2 + net.res_gen.q_mvar**2).pow(1 / 2)
                    net.gen.vm_pu = net.res_gen.vm_pu
            except:
                print("optimal power flow did not converged")
        # update progress
        pbar.update(50)
        # print results for boundaries parameters
        print("the optimized grid modell has the following charakteristik:")
        print(f"min_vm_pu: {net.res_bus.vm_pu.min()}")
        print(f"max_vm_pu: {net.res_bus.vm_pu.max()}")
        print(f"max_line_loading: {net.res_line.loading_percent.max()}")
        print(f"max_trafo_loading: {net.res_trafo.loading_percent.max()}")
        # close progress bar
        pbar.close()
    return net
