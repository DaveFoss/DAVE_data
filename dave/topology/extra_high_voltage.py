import geopandas as gpd
from shapely.geometry import LineString

from dave.datapool import read_ehv_data
from dave.datapool import oep_request


def old(grid_data):
    """
    Dies hier ist der erste Entwurf von create_ehv_topology(grid_data).
    NUr als Backup gedacht und kann nach erfolgreicher umstellung gelöscht werden
    """

    # print to inform user
    print('create extra high voltage network for target area')
    print('-------------------------------------------------')
    # read ehv tso data
    ehv_data = read_ehv_data()
    # ---ehv nodes
    # search for ehv nodes in the target area
    ehv_nodes = gpd.overlay(ehv_data['ehv_nodes'],
                            grid_data.area,
                            how='intersection')
    # consider data only if there are more than one node in the target area
    if len(ehv_nodes) > 1:
        ehv_nodes = ehv_nodes.rename(columns={'name_1': 'name'})
        ehv_nodes = ehv_nodes.sort_values(by=['name']).reset_index()
        ehv_nodes = ehv_nodes.filter(['name', 'name_osm', 'typ', 'voltage_kv', 
                                      'tso', 'osm_id', 'substation_typ', 
                                      'substation_geometry', 'substation_voltage', 
                                      'geometry'])
        grid_data.ehv_data.ehv_nodes = ehv_nodes
        # --- ehv lines
        # search for lines in the target area
        ehv_node_names = ehv_nodes.name.tolist()
        for i, line in ehv_data['ehv_lines'].iterrows():
            # check if both end nodes from the line are inside the target area
            geometry = []
            if line['from_bus_voltage'] in ehv_node_names and line['to_bus_voltage'] in ehv_node_names:
                from_bus_geo = ehv_data['ehv_nodes'][ehv_data['ehv_nodes']['name'] == line.from_bus_voltage].iloc[0].geometry
                to_bus_geo = ehv_data['ehv_nodes'][ehv_data['ehv_nodes']['name'] == line.to_bus_voltage].iloc[0].geometry
                # create LineString for the ehv line by cosnsidering the OSM line course
                
                #An der Stelle muss der LineString noch angepasst werden, damit die LEitungsverläufe von OSM berüksichtigt werden
                #grid_data.ehv_data.ehv_lines.append(pd.DataFrame(geometry = LineString(from_bus_geo.coords[:] + to_bus_geo.coords[:]))
                # write into ehv dataset
                geometry=LineString(from_bus_geo.coords[:] + to_bus_geo.coords[:])
                ehv_line = gpd.GeoDataFrame({'from_bus':line.from_bus_voltage,
                                             'to_bus': line.to_bus_voltage,
                                             'vn_kv': line.vn_kv,
                                             'length_km': line.length_km,
                                             'max_i_ka': line.max_i_ka,
                                             'r_ohm_per_km': line.r_ohm_per_km,
                                             'x_ohm_per_km': line.x_ohm_per_km,
                                             'c_nf_per_km': line.c_nf_per_km,
                                             'geometry': [geometry]})
                grid_data.ehv_data.ehv_lines = grid_data.ehv_data.ehv_lines.append(ehv_line)
    


   
def create_ehv_topology(grid_data):
    """
    This function creates a dictonary with all relevant parameters for the
    extra high voltage level

    INPUT:
        **grid_data** (dict) - all Informations about the target area

    OPTIONAL:

    OUTPUT:

    EXAMPLE:
    """
    # print to inform user
    print('create extra high voltage topology for target area')
    print('-------------------------------------------------')
    # --- create ehv substations
    # read ehv substation data from OpenEnergyPlatform and adapt names
    ehv_substations = oep_request(schema='grid', 
                                  table='ego_dp_ehv_substation', 
                                  where='version=v0.4.5',
                                  geometry='polygon')
    ehv_substations = ehv_substations.rename(columns={'version': 'ego_version', 
                                                      'subst_id': 'ego_subst_id',
                                                      'voltage': 'voltage_kv'})
    ehv_substations = gpd.overlay(ehv_substations, grid_data.area, how='intersection')
    # consider data only if there are more than one node in the target area
    if len(ehv_substations) > 1:
        ehv_substations['voltage_level'] = 1
        # add dave name
        ehv_substations.insert(0, 'dave_name', None)
        ehv_substations = ehv_substations.reset_index(drop=True)
        for i, sub in ehv_substations.iterrows():
            ehv_substations.at[sub.name, 'dave_name'] = f'substation_1_{i}'
        # add ehv substations to grid data
        grid_data.ehv_data.ehv_substations = grid_data.ehv_data.ehv_substations.append(ehv_substations)
    # --- create ehv nodes
    # read ehv/hv node data from OpenEnergyPlatform and adapt names
    ehvhv_buses = oep_request(schema='grid', 
                              table='ego_pf_hv_bus', 
                              where='version=v0.4.6',
                              geometry='geom')
    ehvhv_buses = ehvhv_buses.rename(columns={'version': 'ego_version', 
                                              'scn_name': 'ego_scn_name',
                                              'bus_id': 'ego_bus_id',
                                              'v_nom': 'voltage_kv',
                                              'length': 'length_km'})
    # filter nodes which are on the ehv-level, current exsist and within the target area
    ehv_buses = ehvhv_buses[(ehvhv_buses.voltage_kv.isin([380, 220])) & 
                            (ehvhv_buses.ego_scn_name == 'Status Quo')]
    ehv_buses = gpd.overlay(ehv_buses, grid_data.area, how='intersection')
    if not ehv_buses.empty:
        remove_columns = grid_data.area.keys().tolist()
        remove_columns.remove('geometry')
        ehv_buses = ehv_buses.drop(columns=remove_columns)
    # consider data only if there are more than one node in the target area
    if len(ehv_buses) > 1:
        # search for the substations where the ehv nodes are within
        for i, bus in ehv_buses.iterrows():
            for j, sub in ehv_substations.iterrows():
                if bus.geometry.within(sub.geometry):
                    ehv_buses.at[bus.name, 'ego_subst_id'] = sub.ego_subst_id
                    ehv_buses.at[bus.name, 'subst_name'] = sub.subst_name
                    break
        # read ehv tso data
        ehv_data = read_ehv_data()
        # search for the tso ehv nodes in ego ehv nodes
        for i, node in ehv_data['ehv_nodes'].iterrows():
            if node.osm_id:
                # search for the matching ego ehv substation for the tso ehv node
                node_osm_id = 'w'+node.osm_id
                substation = ehv_substations[ehv_substations.osm_id == node_osm_id]
                if not substation.empty:
                    substation_id = ehv_substations[ehv_substations.osm_id == node_osm_id].iloc[0].ego_subst_id
                    ehv_buses_index = ehv_buses[ehv_buses.ego_subst_id == substation_id].index
                    for index in ehv_buses_index:
                        ehv_buses.at[index, 'tso_name'] = node['name'].replace('_380','').replace('_220','')
                        ehv_buses.at[index, 'tso'] = node['tso']
            else:
                # search for tso connection points in ego ehv nodes by a minimal distance
                for j, bus in ehv_buses.iterrows():
                    distance = node.geometry.distance(bus.geometry)
                    if distance < 2E-03:
                        ehv_buses.at[bus.name, 'tso_name'] = node['name']
                        ehv_buses.at[bus.name, 'tso'] = node['tso']
                        break
        ehv_buses['voltage_level'] = 1
        # add dave name
        ehv_buses.insert(0, 'dave_name', None)
        ehv_buses = ehv_buses.reset_index(drop=True)
        for i, bus in ehv_buses.iterrows():
            ehv_buses.at[bus.name, 'dave_name'] = f'node_1_{i}'
        # add ehv nodes to grid data
        grid_data.ehv_data.ehv_nodes = grid_data.ehv_data.ehv_nodes.append(ehv_buses)
        # --- create ehv lines
        ehv_lines = oep_request(schema='grid', 
                                table='ego_pf_hv_line', 
                                where='version=v0.4.6',
                                geometry='geom')
        ehv_lines = ehv_lines.rename(columns={'version': 'ego_version', 
                                              'subst_id': 'ego_subst_id',
                                              'scn_name': 'ego_scn_name',
                                              'line_id': 'ego_line_id',
                                              'length': 'length_km',
                                              's_nom': 's_nom_mva'})
        # filter lines which are on the ehv level by check if both endpoints are on the ehv level
        ehv_bus_ids = ehv_buses.ego_bus_id.tolist()
        ehv_lines = ehv_lines[(ehv_lines.bus0.isin(ehv_bus_ids)) & 
                              (ehv_lines.bus1.isin(ehv_bus_ids)) & 
                              (ehv_lines.ego_scn_name == 'Status Quo')]
        ehv_lines['voltage_level'] = 1
        # search for line voltage
        for i, line in ehv_lines.iterrows():
            ehv_bus_index = ehv_buses[ehv_buses.ego_bus_id == line.bus0].index[0]
            ehv_lines.at[line.name, 'voltage_kv'] = ehv_buses.loc[ehv_bus_index].voltage_kv
            ehv_lines.at[i, 'voltage_level'] = 1
        # add dave name
        ehv_lines.insert(0, 'dave_name', None)
        ehv_lines = ehv_lines.reset_index(drop=True)
        for i, line in ehv_lines.iterrows():
            ehv_lines.at[line.name, 'dave_name'] = f'line_1_{i}'
        # add ehv lines to grid data
        grid_data.ehv_data.ehv_lines = grid_data.ehv_data.ehv_lines.append(ehv_lines)
                   
    
        

    
    
    
    
    
    

    

