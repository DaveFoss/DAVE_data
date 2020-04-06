import geopandas as gpd
from geopy.geocoders import ArcGIS
from shapely.geometry import Point

from dave.datapool import oep_request


def renewable_powerplants(target_input, area=None):
    # hier muss noch eine Fallunterscheidung gemacht werden, welche Spannungsebene in den inzput daten gewählt wurden
    # Das evt mit einem Case PArameter machen der dann der Funktion übergeben wird
    # Je nach dem müssen einige Erzeuger dann aggregiert werden
    """
    This function collects the generators based on ego_renewable_powerplant from OEP 
    and assign them their exact location by adress, if these are available
    """
    print('create renewable powerplants for target area')
    print('--------------------------------------------')
    typ = target_input.typ.iloc[0]
    if typ in ['postalcode', 'federal state', 'own area']:
        for plz in target_input.data.iloc[0]:
            where = f'postcode={plz}'
            data = oep_request(schema='supply',
                               table='ego_renewable_powerplant',
                               where=where)
            if plz == target_input.data.iloc[0][0]: 
                renewables = data
            else: 
                renewables = renewables.append(data)
    elif typ == 'town name':
        for name in target_input.data.iloc[0]:
            where = f'city={name}'
            data = oep_request(schema='supply',
                               table='ego_renewable_powerplant',
                               where=where)
            if name == target_input.data.iloc[0][0]: 
                renewables = data
            else: 
                renewables = renewables.append(data)
    # prepare the DataFrame of the renewable plants
    if not renewables.empty:
        renewables = renewables.reset_index()
        renewables = renewables.drop(columns=['id',
                                              'gps_accuracy',
                                              'geom',
                                              'index'])
        renewables['lon'] = renewables['lon'].astype(float)
        renewables['lat'] = renewables['lat'].astype(float)
        renewables.rename(columns={'electrical_capacity': 'electrical_capacity_kw', 
                                   'thermal_capacity': 'thermal_capacity_kw'})
        # find exact location by adress
        geolocator = ArcGIS(timeout=10000)  # set on None when geopy 2.0 was released
        for i, plant in renewables.iterrows():
            if plant.address:
                address = str(plant.address)+' ' + str(plant.postcode)+' '+str(plant.city)
                location = geolocator.geocode(address)
                renewables.at[i,'lon'] = location.longitude
                renewables.at[i,'lat'] = location.latitude
            else: 
                pass
                # zu diesem Zeitpunkt erstmal die Geokoordinaten des Rasterpunktes 
                # behalten, falls keine Adresse bekannt. Das aber noch abändern. 
        # convert DataFrame into a GeoDataFrame
        renewables_geo = gpd.GeoDataFrame(renewables,
                                          crs = 'EPSG:4326', 
                                          geometry=gpd.points_from_xy(
                                                  renewables.lon, renewables.lat))
        # intersection of power plants with target_area when target is an own area
        if typ == 'own area':
            renewables_geo = gpd.overlay(renewables_geo, area, how='intersection')
    else:
        renewables_geo = renewables
    return renewables_geo
    
def conventional_powerplants(target_input, area=None):
    # hier muss noch eine Fallunterscheidung gemacht werden, welche Spannungsebene in den inzput daten gewählt wurden
    # Das evt mit einem Case PArameter machen der dann der Funktion übergeben wird
    # Je nach dem müssen einige Erzeuger dann aggregiert werden
    """
    This function collects the generators based on ego_conventional_powerplant from OEP
    """
    print('create conventional powerplants for target area')
    print('-----------------------------------------------')
    typ = target_input.typ.iloc[0]
    if typ in ['postalcode', 'federal state', 'own area']:
        for plz in target_input.data.iloc[0]:
            where = f'postcode={plz}'
            data = oep_request(schema='supply',
                               table='ego_conventional_powerplant',
                               where=where)
            if plz == target_input.data.iloc[0][0]: 
                conventionals = data
            else: 
                conventionals = conventionals.append(data)
    elif typ == 'town name':
        for name in target_input.data.iloc[0]:
            where = f'city={name}'
            data = oep_request(schema='supply',
                               table='ego_conventional_powerplant',
                               where=where)
            if name == target_input.data.iloc[0][0]: 
                conventionals = data
            else: 
                conventionals = conventionals.append(data)
    # prepare the DataFrame of the renewable plants
    if not conventionals.empty:
        conventionals = conventionals.reset_index()
        conventionals = conventionals.drop(columns=['gid',
                                                    'geom',
                                                    'index'])
        conventionals.rename(columns={'capacity': 'capacity_mw',
                                      'chp_capacity_uba': 'chp_capacity_uba_mw'})
        # convert DataFrame into a GeoDataFrame
        conventionals_geo = gpd.GeoDataFrame(conventionals, 
                                             crs = 'EPSG:4326',
                                             geometry=gpd.points_from_xy(
                                                     conventionals.lon, conventionals.lat))
        # intersection of power plants with target_area when target is an own area
        if typ == 'own area':
            conventionals_geo = gpd.overlay(conventionals_geo, area, how='intersection')
    else:
        conventionals_geo = conventionals
    return conventionals_geo

def transformators(grid_data):
    """
    This function collects the transformers
    EHV and HV level are based on ego_pf_hv_transformer from OEP
    """
    print('create transformers for target area')
    print('-----------------------------------')
    # --- create ehv/ehv and ehv/hv trafos
    if 'EHV' in grid_data.target_input.power_levels[0] or 'HV' in grid_data.target_input.power_levels[0]:
        # read transformator data from OEP, filter current exsist ones and rename paramter names
        hv_trafos = oep_request(schema='grid', 
                                  table='ego_pf_hv_transformer', 
                                  where='version=v0.4.6',
                                  geometry='geom')
        hv_trafos = hv_trafos.rename(columns={'version': 'ego_version', 
                                              'scn_name': 'ego_scn_name',
                                              'trafo_id': 'ego_trafo_id',
                                              's_nom': 's_nom_mva'})
        hv_trafos = hv_trafos[hv_trafos.ego_scn_name == 'Status Quo']
        # change geometry to point because in original data the geometry was lines with length 0
        for i, trafo in hv_trafos.iterrows():
            trafo_point = Point(trafo.geometry[0].coords[:][0][0], trafo.geometry[0].coords[:][0][1])
            hv_trafos.at[trafo.name, 'geometry'] = trafo_point
        # check for transformer in the target area
        
        hv_trafos = gpd.overlay(hv_trafos, grid_data.area, how='intersection')
        hv_trafos = hv_trafos.drop(columns=['name', 'length_m', 'area_km2', 'population'])
        # check if there is no ehv level or hv level. in this case the missing nodes for the transformator must be procured from OEP
        if ('EHV' in grid_data.target_input.power_levels[0] and grid_data.hv_data.hv_nodes.empty) \
           or ('HV' in grid_data.target_input.power_levels[0] and grid_data.ehv_data.ehv_nodes.empty):
            # read ehv/hv node data from OpenEnergyPlatform and adapt names
            ehvhv_buses = oep_request(schema='grid', 
                                      table='ego_pf_hv_bus', 
                                      where='version=v0.4.6',
                                      geometry='geom')
            ehvhv_buses = ehvhv_buses.rename(columns={'version': 'ego_version', 
                                                      'scn_name': 'ego_scn_name',
                                                      'bus_id': 'ego_bus_id',
                                                      'v_nom': 'voltage_kv'})
            ehvhv_buses = ehvhv_buses[ehvhv_buses.ego_scn_name == 'Status Quo']
            ehvhv_buses = gpd.overlay(ehvhv_buses, grid_data.area, how='intersection')
            ehvhv_buses = ehvhv_buses.drop(columns=['name', 'length_m', 'area_km2', 'population'])
        # search for line voltage and create missing nodes
        for i, trafo in hv_trafos.iterrows():
            if 'EHV' in grid_data.target_input.power_levels[0]:
                ehv_bus0 = grid_data.ehv_data.ehv_nodes[grid_data.ehv_data.ehv_nodes.ego_bus_id == trafo.bus0]
                ehv_bus1 = grid_data.ehv_data.ehv_nodes[grid_data.ehv_data.ehv_nodes.ego_bus_id == trafo.bus1]
                if not ehv_bus0.empty:
                    ehv_bus_index0 = ehv_bus0.index[0]
                    hv_trafos.at[trafo.name, 'voltage_kv_us'] = grid_data.ehv_data.ehv_nodes.loc[ehv_bus_index0].voltage_kv
                if not ehv_bus1.empty:
                    ehv_bus_index1 = ehv_bus1.index[0]
                    hv_trafos.at[trafo.name, 'voltage_kv_os'] = grid_data.ehv_data.ehv_nodes.loc[ehv_bus_index1].voltage_kv
                if ('HV' not in grid_data.target_input.power_levels[0]) and (ehv_bus0.empty):
                    hv_buses = ehvhv_buses[ehvhv_buses.voltage_kv.isin([110])]
                    hv_bus0 = hv_buses[hv_buses.ego_bus_id == trafo.bus0]
                    if not hv_bus0.empty:
                        hv_bus_index0 = hv_bus0.index[0]
                        hv_trafos.at[trafo.name, 'voltage_kv_us'] = hv_buses.loc[hv_bus_index0].voltage_kv
                        # check if node allready exsist, otherwise create them
                        if grid_data.hv_data.hv_nodes.empty:
                            grid_data.hv_data.hv_nodes = grid_data.hv_data.hv_nodes.append(hv_bus0)
                        else:
                            if grid_data.hv_data.hv_nodes[grid_data.hv_data.hv_nodes.ego_bus_id == trafo.bus0].empty:
                                grid_data.hv_data.hv_nodes = grid_data.hv_data.hv_nodes.append(hv_bus0)
            if 'HV' in grid_data.target_input.power_levels[0]:
                hv_bus0 = grid_data.hv_data.hv_nodes[grid_data.hv_data.hv_nodes.ego_bus_id == trafo.bus0]
                if not hv_bus0.empty:
                    hv_bus_index0 = hv_bus0.index[0]
                    hv_trafos.at[trafo.name, 'voltage_kv_us'] = grid_data.hv_data.hv_nodes.loc[hv_bus_index0].voltage_kv
                if ('EHV' not in grid_data.target_input.power_levels[0]) and (not hv_bus0.empty):
                    ehv_buses = ehvhv_buses[ehvhv_buses.voltage_kv.isin([380, 220])]
                    ehv_bus1 = ehv_buses[ehv_buses.ego_bus_id == trafo.bus1]
                    if not ehv_bus1.empty:
                        ehv_bus_index1 = ehv_bus1.index[0]
                        hv_trafos.at[trafo.name, 'voltage_kv_os'] = ehv_buses.loc[ehv_bus_index1].voltage_kv
                        # check if node allready exsist, otherwise create them
                        if grid_data.ehv_data.ehv_nodes.empty:
                            grid_data.ehv_data.ehv_nodes = grid_data.ehv_data.ehv_nodes.append(ehv_bus1)
                        else:
                            if grid_data.ehv_data.ehv_nodes[grid_data.ehv_data.ehv_nodes.ego_bus_id == trafo.bus1].empty:
                                grid_data.ehv_data.ehv_nodes = grid_data.ehv_data.ehv_nodes.append(ehv_bus1)
        # write transformator data in grid data and decied the grid level depending on voltage level
        if 'EHV' in grid_data.target_input.power_levels[0]:
            ehv_ehv_trafos = hv_trafos[hv_trafos.voltage_kv_us.isin([380, 220])]
            grid_data.components_power.transformers.ehv_ehv = grid_data.components_power.transformers.ehv_ehv.append(ehv_ehv_trafos)
        ehv_hv_trafos = hv_trafos[hv_trafos.voltage_kv_us == 110]
        grid_data.components_power.transformers.ehv_hv = grid_data.components_power.transformers.ehv_hv.append(ehv_hv_trafos)

    # --- create hv/mv trafos
    if 'HV' in grid_data.target_input.power_levels[0] or 'MV' in grid_data.target_input.power_levels[0]:
        pass
        # muss noch geschrieben werden
    
    # --- create mv/lv trafos
    if 'MV' in grid_data.target_input.power_levels[0] or 'LV' in grid_data.target_input.power_levels[0]:
        pass
        # muss noch geschrieben werden 

def loads():
    pass


def power_components(grid_data):
    """
    # add renewable powerplants
    renewable_data = renewable_powerplants(target_input = grid_data.target_input,
                                           area = grid_data.area)
    grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(renewable_data)
    # add conventional powerplants
    conventional_data = conventional_powerplants(
            target_input = grid_data.target_input, area = grid_data.area)
    grid_data.components_power.conventional_powerplants = grid_data.components_power.conventional_powerplants.append(conventional_data)
    """
    # add transformers
    transformators(grid_data)
    
    