import pandapower as pp
from shapely.geometry import MultiLineString
from shapely.ops import linemerge

from dave.settings import dave_settings


def create_power_grid(grid_data):
    """
    This function creates a pandapower network based an the DaVe dataset

    INPUT:
        **grid_data** (attrdict) - calculated grid data from dave

    OUTPUT:
        **net** (attrdict) - pandapower attrdict with grid data
    """
    print('create pandapower network')
    print('----------------------------------')
    # create empty network
    net = pp.create_empty_network()
    # add dave version
    net['dave_version'] = grid_data.dave_version

    # --- create extra high voltage topology
    # create buses
    if not grid_data.ehv_data.ehv_nodes.empty:
        net.bus['tso_name'] = None
        for i, bus in grid_data.ehv_data.ehv_nodes.iterrows():
            bus_id = pp.create_bus(net,
                                   name=bus.dave_name,
                                   vn_kv=bus.voltage_kv,
                                   geodata=bus.geometry.coords[:][0])
            # additional Informations
            net.bus.at[bus_id, 'ego_bus_id'] = bus.ego_bus_id
            net.bus.at[bus_id, 'ego_version'] = bus.ego_version
            if 'tso_name' in bus.index:
                net.bus.at[bus_id, 'tso_name'] = bus.tso_name
            net.bus.at[bus_id, 'voltage_level'] = bus.voltage_level
            net.bus.at[bus_id, 'source'] = bus.source
    # create lines
    if not grid_data.ehv_data.ehv_lines.empty:
        for i, line in grid_data.ehv_data.ehv_lines.iterrows():
            # get line geometry coordinates
            if isinstance(line.geometry, MultiLineString):
                merged_line = linemerge(line.geometry)
                # sometimes line merge can not merge the lines correctly
                if isinstance(merged_line, MultiLineString):
                    line_coords = []
                    for j in range(0, len(merged_line)):
                        line_coords += merged_line[j].coords[:]
                else:
                    line_coords = merged_line.coords[:]
            else:
                line_coords = line.geometry.coords[:]
            # get bus indexes for the line buses
            from_bus = pp.get_element_index(net, element='bus', name=line.bus0)
            to_bus = pp.get_element_index(net, element='bus', name=line.bus1)
            line_id = pp.create_line_from_parameters(net,
                                                     from_bus=from_bus,
                                                     to_bus=to_bus,
                                                     length_km=line.length_km,
                                                     r_ohm_per_km=line.r_ohm_per_km,
                                                     x_ohm_per_km=line.x_ohm_per_km,
                                                     c_nf_per_km=line.c_nf_per_km,
                                                     max_i_ka=line.max_i_ka,
                                                     name=line.dave_name,
                                                     type='ol',
                                                     geodata=[list(coord) for coord in line_coords],
                                                     parallel=line.parallel)
            # additional Informations
            net.line.at[line_id, 'voltage_kv'] = line.voltage_kv
            net.line.at[line_id, 'voltage_level'] = line.voltage_level
            net.line.at[line_id, 'ego_line_id'] = line.ego_line_id
            net.line.at[line_id, 'ego_version'] = line.ego_version
            net.line.at[line_id, 'source'] = line.source

    # --- create high voltage topology
    # create buses
    if not grid_data.hv_data.hv_nodes.empty:
        for i, bus in grid_data.hv_data.hv_nodes.iterrows():
            bus_id = pp.create_bus(net,
                                   name=bus.dave_name,
                                   vn_kv=bus.voltage_kv,
                                   geodata=bus.geometry.coords[:][0])
            # additional Informations
            net.bus.at[bus_id, 'voltage_level'] = bus.voltage_level
            net.bus.at[bus_id, 'ego_bus_id'] = bus.ego_bus_id
            net.bus.at[bus_id, 'ego_version'] = bus.ego_version
            net.bus.at[bus_id, 'source'] = bus.source
    # create lines
    if not grid_data.hv_data.hv_lines.empty:
        for i, line in grid_data.hv_data.hv_lines.iterrows():
            # get line geometry coordinates
            if isinstance(line.geometry, MultiLineString):
                merged_line = linemerge(line.geometry)
                # sometimes line merge can not merge the lines correctly
                if isinstance(merged_line, MultiLineString):
                    line_coords = []
                    for j in range(0, len(merged_line)):
                        line_coords += merged_line[j].coords[:]
                else:
                    line_coords = merged_line.coords[:]
            else:
                line_coords = line.geometry.coords[:]
            # get bus indexes for lines
            from_bus = pp.get_element_index(net, element='bus', name=line.bus0)
            to_bus = pp.get_element_index(net, element='bus', name=line.bus1)
            line_id = pp.create_line_from_parameters(net,
                                                     from_bus=from_bus,
                                                     to_bus=to_bus,
                                                     length_km=line.length_km,
                                                     r_ohm_per_km=line.r_ohm_per_km,
                                                     x_ohm_per_km=line.x_ohm_per_km,
                                                     c_nf_per_km=line.c_nf_per_km,
                                                     max_i_ka=line.max_i_ka,
                                                     name=line.dave_name,
                                                     type='ol',
                                                     geodata=[list(coord) for coord in line_coords],
                                                     parallel=line.parallel)
            # additional Informations
            net.line.at[line_id, 'voltage_kv'] = line.voltage_kv
            net.line.at[line_id, 'voltage_level'] = line.voltage_level
            net.line.at[line_id, 'ego_line_id'] = line.ego_line_id
            net.line.at[line_id, 'ego_version'] = line.ego_version
            net.line.at[line_id, 'source'] = line.source

    # --- create medium voltage topology
    # create buses
    if not grid_data.mv_data.mv_nodes.empty:
        for i, bus in grid_data.mv_data.mv_nodes.iterrows():
            bus_id = pp.create_bus(net,
                                   name=bus.dave_name,
                                   vn_kv=bus.voltage_kv,
                                   geodata=bus.geometry.coords[:][0])
            # additional Informations
            if 'node_type' in bus.keys():
                net.bus.at[bus_id, 'node_type'] = bus.node_type
            net.bus.at[bus_id, 'voltage_level'] = bus.voltage_level
            if 'ego_version' in bus.keys():
                net.bus.at[bus_id, 'ego_version'] = bus.ego_version
            if 'ego_subst_id' in bus.keys():
                net.bus.at[bus_id, 'ego_subst_id'] = bus.ego_subst_id
            net.bus.at[bus_id, 'source'] = bus.source
    # create lines
    if not grid_data.mv_data.mv_lines.empty:
        for i, line in grid_data.mv_data.mv_lines.iterrows():
            line_coords = line.geometry.coords[:]
            line_id = pp.create_line(
                net,
                name=line.dave_name,
                from_bus=pp.get_element_index(net, element='bus', name=line.from_bus),
                to_bus=pp.get_element_index(net, element='bus', name=line.to_bus),
                length_km=line.length_km,
                std_type=dave_settings()['mv_line_std_type'],
                geodata=[list(coords) for coords in line_coords])
            # additional Informations
            net.line.at[line_id, 'voltage_level'] = line.voltage_level
            net.line.at[line_id, 'source'] = line.source

    # --- create low voltage topology
    # create buses
    if not grid_data.lv_data.lv_nodes.empty:
        for i, bus in grid_data.lv_data.lv_nodes.iterrows():
            bus_geoedata = bus.geometry.coords[:][0]
            bus_id = pp.create_bus(net,
                                   name=bus.dave_name,
                                   vn_kv=bus.voltage_kv,
                                   geodata=bus_geoedata)
            # additional Informations
            net.bus.at[bus_id, 'node_type'] = bus.node_type
            net.bus.at[bus_id, 'voltage_level'] = bus.voltage_level
            net.bus.at[bus_id, 'source'] = bus.source
    # create lines
    if not grid_data.lv_data.lv_lines.empty:
        for i, line in grid_data.lv_data.lv_lines.iterrows():
            line_coords = line.geometry.coords[:]
            line_id = pp.create_line(
                net,
                name=line.dave_name,
                from_bus=pp.get_element_index(net, element='bus', name=line.from_bus),
                to_bus=pp.get_element_index(net, element='bus', name=line.to_bus),
                length_km=line.length_km,
                std_type=dave_settings()['lv_line_std_type'],
                geodata=[list(coords) for coords in line_coords])
            # additional Informations
            net.line.at[line_id, 'voltage_level'] = line.voltage_level
            net.line.at[line_id, 'line_type'] = line.line_type
            net.line.at[line_id, 'source'] = line.source

    # --- create transformers
    # create ehv/ehv transformers
    net.trafo['geometry'] = None
    net.trafo['tso_name'] = None
    if not grid_data.components_power.transformers.ehv_ehv.empty:
        for i, trafo in grid_data.components_power.transformers.ehv_ehv.iterrows():
            hv_bus = net.bus[net.bus['name'] == trafo.bus_hv].index[0]
            lv_bus = net.bus[net.bus['name'] == trafo.bus_lv].index[0]

            # trafo über parameter. Dafür müssen die Parameter noch berechnet werden
            # aber wie? wenn ich nur r,x,b, gegeben habe
            trafo_id = pp.create_transformer_from_parameters(
                net,
                hv_bus=hv_bus,
                lv_bus=lv_bus,
                sn_mva=trafo.s_nom_mva,
                vn_hv_kv=trafo.voltage_kv_hv,
                vn_lv_kv=trafo.voltage_kv_lv,
                vkr_percent=dave_settings()['trafo_vkr_percent'],  # dummy value
                vk_percent=dave_settings()['trafo_vk_percent'],  # dummy value
                pfe_kw=dave_settings()['trafo_pfe_kw'],  # dummy value accepted as ideal
                i0_percent=dave_settings()['trafo_i0_percent'],  # dummy value accepted as ideal
                shift_degree=trafo.phase_shift,
                name=trafo.dave_name)
            # additional Informations
            net.trafo.at[trafo_id, 'geometry'] = trafo.geometry
            net.trafo.at[trafo_id, 'voltage_level'] = trafo.voltage_level
            net.trafo.at[trafo_id, 'ego_trafo_id'] = trafo.ego_trafo_id
            net.trafo.at[trafo_id, 'ego_version'] = trafo.ego_version
            net.trafo.at[trafo_id, 'substation_name'] = trafo.substation_name
            net.trafo.at[trafo_id, 'tso_name'] = trafo.tso_name
    # create ehv/hv transformers
    if not grid_data.components_power.transformers.ehv_hv.empty:
        for i, trafo in grid_data.components_power.transformers.ehv_hv.iterrows():
            hv_bus = net.bus[net.bus['name'] == trafo.bus_hv].index[0]
            lv_bus = net.bus[net.bus['name'] == trafo.bus_lv].index[0]

            # trafo über parameter. Dafür müssen die Parameter noch berechnet werden
            # aber wie? wenn ich nur r,x,b, gegeben habe
            trafo_id = pp.create_transformer_from_parameters(
                net,
                hv_bus=hv_bus,
                lv_bus=lv_bus,
                sn_mva=trafo.s_nom_mva,
                vn_hv_kv=trafo.voltage_kv_hv,
                vn_lv_kv=trafo.voltage_kv_lv,
                vkr_percent=dave_settings()['trafo_vkr_percent'],  # dummy value
                vk_percent=dave_settings()['trafo_vk_percent'],  # dummy value
                pfe_kw=dave_settings()['trafo_pfe_kw'],  # dummy value accepted as ideal
                i0_percent=dave_settings()['trafo_i0_percent'],  # dummy value accepted as ideal
                shift_degree=trafo.phase_shift,
                name=trafo.dave_name)
            # additional Informations
            net.trafo.at[trafo_id, 'geometry'] = trafo.geometry
            net.trafo.at[trafo_id, 'voltage_level'] = trafo.voltage_level
            net.trafo.at[trafo_id, 'ego_trafo_id'] = trafo.ego_trafo_id
            net.trafo.at[trafo_id, 'ego_version'] = trafo.ego_version
            if 'substation_name' in trafo.index:
                net.trafo.at[trafo_id, 'substation_name'] = trafo.substation_name
            net.trafo.at[trafo_id, 'tso_name'] = trafo.tso_name
    # create hv/mv transformers
    if not grid_data.components_power.transformers.hv_mv.empty:
        for i, trafo in grid_data.components_power.transformers.hv_mv.iterrows():
            hv_bus = net.bus[net.bus['name'] == trafo.bus_hv].index[0]
            lv_bus = net.bus[net.bus['name'] == trafo.bus_lv].index[0]
            trafo_id = pp.create_transformer(net,
                                             hv_bus=hv_bus,
                                             lv_bus=lv_bus,
                                             std_type=dave_settings()['hvmv_trafo_std_type'],
                                             name=trafo.dave_name)
            # additional Informations
            net.trafo.at[trafo_id, 'geometry'] = trafo.geometry
            net.trafo.at[trafo_id, 'voltage_level'] = trafo.voltage_level
            net.trafo.at[trafo_id, 'ego_subst_id'] = trafo.ego_subst_id
            net.trafo.at[trafo_id, 'ego_version'] = trafo.ego_version
            net.trafo.at[trafo_id, 'substation_name'] = trafo.substation_name

    # create mv/lv transformers
    if not grid_data.components_power.transformers.mv_lv.empty:
        for i, trafo in grid_data.components_power.transformers.mv_lv.iterrows():
            hv_bus = net.bus[net.bus['name'] == trafo.bus_hv].index[0]
            lv_bus = net.bus[net.bus['name'] == trafo.bus_lv].index[0]
            trafo_id = pp.create_transformer(net,
                                             hv_bus=hv_bus,
                                             lv_bus=lv_bus,
                                             std_type=dave_settings()['mvlv_trafo_std_type'],
                                             name=trafo.dave_name)
            # additional Informations
            net.trafo.at[trafo_id, 'geometry'] = trafo.geometry
            net.trafo.at[trafo_id, 'voltage_level'] = trafo.voltage_level
            if 'ego_subst_id' in bus.keys():
                net.trafo.at[trafo_id, 'ego_subst_id'] = trafo.ego_subst_id
            if 'ego_version' in bus.keys():
                net.trafo.at[trafo_id, 'ego_version'] = trafo.ego_version

    # ---create generators
    # create renewable powerplants
    net.sgen['geometry'] = None
    net.sgen['source'] = None
    if not grid_data.components_power.renewable_powerplants.empty:
        for i, plant in grid_data.components_power.renewable_powerplants.iterrows():
            sgen_bus = net.bus[net.bus['name'] == plant.bus].index[0]
            sgen_id = pp.create_sgen(net,
                                     bus=sgen_bus,
                                     p_mw=float(plant.electrical_capacity_kw)/1000,
                                     name=plant.dave_name,
                                     type=plant.generation_type)
            # additional Informations
            net.sgen.at[sgen_id, 'geometry'] = plant.geometry
            if 'aggregated' in plant.keys():
                net.sgen.at[sgen_id, 'aggregated'] = plant.aggregated
            net.sgen.at[sgen_id, 'voltage_level'] = plant.voltage_level
            if 'source' in plant.keys():
                net.sgen.at[sgen_id, 'source'] = plant.source
    # create conventional powerplants
    net.gen['geometry'] = None
    if not grid_data.components_power.conventional_powerplants.empty:
        for i, plant in grid_data.components_power.conventional_powerplants.iterrows():
            gen_bus = net.bus[net.bus['name'] == plant.bus].index[0]
            gen_id = pp.create_gen(net,
                                   bus=gen_bus,
                                   p_mw=float(plant.electrical_capacity_mw),
                                   name=plant.dave_name,
                                   type=plant.fuel)
            # additional Informations
            net.gen.at[gen_id, 'geometry'] = plant.geometry
            if 'aggregated' in plant.keys():
                net.gen.at[gen_id, 'aggregated'] = plant.aggregated
            net.gen.at[gen_id, 'voltage_level'] = plant.voltage_level
            if 'source' in plant.keys():
                net.gen.at[gen_id, 'source'] = plant.source

    # --- create loads
    if not grid_data.components_power.loads.empty:
        for i, load in grid_data.components_power.loads.iterrows():
            load_bus = net.bus[net.bus['name'] == load.bus].index[0]
            load_id = pp.create_load(net,
                                     bus=load_bus,
                                     p_mw=load.p_mw,
                                     q_mvar=load.q_mvar,
                                     name=load.dave_name,
                                     type=load.landuse)
            # additional Informations
            if 'area_km2' in load.keys():
                net.load.at[load_id, 'area_km2'] = load.area_km2
            net.load.at[load_id, 'voltage_level'] = load.voltage_level

    # --- create ext_grid
    if 'EHV' in grid_data.target_input.power_levels[0]:
        # check if their are convolutional power plants in the grid area
        if not net.gen.empty:
            plant_max = net.gen[net.gen.p_mw == net.gen.p_mw.max()]
            # set gens as slack bus
            for i, plant in plant_max.iterrows():
                net.gen.at[plant.name, 'slack'] = True
        # in case there is no convolutional power plant
        else:
            # create a ext grid on the first grid bus
            first_bus = grid_data.ehv_data.ehv_nodes.iloc[0].name
            ext_id = pp.create_ext_grid(net,
                                        bus=first_bus,
                                        name='ext_grid_1_0')
            # additional Informations
            net.ext_grid.at[ext_id, 'voltage_level'] = 1
    elif 'HV' in grid_data.target_input.power_levels[0]:
        for i, trafo in grid_data.components_power.transformers.ehv_hv.iterrows():
            ext_bus = net.bus[net.bus['name'] == trafo.bus_hv].index[0]
            ext_id = pp.create_ext_grid(net,
                                        bus=ext_bus,
                                        name=f'ext_grid_2_{i}')
            # additional Informations
            net.ext_grid.at[ext_id, 'voltage_level'] = 2
    elif 'MV' in grid_data.target_input.power_levels[0]:
        for i, trafo in grid_data.components_power.transformers.hv_mv.iterrows():
            ext_bus = net.bus[net.bus['name'] == trafo.bus_hv].index[0]
            ext_id = pp.create_ext_grid(net,
                                        bus=ext_bus,
                                        name=f'ext_grid_4_{i}')
            # additional Informations
            net.ext_grid.at[ext_id, 'voltage_level'] = 4
    elif 'LV' in grid_data.target_input.power_levels[0]:
        for i, trafo in grid_data.components_power.transformers.mv_lv.iterrows():
            ext_bus = net.bus[net.bus['name'] == trafo.bus_hv].index[0]
            ext_id = pp.create_ext_grid(net,
                                        bus=ext_bus,
                                        name=f'ext_grid_6_{i}')
            # additional Informations
            net.ext_grid.at[ext_id, 'voltage_level'] = 6
    return net
