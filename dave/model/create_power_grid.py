import pandapower as pp

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
    
    # --- create lv components 
    # --- create busses
    vn_kv_lv = 0.4
    # lv busses for building connections
    for i, busses in grid_data.lv_data.lv_nodes.building_connections.iterrows():
        building_bus = busses['building_centroid'].coords[:][0]
        road_bus = busses['nearest_point'].coords[:][0]
        pp.create_bus(net,
                      name=f'building connection {i}',
                      vn_kv=vn_kv_lv,
                      geodata=building_bus)
        pp.create_bus(net,
                      name=f'road connection {i}',
                      vn_kv=vn_kv_lv,
                      geodata=road_bus)
    # lv busses for road junctions
    for i, junction in grid_data.roads.road_junctions.items():
        junction_point = junction.coords[:][0]
        pp.create_bus(net,
                      name=f'road junction {i}',
                      vn_kv=vn_kv_lv,
                      geodata=junction_point,
                      type='m')

    # --- create lines
    std_type = 'NAYY 4x150 SE'  # dummy value
    # lv lines for buildings
    for i, line in grid_data.lv_data.lv_lines.line_buildings.iterrows():
        line_coords = line.geometry.coords[:]
        start_bus = net.bus_geodata[net.bus_geodata.x == line_coords[0][0]].index[0]
        end_bus = net.bus_geodata[net.bus_geodata.x == line_coords[len(line_coords)-1][0]].index[0]
        pp.create_line(net,
                       name=f'line building {i}',
                       from_bus=start_bus,
                       to_bus=end_bus,
                       length_km=line.length_m/1000,
                       std_type=std_type,
                       geodata=[list(coords) for coords in line_coords])
    # lv lines to connect each other
    for i, line in grid_data.lv_data.lv_lines.line_connections.iterrows():
        line_coords = line.geometry.coords[:]
        start_bus = net.bus_geodata[net.bus_geodata.x == line_coords[0][0]].index[0]
        end_bus = net.bus_geodata[net.bus_geodata.x == line_coords[len(line_coords)-1][0]].index[0]
        pp.create_line(net,
                       name=f'line connection {i}',
                       from_bus=start_bus,
                       to_bus=end_bus,
                       length_km=line.length_m/1000,
                       std_type=std_type,
                       geodata=[list(coords) for coords in line_coords])
    
    
    # create transformers
    
    # create loads
    
    # ---create generators
    
    
    
    # save in any path
    return net