import geopandas as gpd

from dave.datapool import oep_request


def create_hv_topology(grid_data):
    """
    This function creates a dictonary with all relevant parameters for the
    high voltage level

    INPUT:
        **grid_data** (dict) - all Informations about the target area

    OPTIONAL:

    OUTPUT:

    EXAMPLE:
    """
    # print to inform user
    print('create high voltage topology for target area')
    print('--------------------------------------------')
    # --- create hv nodes
    ehvhv_buses = oep_request(schema='grid', 
                              table='ego_pf_hv_bus', 
                              where='version=v0.4.6',
                              geometry='geom')
    ehvhv_buses = ehvhv_buses.rename(columns={'version': 'ego_version', 
                                              'scn_name': 'ego_scn_name',
                                              'bus_id': 'ego_bus_id',
                                              'v_nom': 'voltage_kv'})
    # filter nodes which are on the hv level, current exsist and within the target area
    hv_buses = ehvhv_buses[(ehvhv_buses.voltage_kv == 110) & 
                           (ehvhv_buses.ego_scn_name == 'Status Quo')]
    hv_buses = gpd.overlay(hv_buses, grid_data.area, how='intersection')
    if not hv_buses.empty:
        remove_columns = grid_data.area.keys().tolist()
        remove_columns.remove('geometry')
        hv_buses = hv_buses.drop(columns=remove_columns)
    hv_buses['voltage_level'] = 3
    # consider data only if there are more than one node in the target area
    if len(hv_buses) > 1:
        # add dave name
        hv_buses.insert(0, 'dave_name', None)
        hv_buses = hv_buses.reset_index(drop=True)
        for i, bus in hv_buses.iterrows():
            hv_buses.at[bus.name, 'dave_name'] = f'node_3_{i}'
        # add hv nodes to grid data
        grid_data.hv_data.hv_nodes = grid_data.hv_data.hv_nodes.append(hv_buses)
        # --- create hv lines
        hv_lines = oep_request(schema='grid', 
                        table='ego_pf_hv_line', 
                        where='version=v0.4.6',
                        geometry='geom')
        hv_lines = hv_lines.rename(columns={'version': 'ego_version', 
                                             'subst_id': 'ego_subst_id',
                                             'scn_name': 'ego_scn_name',
                                             'line_id': 'ego_line_id',
                                             'length': 'length_km',
                                             's_nom': 's_nom_mva'})
        # filter lines which are on the hv level by check if both endpoints are on the hv level
        hv_bus_ids = hv_buses.ego_bus_id.tolist()
        hv_lines = hv_lines[(hv_lines.bus0.isin(hv_bus_ids)) & 
                            (hv_lines.bus1.isin(hv_bus_ids)) & 
                            (hv_lines.ego_scn_name == 'Status Quo')]
        hv_lines['voltage_level'] = 3
        # add dave name
        hv_lines.insert(0, 'dave_name', None)
        hv_lines = hv_lines.reset_index(drop=True)
        for i, line in hv_lines.iterrows():
            hv_lines.at[line.name, 'dave_name'] = f'line_3_{i}'
        # add hv lines to grid data
        grid_data.hv_data.hv_lines = grid_data.hv_data.hv_lines.append(hv_lines)
