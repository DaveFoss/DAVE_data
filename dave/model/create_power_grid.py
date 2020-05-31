import pandapower as pp
from shapely import geometry, ops

from dave import __version__
from dave import dave_output_dir


# hier wird das Stromnetzmodell anhand der grid_data erstellt. ruaskommen soll dan fertiges pp netz als pickel(oder json?)

# hier noch if abfragen bei den einzelnen komponenten hin zur abfrage ob empty. 

# voltage_level sollte auch in dem pandapower modell mit eingetragen werden. 


def create_power_grid(grid_data):
    """
    This function creates papandapower network.

    INPUT:
        **grid_data** (attrdict) - calculated grid data from dave

    OUTPUT:
        **net** (attrdict) - PANDAPOWER attrdict with grid data

    EXAMPLE:

    """
    print('create pandapower network for target area')
    print('-----------------------------------------')
    # create empty network
    net = pp.create_empty_network()
    # add dave version
    net['dave_version'] = __version__
    
    # --- create extra high voltage topology
    # create buses
    if not grid_data.ehv_data.ehv_nodes.empty:
        for i, bus in grid_data.ehv_data.ehv_nodes.iterrows():
            pp.create_bus(net,
                          name=bus.dave_name,
                          vn_kv=bus.voltage_kv,
                          geodata=bus.geometry.coords[:][0])
            # additional Informations
            bus_id = pp.get_element_index(net,
                                          element='bus',
                                          name=bus.dave_name)
            net.bus.at[bus_id, 'ego_bus_id'] = bus.ego_bus_id
            net.bus.at[bus_id, 'ego_version'] = bus.ego_version
            net.bus.at[bus_id, 'tso_name'] = bus.tso_name
            net.bus.at[bus_id, 'voltage_level'] = bus.voltage_level
    # create lines
    if not grid_data.ehv_data.ehv_lines.empty:
        for i, line in grid_data.ehv_data.ehv_lines.iterrows():
            # get line geometry coordinates
            if isinstance(line.geometry, geometry.multilinestring.MultiLineString):
                merged_line = ops.linemerge(line.geometry)
                line_coords = merged_line.coords[:]
            else:
                line_coords = line.geometry.coords[:]
            # get bus indexes for the line buses
            from_bus = pp.get_element_index(net, element='bus', name=line.bus0)
            to_bus = pp.get_element_index(net, element='bus', name=line.bus1)
            pp.create_line_from_parameters(net,
                                           from_bus=from_bus,
                                           to_bus=to_bus,
                                           length_km=line.length_km,
                                           r_ohm_per_km=line.r_ohm_per_km,
                                           x_ohm_per_km=line.x_ohm_per_km,
                                           c_nf_per_km=line.c_nf_per_km,
                                           max_i_ka=line.max_i_ka,
                                           name=line.dave_name,
                                           type='ol',
                                           geodata=[list(coords) for coords in line_coords],
                                           parallel=line.cables/3)
            # additional Informations
            line_id = pp.get_element_index(net,
                                           element='line',
                                           name=line.dave_name)
            net.line.at[line_id, 'voltage_kv'] = line.voltage_kv
            net.line.at[line_id, 'voltage_level'] = line.voltage_level
            net.line.at[line_id, 'ego_line_id'] = line.ego_line_id
            net.line.at[line_id, 'ego_version'] = line.ego_version

    # --- create high voltage topology
    # create buses
    if not grid_data.hv_data.hv_nodes.empty:
        for i, bus in grid_data.hv_data.hv_nodes.iterrows():
            pp.create_bus(net,
                          name=bus.dave_name,
                          vn_kv=bus.voltage_kv,
                          geodata=bus.geometry.coords[:][0])
            # additional Informations
            bus_id = pp.get_element_index(net,
                                          element='bus',
                                          name=bus.dave_name)
            net.bus.at[bus_id, 'voltage_level'] = bus.voltage_level
            net.bus.at[bus_id, 'ego_bus_id'] = bus.ego_bus_id
            net.bus.at[bus_id, 'ego_version'] = bus.ego_version
    # create lines
    if not grid_data.hv_data.hv_lines.empty:
        for i, line in grid_data.hv_data.hv_lines.iterrows():
            # get line geometry coordinates
            if isinstance(line.geometry, geometry.multilinestring.MultiLineString):
                merged_line = ops.linemerge(line.geometry)
                if isinstance(merged_line, geometry.multilinestring.MultiLineString):
                    line_coords = merged_line[0].coords[:]
                else:
                    line_coords = merged_line.coords[:]
            else:
                line_coords = line.geometry.coords[:]
            # get bus indexes for lines
            from_bus = pp.get_element_index(net, element='bus', name=line.bus0)
            to_bus = pp.get_element_index(net, element='bus', name=line.bus1)
            pp.create_line_from_parameters(net, 
                                           from_bus=from_bus,
                                           to_bus=to_bus,
                                           length_km=line.length_km,
                                           r_ohm_per_km=line.r_ohm_per_km,
                                           x_ohm_per_km=line.x_ohm_per_km,
                                           c_nf_per_km=line.c_nf_per_km,
                                           max_i_ka= line.max_i_ka,
                                           name=line.dave_name,
                                           type='ol',
                                           geodata=[list(coords) for coords in line_coords],
                                           parallel=line.cables/3)
            # additional Informations
            line_id = pp.get_element_index(net, 
                                           element='line',
                                           name=line.dave_name)
            net.line.at[line_id, 'voltage_kv'] = line.voltage_kv
            net.line.at[line_id, 'voltage_level'] = line.voltage_level
            net.line.at[line_id, 'ego_line_id'] = line.ego_line_id
            net.line.at[line_id, 'ego_version'] = line.ego_version
            
    # --- create medium voltage topology
    # create buses
    if not grid_data.mv_data.mv_nodes.empty:
        for i, bus in grid_data.mv_data.mv_nodes.iterrows():
            pp.create_bus(net,
                          name=bus.dave_name,
                          vn_kv=bus.voltage_kv,
                          geodata=bus.geometry.coords[:][0])
            # additional Informations
            bus_id = pp.get_element_index(net, 
                                          element='bus',
                                          name=bus.dave_name)
            net.bus.at[bus_id, 'voltage_level'] = bus.voltage_level
            net.bus.at[bus_id, 'ego_version'] = bus.ego_version
            
    # --- create low voltage topology
    # create buses
    vn_kv_lv = 0.4
    if not grid_data.lv_data.lv_nodes.empty:
        for i, bus in grid_data.lv_data.lv_nodes.iterrows():
            bus_geoedata = bus.geometry.coords[:][0]
            pp.create_bus(net,
                          name=bus.dave_name,
                          vn_kv=vn_kv_lv,
                          geodata=bus_geoedata)
            # additional Informations
            bus_id = pp.get_element_index(net, 
                                          element='bus',
                                          name=bus.dave_name)
            net.bus.at[bus_id, 'node_type'] = bus.node_type
            net.bus.at[bus_id, 'voltage_level'] = bus.voltage_level

    # lv buses for road junctions
    if not grid_data.roads.road_junctions.empty:
        for i, junction in grid_data.roads.road_junctions.items():
            junction_point = junction.coords[:][0]
            pp.create_bus(net,
                          name=f'road junction {i}',
                          vn_kv=vn_kv_lv,
                          geodata=junction_point,
                          type='m')
    # create lines
    std_type = 'NAYY 4x150 SE'  # dummy value, must be changed
    # lv lines for buildings
    if not grid_data.lv_data.lv_lines.empty:
        for i, line in grid_data.lv_data.lv_lines.iterrows():
            line_coords = line.geometry.coords[:]
            start_bus = net.bus_geodata[net.bus_geodata.x == line_coords[0][0]].index[0]
            end_bus = net.bus_geodata[net.bus_geodata.x == line_coords[len(line_coords)-1][0]].index[0]
            pp.create_line(net,
                           name=line.dave_name,
                           from_bus=start_bus,
                           to_bus=end_bus,
                           length_km=line.length_m/1000,
                           std_type=std_type,
                           geodata=[list(coords) for coords in line_coords])
            # additional Informations
            line_id = pp.get_element_index(net, 
                                          element='line',
                                          name=line.dave_name)
            net.line.at[line_id, 'voltage_level'] = line.voltage_level
            net.line.at[line_id, 'line_type'] = line.line_type
            
    # --- create transformers
    # create ehv/ehv transformers
    net.trafo['geometry'] = None
    if not grid_data.components_power.transformers.ehv_ehv.empty:
        for i, trafo in grid_data.components_power.transformers.ehv_ehv.iterrows():
            hv_bus = net.bus[net.bus['name'] == trafo.bus_hv].index[0]
            lv_bus = net.bus[net.bus['name'] == trafo.bus_lv].index[0]
            
            # trafo über parameter. Dafür müssen die Parameter noch berechnet werden
            # aber wie? wenn ich nur r,x,b, gegeben habe
            pp.create_transformer_from_parameters(net, 
                                                  hv_bus=hv_bus, 
                                                  lv_bus=lv_bus, 
                                                  sn_mva=trafo.s_nom_mva, 
                                                  vn_hv_kv=trafo.voltage_kv_hv, 
                                                  vn_lv_kv=trafo.voltage_kv_lv, 
                                                  vkr_percent=0,  # dummy value
                                                  vk_percent=10,  # dummy value
                                                  pfe_kw=0,  # dummy value accepted as ideal
                                                  i0_percent=0, # dummy value accepted as ideal
                                                  shift_degree=trafo.phase_shift, 
                                                  name=trafo.dave_name)
            # additional Informations
            trafo_id = pp.get_element_index(net, 
                                            element='trafo',
                                            name=trafo.dave_name)
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
            pp.create_transformer_from_parameters(net, 
                                                  hv_bus=hv_bus, 
                                                  lv_bus=lv_bus, 
                                                  sn_mva=trafo.s_nom_mva, 
                                                  vn_hv_kv=trafo.voltage_kv_hv, 
                                                  vn_lv_kv=trafo.voltage_kv_lv, 
                                                  vkr_percent=0,  # dummy value 
                                                  vk_percent=10,   # dummy value
                                                  pfe_kw=0,  # dummy value accepted as ideal
                                                  i0_percent=0, # dummy value accepted as ideal
                                                  shift_degree=trafo.phase_shift, 
                                                  name=trafo.dave_name)
            # additional Informations
            trafo_id = pp.get_element_index(net, 
                                            element='trafo',
                                            name=trafo.dave_name)
            net.trafo.at[trafo_id, 'geometry'] = trafo.geometry
            net.trafo.at[trafo_id, 'voltage_level'] = trafo.voltage_level
            net.trafo.at[trafo_id, 'ego_trafo_id'] = trafo.ego_trafo_id
            net.trafo.at[trafo_id, 'ego_version'] = trafo.ego_version
            net.trafo.at[trafo_id, 'substation_name'] = trafo.substation_name
            net.trafo.at[trafo_id, 'tso_name'] = trafo.tso_name
    # create hv/mv transformers
    if not grid_data.components_power.transformers.hv_mv.empty:
        std_type = '63 MVA 110/20 kV'
        for i, trafo in grid_data.components_power.transformers.hv_mv.iterrows():
            hv_bus = net.bus[net.bus['name'] == trafo.bus_hv].index[0]
            lv_bus = net.bus[net.bus['name'] == trafo.bus_lv].index[0]
            pp.create_transformer(net,
                                  hv_bus=hv_bus,
                                  lv_bus=lv_bus,
                                  std_type=std_type,
                                  name=trafo.dave_name)
            # additional Informations
            trafo_id = pp.get_element_index(net, 
                                            element='trafo',
                                            name=trafo.dave_name)
            net.trafo.at[trafo_id, 'geometry'] = trafo.geometry
            net.trafo.at[trafo_id, 'voltage_level'] = trafo.voltage_level
            net.trafo.at[trafo_id, 'ego_subst_id'] = trafo.ego_subst_id
            net.trafo.at[trafo_id, 'ego_version'] = trafo.ego_version
            net.trafo.at[trafo_id, 'substation_name'] = trafo.substation_name

    # create mv/lv transformers
    
    # ---create generators
    # create renewable powerplants
    net.sgen['geometry'] = None
    if not grid_data.components_power.renewable_powerplants.empty:
        for i, plant in grid_data.components_power.renewable_powerplants.iterrows():
            sgen_bus = net.bus[net.bus['name'] == plant.bus].index[0]
            pp.create_sgen(net,
                           bus=sgen_bus,
                           p_mw=float(plant.electrical_capacity_kw)/1000,
                           name=plant.dave_name,
                           type=plant.generation_type)
            # additional Informations
            sgen_id = pp.get_element_index(net, 
                                           element='sgen',
                                            name=plant.dave_name)
            net.sgen.at[sgen_id, 'geometry'] = plant.geometry
            net.sgen.at[sgen_id, 'aggregated'] = plant.aggregated
            net.sgen.at[sgen_id, 'voltage_level'] = plant.voltage_level
            net.sgen.at[sgen_id, 'source'] = plant.source
    # create conventional powerplants
    net.gen['geometry'] = None
    if not grid_data.components_power.conventional_powerplants.empty:
        for i, plant in grid_data.components_power.conventional_powerplants.iterrows():
            gen_bus = net.bus[net.bus['name'] == plant.bus].index[0]
            pp.create_gen(net,
                          bus=gen_bus,
                          p_mw=float(plant.electrical_capacity_mw),
                          name=plant.dave_name,
                          type=plant.fuel)
            # additional Informations
            gen_id = pp.get_element_index(net, 
                                          element='gen',
                                          name=plant.dave_name)
            net.gen.at[gen_id, 'geometry'] = plant.geometry
            net.gen.at[gen_id, 'aggregated'] = plant.aggregated
            net.gen.at[gen_id, 'voltage_level'] = plant.voltage_level
    
    # --- create loads
    if not grid_data.components_power.loads.empty:
        for i, load in grid_data.components_power.loads.iterrows():
            load_bus = net.bus[net.bus['name'] == load.bus].index[0]
            pp.create_load(net,
                           bus=load_bus,
                           p_mw=load.p_mw,
                           name=load.dave_name,
                           type=load.landuse)
            # additional Informations
            load_id = pp.get_element_index(net, 
                                           element='load',
                                           name=load.dave_name)
            net.load.at[load_id, 'area_km2'] = load.area_km2
            net.load.at[load_id, 'voltage_level'] = load.voltage_level

    # --- create ext_grid
    # place external grid at the first bus on the highest considered voltage level
    if 'EHV' in grid_data.target_input.power_levels[0]:
        first_bus = grid_data.ehv_data.ehv_nodes.iloc[0].dave_name
        voltage_level = 1
    elif 'HV' in grid_data.target_input.power_levels[0]:
        first_bus = grid_data.hv_data.hv_nodes.iloc[0].dave_name 
        voltage_level = 3
    elif 'MV' in grid_data.target_input.power_levels[0]:
        first_bus = grid_data.mv_data.mv_nodes.iloc[0].dave_name
        voltage_level = 5
    elif 'LV' in grid_data.target_input.power_levels[0]:
        first_bus = grid_data.lv_data.lv_nodes.iloc[0].dave_name 
        voltage_level = 7
    ext_bus = net.bus[net.bus['name'] == first_bus].index[0]
    pp.create_ext_grid(net,
                       bus=ext_bus,
                       name=f'ext_grid_{voltage_level}_0')
    
    # save grid model in the dave output folder                   
    file_path = dave_output_dir + '\\dave_power_grid.p'
    pp.to_pickle(net, file_path)
    
    return net