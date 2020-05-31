import geopandas as gpd
import math

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
    hv_buses = hv_buses.drop(columns=(['current_type', 'v_mag_pu_min', 'v_mag_pu_max', 'geom']))
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
                                            's_nom': 's_nom_mva',
                                            'r': 'r_ohm',
                                            'x': 'x_ohm',
                                            'g': 'g_s',
                                            'b': 'b_s'})
        # filter lines which are on the hv level by check if both endpoints are on the hv level
        hv_bus_ids = hv_buses.ego_bus_id.tolist()
        hv_lines = hv_lines[(hv_lines.bus0.isin(hv_bus_ids)) & 
                            (hv_lines.bus1.isin(hv_bus_ids)) & 
                            (hv_lines.ego_scn_name == 'Status Quo')]
        # --- add additional line parameter and change bus names
        r_column_index = hv_lines.columns.get_loc('r_ohm')
        hv_lines.insert(r_column_index+1, 'r_ohm_per_km', None)
        x_column_index = hv_lines.columns.get_loc('x_ohm')
        hv_lines.insert(x_column_index+1, 'x_ohm_per_km', None)
        b_column_index = hv_lines.columns.get_loc('b_s')
        hv_lines.insert(b_column_index+1, 'c_nf_per_km', None)
        hv_lines.insert(b_column_index+1, 'c_nf', None)
        # add voltage
        hv_lines['voltage_kv'] = 110
        bus0_new = []
        bus1_new = []
        for i, line in hv_lines.iterrows():
            # calculate and add r,x,c per km
            hv_lines.at[line.name, 'r_ohm_per_km'] = float(line.r_ohm)/line.length_km
            hv_lines.at[line.name, 'x_ohm_per_km'] = float(line.x_ohm)/line.length_km
            c_nf = float(line.b_s)/(2*math.pi*float(line.frequency))*1E09
            hv_lines.at[line.name, 'c_nf'] = c_nf
            hv_lines.at[line.name, 'c_nf_per_km'] = c_nf/line.length_km
            # calculate and add max i
            hv_lines.at[line.name, 'max_i_ka'] = ((float(line.s_nom_mva)*1E06)/(line.voltage_kv*1E03))*1E-03
            # change line bus names from ego id to dave name
            bus0_dave = hv_buses[hv_buses.ego_bus_id == line.bus0].iloc[0].dave_name
            bus1_dave = hv_buses[hv_buses.ego_bus_id == line.bus1].iloc[0].dave_name
            bus0_new.append(bus0_dave)
            bus1_new.append(bus1_dave)
        hv_lines['bus0'] = bus0_new
        hv_lines['bus1'] = bus1_new
        # add oep as source
        hv_lines['source'] = 'OEP'
        # add voltage level
        hv_lines['voltage_level'] = 3
        # add dave name
        hv_lines.insert(0, 'dave_name', None)
        hv_lines = hv_lines.reset_index(drop=True)
        for i, line in hv_lines.iterrows():
            hv_lines.at[line.name, 'dave_name'] = f'line_3_{i}'
        # add hv lines to grid data
        grid_data.hv_data.hv_lines = grid_data.hv_data.hv_lines.append(hv_lines)
