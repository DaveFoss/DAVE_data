import geopandas as gpd
from shapely.geometry import LineString
import math

from dave.datapool import read_ehv_data, oep_request
from dave.settings import dave_settings


def create_ehv_topology(grid_data):
    """
    This function creates a dictonary with all relevant parameters for the
    extra high voltage level

    INPUT:
        **grid_data** (dict) - all Informations about the grid area

    OUTPUT:
        Writes data in the DaVe dataset
    """
    # print to inform user
    print('create extra high voltage topology for target area')
    print('-------------------------------------------------')
    # --- create ehv substations
    # read ehv substation data from OpenEnergyPlatform and adapt names
    ehv_substations, meta_data = oep_request(schema='grid',
                                             table='ego_dp_ehv_substation',
                                             where=dave_settings()['ehv_sub_ver'],
                                             geometry='polygon')
    # add meta data
    if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
        grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
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
    ehvhv_buses, meta_data = oep_request(schema='grid',
                                         table='ego_pf_hv_bus',
                                         where=dave_settings()['hv_buses_ver'],
                                         geometry='geom')
    # add meta data
    if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
        grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
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
                if (bus.geometry.within(sub.geometry)) or (bus.geometry.distance(sub.geometry) < 1E-05):
                    ehv_buses.at[bus.name, 'ego_subst_id'] = sub.ego_subst_id
                    ehv_buses.at[bus.name, 'subst_name'] = sub.subst_name
                    break
        # read ehv tso data
        ehv_data, meta_data = read_ehv_data()
        # add meta data
        if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
            grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        # assign tso ehv node names to the ego ehv nodes
        for i, node in ehv_data['ehv_nodes'].iterrows():
            if node.osm_id:
                # search for the matching ego ehv substation for the tso ehv node
                node_osm_id = 'w'+node.osm_id
                substation = ehv_substations[ehv_substations.osm_id == node_osm_id]
                if not substation.empty:
                    substation_id = substation.iloc[0].ego_subst_id
                    ehv_buses_index = ehv_buses[ehv_buses.ego_subst_id == substation_id].index
                    for index in ehv_buses_index:
                        ehv_buses.at[index, 'tso_name'] = node['name'].replace('_380', '').replace('_220', '')
                        ehv_buses.at[index, 'tso'] = node['tso']
            else:
                # search for tso connection points in ego ehv nodes by a minimal distance
                for j, bus in ehv_buses.iterrows():
                    distance = node.geometry.distance(bus.geometry)
                    if distance < 2E-03:
                        ehv_buses.at[bus.name, 'tso_name'] = node['name'].replace('_380', '').replace('_220', '')
                        ehv_buses.at[bus.name, 'tso'] = node['tso']
                        break
        # add oep as source
        ehv_buses['source'] = 'OEP'
        # add missing tso ehv nodes which are not in the ego node data
        ehv_buses_tso_names = ehv_buses.tso_name.to_list()
        if 'name' in grid_data.area.keys():
            area = grid_data.area.drop(columns=['name'])
        else:
            area = grid_data.area
        ehv_buses_tso = gpd.overlay(ehv_data['ehv_nodes'], area, how='intersection')
        for i, tso_bus in ehv_buses_tso.iterrows():
            if tso_bus['name'].replace('_380', '').replace('_220', '') not in ehv_buses_tso_names:
                tso_name = tso_bus['name'].replace('_380', '').replace('_220', '')
                ehv_buses = ehv_buses.append(gpd.GeoDataFrame({'voltage_kv': tso_bus.voltage_kv,
                                                               'geometry': [tso_bus.geometry],
                                                               'subst_name': tso_bus.name_osm,
                                                               'tso_name': tso_name,
                                                               'tso': tso_bus.tso,
                                                               'source': 'tso data'}))
        ehv_buses = ehv_buses.reset_index(drop=True)
        # add voltage level
        ehv_buses['voltage_level'] = 1
        # add dave name
        ehv_buses.insert(0, 'dave_name', None)
        for i, bus in ehv_buses.iterrows():
            ehv_buses.at[bus.name, 'dave_name'] = f'node_1_{i}'
        # add ehv nodes to grid data
        grid_data.ehv_data.ehv_nodes = grid_data.ehv_data.ehv_nodes.append(ehv_buses)
        # --- create ehv lines
        ehv_lines, meta_data = oep_request(schema='grid',
                                           table='ego_pf_hv_line',
                                           where=dave_settings()['hv_line_ver'],
                                           geometry='geom')
        # add meta data
        if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
            grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
        ehv_lines = ehv_lines.rename(columns={'version': 'ego_version',
                                              'subst_id': 'ego_subst_id',
                                              'scn_name': 'ego_scn_name',
                                              'line_id': 'ego_line_id',
                                              'length': 'length_km',
                                              's_nom': 's_nom_mva',
                                              'r': 'r_ohm',
                                              'x': 'x_ohm',
                                              'g': 'g_s',
                                              'b': 'b_s'})
        # filter lines which are on the ehv level by check if both endpoints are on the ehv level
        ehv_bus_ids = ehv_buses.ego_bus_id.tolist()
        ehv_lines = ehv_lines[(ehv_lines.bus0.isin(ehv_bus_ids)) &
                              (ehv_lines.bus1.isin(ehv_bus_ids)) &
                              (ehv_lines.ego_scn_name == 'Status Quo')]
        # --- add additional line parameter and change bus names
        r_column_index = ehv_lines.columns.get_loc('r_ohm')
        ehv_lines.insert(r_column_index+1, 'r_ohm_per_km', None)
        x_column_index = ehv_lines.columns.get_loc('x_ohm')
        ehv_lines.insert(x_column_index+1, 'x_ohm_per_km', None)
        b_column_index = ehv_lines.columns.get_loc('b_s')
        ehv_lines.insert(b_column_index+1, 'c_nf_per_km', None)
        ehv_lines.insert(b_column_index+1, 'c_nf', None)
        bus0_new = []
        bus1_new = []
        for i, line in ehv_lines.iterrows():
            # add voltage
            ehv_bus_index = ehv_buses[ehv_buses.ego_bus_id == line.bus0].index[0]
            ehv_lines.at[line.name, 'voltage_kv'] = ehv_buses.loc[ehv_bus_index].voltage_kv
            # change line bus names from ego id to dave name
            bus0_dave = ehv_buses[ehv_buses.ego_bus_id == line.bus0].iloc[0].dave_name
            bus1_dave = ehv_buses[ehv_buses.ego_bus_id == line.bus1].iloc[0].dave_name
            bus0_new.append(bus0_dave)
            bus1_new.append(bus1_dave)
        ehv_lines['bus0'] = bus0_new
        ehv_lines['bus1'] = bus1_new
        for i, line in ehv_lines.iterrows():
            # calculate and add r,x,c per km
            ehv_lines.at[line.name, 'r_ohm_per_km'] = float(line.r_ohm)/line.length_km
            ehv_lines.at[line.name, 'x_ohm_per_km'] = float(line.x_ohm)/line.length_km
            c_nf = float(line.b_s)/(2*math.pi*float(line.frequency))*1E09
            ehv_lines.at[line.name, 'c_nf'] = c_nf
            ehv_lines.at[line.name, 'c_nf_per_km'] = c_nf/line.length_km
            # calculate and add max i
            ehv_lines.at[line.name, 'max_i_ka'] = ((float(line.s_nom_mva)*1E06)/(line.voltage_kv*1E03))*1E-03
            # parallel lines
            ehv_lines.at[line.name, 'parallel'] = line.cables/3
        # add oep as source
        ehv_lines['source'] = 'OEP'
        # add missing tso ehv lines which are not in the ego line data
        ehv_buses_from_tso = ehv_buses[ehv_buses.source == 'tso data'].tso_name.tolist()
        for i, line in ehv_data['ehv_lines'].iterrows():
            from_bus = line.from_bus_voltage.replace('_380', '').replace('_220', '')
            to_bus = line.to_bus_voltage.replace('_380', '').replace('_220', '')
            if ((from_bus in ehv_buses_from_tso) and (to_bus in ehv_buses_tso_names)) or ((to_bus in ehv_buses_from_tso) and (from_bus in ehv_buses_tso_names)) or ((from_bus in ehv_buses_from_tso) and (to_bus in ehv_buses_from_tso)) :
                g_s = line.g_us*1E-06 if str(line.g_us) != 'nan' else line.g_us
                b_s = line.b_us*1E-06 if str(line.b_us) != 'nan' else line.b_us
                # search for the buses with the right voltage level
                from_bus = ehv_buses[ehv_buses.tso_name == from_bus]
                to_bus = ehv_buses[ehv_buses.tso_name == to_bus]
                # find the bus with the right voltage
                from_bus = from_bus[from_bus.voltage_kv == line.vn_kv]
                to_bus = to_bus[to_bus.voltage_kv == line.vn_kv]
                if (not from_bus.empty) and (not to_bus.empty):
                    geometry = LineString([from_bus.iloc[0].geometry, to_bus.iloc[0].geometry])
                    ehv_lines = ehv_lines.append(gpd.GeoDataFrame({'bus0': from_bus.iloc[0].dave_name,
                                                                   'bus1': to_bus.iloc[0].dave_name,
                                                                   'x_ohm': line.x_ohm,
                                                                   'x_ohm_per_km': line.x_ohm_per_km,
                                                                   'r_ohm': line.r_ohm,
                                                                   'r_ohm_per_km': line.r_ohm_per_km,
                                                                   'g_s': g_s,
                                                                   'b_s': b_s,
                                                                   'c_nf': line.c_uf,
                                                                   'c_nf_per_km': line.c_nf_per_km,
                                                                   'length_km': line.length_km,
                                                                   'geometry': [geometry],
                                                                   'voltage_kv': line.vn_kv,
                                                                   'max_i_ka': line.max_i_ka,
                                                                   'source': 'tso data',
                                                                   'parallel': 1}))
        # add voltage level
        ehv_lines['voltage_level'] = 1
        # add dave name
        ehv_lines.insert(0, 'dave_name', None)
        ehv_lines = ehv_lines.reset_index(drop=True)
        for i, line in ehv_lines.iterrows():
            ehv_lines.at[line.name, 'dave_name'] = f'line_1_{i}'
        # add ehv lines to grid data
        grid_data.ehv_data.ehv_lines = grid_data.ehv_data.ehv_lines.append(ehv_lines)
