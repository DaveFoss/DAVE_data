import pandapower as pp
from shapely import geometry, ops
import pandas as pd


from dave import dave_output_dir


# hier wird das Stromnetzmodell anhand der grid_data erstellt. ruaskommen soll dan fertiges pp netz als pickel(oder json?)


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
    net['dave_version'] = grid_data.dave_version

    # --- create extra high voltage topology
    # create buses
    if not grid_data.ehv_data.ehv_nodes.empty:
        net.bus['tso_name'] = None
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
            if 'tso_name' in bus.index:
                net.bus.at[bus_id, 'tso_name'] = bus.tso_name
            net.bus.at[bus_id, 'voltage_level'] = bus.voltage_level
            net.bus.at[bus_id, 'source'] = bus.source
    # create lines
    if not grid_data.ehv_data.ehv_lines.empty:
        for i, line in grid_data.ehv_data.ehv_lines.iterrows():
            # get line geometry coordinates
            if isinstance(line.geometry, geometry.multilinestring.MultiLineString):
                merged_line = ops.linemerge(line.geometry)
                # sometimes line merge can not merge the lines correctly
                if isinstance(merged_line, geometry.multilinestring.MultiLineString):
                    line_coords = []
                    for i in range(0, len(merged_line)):
                        line_coords += merged_line[i].coords[:]
                else:
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
                                           parallel=line.parallel)
            # additional Informations
            line_id = pp.get_element_index(net,
                                           element='line',
                                           name=line.dave_name)
            net.line.at[line_id, 'voltage_kv'] = line.voltage_kv
            net.line.at[line_id, 'voltage_level'] = line.voltage_level
            net.line.at[line_id, 'ego_line_id'] = line.ego_line_id
            net.line.at[line_id, 'ego_version'] = line.ego_version
            net.line.at[line_id, 'source'] = line.source

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
            net.bus.at[bus_id, 'source'] = bus.source
    # create lines
    if not grid_data.hv_data.hv_lines.empty:
        for i, line in grid_data.hv_data.hv_lines.iterrows():
            # get line geometry coordinates
            if isinstance(line.geometry, geometry.multilinestring.MultiLineString):
                merged_line = ops.linemerge(line.geometry)
                # sometimes line merge can not merge the lines correctly
                if isinstance(merged_line, geometry.multilinestring.MultiLineString):
                    line_coords = []
                    for i in range(0, len(merged_line)):
                        line_coords += merged_line[i].coords[:]
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
                                           max_i_ka=line.max_i_ka,
                                           name=line.dave_name,
                                           type='ol',
                                           geodata=[list(coords) for coords in line_coords],
                                           parallel=line.parallel)
            # additional Informations
            line_id = pp.get_element_index(net,
                                           element='line',
                                           name=line.dave_name)
            net.line.at[line_id, 'voltage_kv'] = line.voltage_kv
            net.line.at[line_id, 'voltage_level'] = line.voltage_level
            net.line.at[line_id, 'ego_line_id'] = line.ego_line_id
            net.line.at[line_id, 'ego_version'] = line.ego_version
            net.line.at[line_id, 'source'] = line.source

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
    if not grid_data.lv_data.lv_nodes.empty:
        for i, bus in grid_data.lv_data.lv_nodes.iterrows():
            bus_geoedata = bus.geometry.coords[:][0]
            pp.create_bus(net,
                          name=bus.dave_name,
                          vn_kv=bus.voltage_kv,
                          geodata=bus_geoedata)
            # additional Informations
            bus_id = pp.get_element_index(net,
                                          element='bus',
                                          name=bus.dave_name)
            net.bus.at[bus_id, 'node_type'] = bus.node_type
            net.bus.at[bus_id, 'voltage_level'] = bus.voltage_level
            net.bus.at[bus_id, 'source'] = bus.source
    # create lines
    std_type = 'NAYY 4x150 SE'  # dummy value, must be changed
    # lv lines for buildings
    if not grid_data.lv_data.lv_lines.empty:
        for i, line in grid_data.lv_data.lv_lines.iterrows():
            line_coords = line.geometry.coords[:]
            pp.create_line(net,
                           name=line.dave_name,
                           from_bus=pp.get_element_index(net, element='bus', name=line.from_bus),
                           to_bus=pp.get_element_index(net, element='bus', name=line.to_bus),
                           length_km=line.length_km,
                           std_type=std_type,
                           geodata=[list(coords) for coords in line_coords])
            # additional Informations
            line_id = pp.get_element_index(net,
                                           element='line',
                                           name=line.dave_name)
            net.line.at[line_id, 'voltage_level'] = line.voltage_level
            net.line.at[line_id, 'line_type'] = line.line_type
            net.line.at[line_id, 'source'] = line.source

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
                                                  i0_percent=0,  # dummy value accepted as ideal
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
                                                  i0_percent=0,  # dummy value accepted as ideal
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
            if 'substation_name' in trafo.index:
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
    if not grid_data.components_power.transformers.mv_lv.empty:
        std_type = '0.63 MVA 20/0.4 kV'
        for i, trafo in grid_data.components_power.transformers.mv_lv.iterrows():
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
            if 'aggregated' in plant.keys():
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
            if 'aggregated' in plant.keys():
                net.gen.at[gen_id, 'aggregated'] = plant.aggregated
            net.gen.at[gen_id, 'voltage_level'] = plant.voltage_level

    # --- create loads
    if not grid_data.components_power.loads.empty:
        for i, load in grid_data.components_power.loads.iterrows():
            load_bus = net.bus[net.bus['name'] == load.bus].index[0]
            pp.create_load(net,
                           bus=load_bus,
                           p_mw=load.p_mw,
                           q_mvar=load.q_mvar,
                           name=load.dave_name,
                           type=load.landuse)
            # additional Informations
            load_id = pp.get_element_index(net,
                                           element='load',
                                           name=load.dave_name)
            if 'area_km2' in load.keys():
                net.load.at[load_id, 'area_km2'] = load.area_km2
            net.load.at[load_id, 'voltage_level'] = load.voltage_level

    # --- create ext_grid
    # place external grid at the first bus on the highest considered voltage level
    if 'EHV' in grid_data.target_input.power_levels[0]:
        # check for convolutional power plant with uranium as energy source
        uranium_idx = net.gen[net.gen.type == 'uranium'].index
        if not uranium_idx.empty: 
            for idx in uranium_idx:
                # create ext grid
                power_plant = net.gen.loc[idx]
                pp.create_ext_grid(net,
                                   bus=power_plant.bus,
                                   vm_pu=1.0,
                                   max_p_mw=power_plant.p_mw,
                                   min_p_mw=50)            
            # del gen
            net.gen = net.gen.drop([idx])
        """
        Noch überlegen was ich mache wenn kein AKW in dem Gebiet ist
        
        # check for convolutional power plants with big capacity
        con_rel = net.gen.loc[pd.isnull(net.gen.aggregated)]
        con_100 = con_rel[con_rel['p_mw']>=100]
        for i, con in con_100.iterrows()
        
        
        # hier schauen ob ein akw im gebiet ist und dann das als ext grid nehmen
        # ansonsten das großte conventionelle nehmen
        # oder sagen das ab gewisser größe 100MW? alle Kraftwerke ein ext grid sind
        # wenn kein con power plant existiert, dann an knoten[0]
        first_bus = grid_data.ehv_data.ehv_nodes.iloc[0].dave_name
        voltage_level = 1
        """
        pass
    elif 'HV' in grid_data.target_input.power_levels[0]:
        for i, trafo in grid_data.components_power.transformers.ehv_hv.iterrows():
            ext_bus = net.bus[net.bus['name'] == trafo.bus_hv].index[0]
            dave_name = f'ext_grid_2_{i}'
            pp.create_ext_grid(net,
                               bus=ext_bus,
                               name=dave_name)
            # additional Informations
            ext_id = pp.get_element_index(net,
                                           element='ext_grid',
                                           name=dave_name)
            net.ext_grid.at[ext_id, 'voltage_level'] = 2
    elif 'MV' in grid_data.target_input.power_levels[0]:
        for i, trafo in grid_data.components_power.transformers.hv_mv.iterrows():
            ext_bus = net.bus[net.bus['name'] == trafo.bus_hv].index[0]
            dave_name = f'ext_grid_4_{i}'
            pp.create_ext_grid(net,
                               bus=ext_bus,
                               name=dave_name)
            # additional Informations
            ext_id = pp.get_element_index(net,
                                           element='ext_grid',
                                           name=dave_name)
            net.ext_grid.at[ext_id, 'voltage_level'] = 4
    elif 'LV' in grid_data.target_input.power_levels[0]:
        for i, trafo in grid_data.components_power.transformers.mv_lv.iterrows():
            ext_bus = net.bus[net.bus['name'] == trafo.bus_hv].index[0]
            dave_name = f'ext_grid_6_{i}'
            pp.create_ext_grid(net,
                               bus=ext_bus,
                               name=dave_name)
            # additional Informations
            ext_id = pp.get_element_index(net,
                                           element='ext_grid',
                                           name=dave_name)
            net.ext_grid.at[ext_id, 'voltage_level'] = 6
    
    
    
    return net