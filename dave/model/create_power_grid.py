import pandapower as pp
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
    line_coords = [line.coords[:] for line in merged_line] \
        if isinstance(merged_line, MultiLineString) else merged_line.coords[:]
    return line_coords


def create_power_grid(grid_data):
    """
    This function creates a pandapower network based an the DaVe dataset

    INPUT:
        **grid_data** (attrdict) - calculated grid data from dave

    OUTPUT:
        **net** (attrdict) - pandapower attrdict with grid data
    """
    # set progress bar
    pbar = tqdm(total=100, desc='create pandapower network:         ', position=0,
                bar_format=dave_settings()['bar_format'])
    # create empty network
    net = pp.create_empty_network()
    # add dave version
    net['dave_version'] = grid_data.dave_version

    # --- create buses
    # collect bus informations and aggregate them
    all_buses = pd.concat([grid_data.ehv_data.ehv_nodes, grid_data.hv_data.hv_nodes,
                           grid_data.mv_data.mv_nodes, grid_data.lv_data.lv_nodes])
    if not all_buses.empty:
        all_buses.rename(columns={'dave_name': 'name', 'voltage_kv': 'vn_kv'}, inplace=True)
        all_buses.reset_index(drop=True, inplace=True)
        # write buses into pandapower structure
        net.bus = net.bus.append(all_buses)
        net.bus_geodata['x'] = all_buses.geometry.apply(lambda x: x.coords[:][0][0])
        net.bus_geodata['y'] = all_buses.geometry.apply(lambda x: x.coords[:][0][1])
        # check necessary parameters and add pandapower standart if needed
        net.bus['type'] = 'b' if all(net.bus.type.isna()) else net.bus.type.apply(
            lambda x: 'b' if pd.isna(x) else x)
        net.bus['in_service'] = bool(True) if all(net.bus.in_service.isna()) else \
            net.bus.in_service.apply(lambda x: bool(True) if pd.isna(x) else x)

    # update progress
    pbar.update(15)

    # --- create lines
    # create lines ehv + hv
    lines_ehvhv = pd.concat([grid_data.ehv_data.ehv_lines, grid_data.hv_data.hv_lines])
    if not lines_ehvhv.empty:
        lines_ehvhv.rename(columns={'dave_name': 'name'}, inplace=True)
        lines_ehvhv['from_bus'] = lines_ehvhv.bus0.apply(
            lambda x: net.bus[net.bus['name'] == x].index[0])
        lines_ehvhv['to_bus'] = lines_ehvhv.bus1.apply(
            lambda x: net.bus[net.bus['name'] == x].index[0])
        lines_ehvhv['type'] = lines_ehvhv.type.apply(lambda x: 'ol' if pd.isna(x) else x)
        # geodata
        coords_ehvhv = pd.DataFrame({'coords': lines_ehvhv.geometry.apply(
            lambda x: [list(coords) for coords in
                       (multiline_coords(x) if isinstance(x, MultiLineString) else x.coords[:])])})
    else:
        coords_ehvhv = pd.DataFrame([])
    # create lines mv + lv
    lines_mvlv = pd.concat([grid_data.mv_data.mv_lines, grid_data.lv_data.lv_lines])
    if not lines_mvlv.empty:
        lines_mvlv.rename(columns={'dave_name': 'name'}, inplace=True)
        lines_mvlv['from_bus'] = lines_mvlv.from_bus.apply(
            lambda x: net.bus[net.bus['name'] == x].index[0])
        lines_mvlv['to_bus'] = lines_mvlv.to_bus.apply(
            lambda x: net.bus[net.bus['name'] == x].index[0])
        lines_mvlv['std_type'] = lines_mvlv.voltage_level.apply(lambda x: {
            5: dave_settings()['mv_line_std_type'], 7: dave_settings()['lv_line_std_type']}[x])
        # add data from standart type
        std_line = pp.available_std_types(net, element='line')
        lines_mvlv['r_ohm_per_km'] = lines_mvlv.std_type.apply(
            lambda x: std_line.loc[x].r_ohm_per_km)
        lines_mvlv['c_nf_per_km'] = lines_mvlv.std_type.apply(
            lambda x: std_line.loc[x].c_nf_per_km)
        lines_mvlv['x_ohm_per_km'] = lines_mvlv.std_type.apply(
            lambda x: std_line.loc[x].x_ohm_per_km)
        lines_mvlv['type'] = lines_mvlv.std_type.apply(
            lambda x: std_line.loc[x].type)
        lines_mvlv['r_ohm_per_km'] = lines_mvlv.std_type.apply(
            lambda x: std_line.loc[x].r_ohm_per_km)
        # geodata
        coords_mvlv = pd.DataFrame({'coords': lines_mvlv.geometry.apply(
            lambda x: [list(coords) for coords in x.coords[:]])})
    else:
        coords_mvlv = pd.DataFrame([])
    # write line data into pandapower structure
    net.line = net.line.append(pd.concat([lines_ehvhv, lines_mvlv]), ignore_index=True)
    net.line_geodata = net.line_geodata.append(pd.concat([coords_ehvhv, coords_mvlv]),
                                               ignore_index=True)
    # check necessary parameters and add pandapower standart if needed
    net.line['in_service'] = bool(True) if all(net.line.in_service.isna()) else \
        net.line.in_service.apply(lambda x: bool(True) if pd.isna(x) else x)
    net.line['df'] = float(1) if all(net.line.df.isna()) else net.line.df.apply(
        lambda x: float(1) if pd.isna(x) else x)
    net.line['parallel'] = int(1) if all(net.line.parallel.isna()) else net.line.parallel.apply(
        lambda x: int(1) if pd.isna(x) else x)
    net.line['std_type'] = None if all(net.line.std_type.isna()) else net.line.std_type.apply(
        lambda x: None if pd.isna(x) else x)
    # update progress
    pbar.update(20)

    # ---create substations
    net['substations'] = pd.concat([grid_data.components_power.substations.ehv_hv,
                                    grid_data.components_power.substations.hv_mv,
                                    grid_data.components_power.substations.mv_lv])
    # update progress
    pbar.update(5)

    # --- create transformers
    # create ehv/ehv, ehv/hv transformers
    trafos_ehvhv = pd.concat([grid_data.components_power.transformers.ehv_ehv,
                              grid_data.components_power.transformers.ehv_hv])
    if not trafos_ehvhv.empty:
        trafos_ehvhv.rename(columns={'dave_name': 'name', 's_nom_mva': 'sn_mva',
                                     'voltage_kv_hv': 'vn_hv_kv', 'voltage_kv_lv': 'vn_lv_kv',
                                     'phase_shift': 'shift_degree'}, inplace=True)
        # trafo über parameter. Dafür müssen die Parameter noch berechnet werden
        # aber wie? wenn ich nur r,x,b, gegeben habe
        trafos_ehvhv['vkr_percent'] = dave_settings()['trafo_vkr_percent']  # dummy value
        trafos_ehvhv['vk_percent'] = dave_settings()['trafo_vk_percent']  # dummy value
        trafos_ehvhv['pfe_kw'] = dave_settings()['trafo_pfe_kw']  # dummy value accepted as ideal
        trafos_ehvhv['i0_percent'] = dave_settings()['trafo_i0_percent']  # dummy value accepted as ideal
        trafos_ehvhv['tap_phase_shifter'] = False  # dummy value accepted as ideal
        trafos_ehvhv['hv_bus'] = trafos_ehvhv.bus_hv.apply(
            lambda x: net.bus[net.bus['name'] == x].index[0])
        trafos_ehvhv['lv_bus'] = trafos_ehvhv.bus_lv.apply(
            lambda x: net.bus[net.bus['name'] == x].index[0])
    # create hv/mv, mv/lv transformers
    trafos_mvlv = pd.concat([grid_data.components_power.transformers.hv_mv,
                             grid_data.components_power.transformers.mv_lv])
    if not trafos_mvlv.empty:
        trafos_mvlv.rename(columns={'dave_name': 'name'}, inplace=True)
        trafos_mvlv['hv_bus'] = trafos_mvlv.bus_hv.apply(
            lambda x: net.bus[net.bus['name'] == x].index[0])
        trafos_mvlv['lv_bus'] = trafos_mvlv.bus_lv.apply(
            lambda x: net.bus[net.bus['name'] == x].index[0])
        trafos_mvlv['std_type'] = trafos_mvlv.voltage_level.apply(lambda x: {
                4: dave_settings()['hvmv_trafo_std_type'],
                6: dave_settings()['mvlv_trafo_std_type']}[x])
        # add data from standart type
        std_trafo = pp.available_std_types(net, element='trafo')
        trafos_mvlv['i0_percent'] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].i0_percent)
        trafos_mvlv['pfe_kw'] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].pfe_kw)
        trafos_mvlv['vkr_percent'] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].vkr_percent)
        trafos_mvlv['sn_mva'] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].sn_mva)
        trafos_mvlv['vn_lv_kv'] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].vn_lv_kv)
        trafos_mvlv['vn_hv_kv'] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].vn_hv_kv)
        trafos_mvlv['vk_percent'] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].vk_percent)
        trafos_mvlv['shift_degree'] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].shift_degree)
        trafos_mvlv['vector_group'] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].vector_group)
        trafos_mvlv['tap_side'] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].tap_side)
        trafos_mvlv['tap_neutral'] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].tap_neutral)
        trafos_mvlv['tap_min'] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].tap_min)
        trafos_mvlv['tap_max'] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].tap_max)
        trafos_mvlv['tap_step_degree'] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].tap_step_degree)
        trafos_mvlv['tap_step_percent'] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].tap_step_percent)
        trafos_mvlv['tap_phase_shifter'] = trafos_mvlv.std_type.apply(
            lambda x: std_trafo.loc[x].tap_phase_shifter)
    # write trafo data into pandapower structure
    net.trafo = net.trafo.append(pd.concat([trafos_ehvhv, trafos_mvlv]), ignore_index=True)
    # check necessary parameters and add pandapower standart if needed
    net.trafo['in_service'] = bool(True) if all(net.trafo.in_service.isna()) else \
        net.trafo.in_service.apply(lambda x: bool(True) if pd.isna(x) else x)
    net.trafo['df'] = float(1) if all(net.trafo.df.isna()) else net.trafo.df.apply(
        lambda x: float(1) if pd.isna(x) else x)
    net.trafo['parallel'] = int(1) if all(net.trafo.parallel.isna()) else net.trafo.parallel.apply(
        lambda x: int(1) if pd.isna(x) else x)
    net.trafo['shift_degree'] = float(0) if all(net.trafo.shift_degree.isna()) else \
        net.trafo.shift_degree.apply(lambda x: float(0) if pd.isna(x) else x)
    net.trafo['tap_phase_shifter'] = bool(False) if all(net.trafo.tap_phase_shifter.isna()) else \
        net.trafo.tap_phase_shifter.apply(lambda x: bool(False) if pd.isna(x) else x)
    net.trafo['std_type'] = None if all(net.trafo.std_type.isna()) else net.trafo.std_type.apply(
        lambda x: None if pd.isna(x) else x)
    # update progress
    pbar.update(20)

    # ---create generators
    # create renewable powerplants
    if not grid_data.components_power.renewable_powerplants.empty:
        renewables = grid_data.components_power.renewable_powerplants.rename(
            columns={'name': 'plant_name', 'dave_name': 'name', 'generation_type': 'type'})
        renewables.reset_index(drop=True, inplace=True)
        net.sgen = net.sgen.append(renewables)
        net.sgen['bus'] = net.sgen.bus.apply(lambda x: net.bus[net.bus['name'] == x].index[0])
        net.sgen['p_mw'] = net.sgen.electrical_capacity_kw.apply(lambda x: float(x)/1000)
        net.sgen.drop(columns=['electrical_capacity_kw'], inplace=True)
        # check necessary parameters and add pandapower standart if needed
        net.sgen['in_service'] = bool(True) if all(net.sgen.in_service.isna()) else \
            net.sgen.in_service.apply(lambda x: bool(True) if pd.isna(x) else x)
        net.sgen['q_mvar'] = float(0) if all(net.sgen.q_mvar.isna()) else net.sgen.q_mvar.apply(
            lambda x: float(0) if pd.isna(x) else x)
        net.sgen['scaling'] = float(1) if all(net.sgen.scaling.isna()) else net.sgen.scaling.apply(
            lambda x: float(1) if pd.isna(x) else x)
        net.sgen['current_source'] = bool(True) if all(net.sgen.current_source.isna()) else \
            net.sgen.current_source.apply(lambda x: bool(True) if pd.isna(x) else x)
        net.sgen['type'] = 'wye' if all(net.sgen.type.isna()) else net.sgen.type.apply(
            lambda x: 'wye' if pd.isna(x) else x)
    # update progress
    pbar.update(15)
    # create conventional powerplants
    if not grid_data.components_power.conventional_powerplants.empty:
        conventionals = grid_data.components_power.conventional_powerplants.rename(
            columns={'name': 'plant_name', 'dave_name': 'name', 'fuel': 'type',
                     'electrical_capacity_mw': 'p_mw'})
        conventionals.reset_index(drop=True, inplace=True)
        net.gen = net.gen.append(conventionals)
        net.gen['bus'] = net.gen.bus.apply(lambda x: net.bus[net.bus['name'] == x].index[0])
        # check necessary parameters and add pandapower standart if needed
        net.gen['in_service'] = bool(True) if all(net.gen.in_service.isna()) else \
            net.gen.in_service.apply(lambda x: bool(True) if pd.isna(x) else x)
        net.gen['vm_pu'] = float(1) if all(net.gen.vm_pu.isna()) else net.gen.vm_pu.apply(
            lambda x: float(1) if pd.isna(x) else x)
        net.gen['scaling'] = float(1) if all(net.gen.scaling.isna()) else net.gen.scaling.apply(
            lambda x: float(1) if pd.isna(x) else x)
        net.gen['slack'] = bool(False) if all(net.gen.slack.isna()) else net.gen.slack.apply(
            lambda x: bool(False) if pd.isna(x) else x)
    # update progress
    pbar.update(15)

    # --- create loads
    if not grid_data.components_power.loads.empty:
        loads = grid_data.components_power.loads.rename(
            columns={'dave_name': 'name', 'landuse': 'type', 'electrical_capacity_mw': 'p_mw'})
        loads.reset_index(drop=True, inplace=True)
        net.load = net.load.append(loads)
        net.load['bus'] = net.load.bus.apply(lambda x: net.bus[net.bus['name'] == x].index[0])
        # check necessary parameters and add pandapower standart if needed
        net.load['in_service'] = bool(True) if all(net.load.in_service.isna()) else \
            net.load.in_service.apply(lambda x: bool(True) if pd.isna(x) else x)
        net.load['q_mvar'] = float(0) if all(net.load.q_mvar.isna()) else net.load.q_mvar.apply(
            lambda x: float(0) if pd.isna(x) else x)
        net.load['type'] = 'wye' if all(net.load.type.isna()) else net.load.type.apply(
            lambda x: 'wye' if pd.isna(x) else x)
        net.load['scaling'] = float(1) if all(net.load.scaling.isna()) else net.load.scaling.apply(
            lambda x: float(1) if pd.isna(x) else x)
        net.load['const_z_percent'] = float(0) if all(net.load.const_z_percent.isna()) else \
            net.load.const_z_percent.apply(lambda x: float(0) if pd.isna(x) else x)
        net.load['const_i_percent'] = float(0) if all(net.load.const_i_percent.isna()) else \
            net.load.const_i_percent.apply(lambda x: float(0) if pd.isna(x) else x)
    # update progress
    pbar.update(10)

    # --- create ext_grid
    if 'EHV' in grid_data.target_input.power_levels[0]:
        # check if their are convolutional power plants in the grid area
        if not net.gen.empty:
            # set gens with max p_mw as slack bus
            net.gen.at[net.gen[net.gen.p_mw == net.gen.p_mw.max()].index, 'slack'] = True
        # in case there is no convolutional power plant
        else:
            # create a ext grid on the first ehv grid bus
            ext_id = pp.create_ext_grid(net,
                                        bus=grid_data.ehv_data.ehv_nodes.iloc[0].name,
                                        name='ext_grid_1_0')
            # additional Informations
            net.ext_grid.at[ext_id, 'voltage_level'] = 1
    elif 'HV' in grid_data.target_input.power_levels[0]:
        for i, trafo in grid_data.components_power.transformers.ehv_hv.iterrows():
            ext_id = pp.create_ext_grid(net,
                                        bus=net.bus[net.bus['name'] == trafo.bus_hv].index[0],
                                        name=f'ext_grid_2_{i}')
            # additional Informations
            net.ext_grid.at[ext_id, 'voltage_level'] = 2
    elif 'MV' in grid_data.target_input.power_levels[0]:
        for i, trafo in grid_data.components_power.transformers.hv_mv.iterrows():
            ext_id = pp.create_ext_grid(net,
                                        bus=net.bus[net.bus['name'] == trafo.bus_hv].index[0],
                                        name=f'ext_grid_4_{i}')
            # additional Informations
            net.ext_grid.at[ext_id, 'voltage_level'] = 4
    elif 'LV' in grid_data.target_input.power_levels[0]:
        for i, trafo in grid_data.components_power.transformers.mv_lv.iterrows():
            ext_id = pp.create_ext_grid(net,
                                        bus=net.bus[net.bus['name'] == trafo.bus_hv].index[0],
                                        name=f'ext_grid_6_{i}')
            # additional Informations
            net.ext_grid.at[ext_id, 'voltage_level'] = 6
    # close progress bar
    pbar.close()
    return net
