import geopandas as gpd
import pandas as pd
from geopy.geocoders import ArcGIS
import shapely
from shapely.geometry import Point, MultiPoint, LineString
from shapely.ops import nearest_points
import numpy as np


from dave.datapool import oep_request
from dave.voronoi import voronoi

def aggregate_plants_ren(grid_data, plants_aggr, aggregate_name=None):
    """
    This function aggregates renewables power plants with the same energy source which are connected 
    to the same trafo
    
    INPUT:
        **grid_data** (dict) - all Informations about the target area
        **plants_aggr** (DataFrame) - all renewable power plants that sould be aggregate after voronoi analysis
    OPTIONAL:
        **aggregate_name** (string) - the original voltage level of the aggregated power plants 
    """
    # create list of all diffrent connection transformers
    connection_trafos = plants_aggr.connection_trafo_dave_name.tolist()
    trafo_names = []
    for tname in connection_trafos:
        if tname not in trafo_names:
            trafo_names.append(tname)
    trafo_names.sort()
    # iterate through the trafo_names to aggregate the power plants with the same energy source
    energy_sources = ['biomass', 'gas', 'geothermal', 'hydro', 'solar', 'wind']
    # concat all trafos to assigne the lv node name to the power plant
    trafos = pd.concat([grid_data.components_power.transformers.ehv_ehv,
                        grid_data.components_power.transformers.ehv_hv,
                        grid_data.components_power.transformers.hv_mv,
                        grid_data.components_power.transformers.mv_lv])
    # create aggregated power plants and assigne them to the grid data
    for trafo_name in trafo_names:
        plants_area = plants_aggr[plants_aggr.connection_trafo_dave_name == trafo_name]
        trafo_bus_lv = trafos[trafos.dave_name == trafo_name].iloc[0].bus_lv
        for esource in energy_sources:
            plant_esource = plants_area[plants_area.generation_type == esource]
            if not plant_esource.empty:
                sources = plant_esource.source.tolist()
                sources_diff = []
                for source in sources:
                    if source not in sources_diff:
                        sources_diff.append(source)
                plant_power = pd.to_numeric(plant_esource.electrical_capacity_kw, downcast='float')
                plant_df = gpd.GeoDataFrame({'aggregated': aggregate_name,  
                                             'electrical_capacity_kw': plant_power.sum(),
                                             'generation_type': esource,
                                             'voltage_level': plant_esource.voltage_level.iloc[0],
                                             'source': [sources_diff],
                                             'geometry': [plant_esource.connection_node.iloc[0]],
                                             'bus': trafo_bus_lv})
                grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(plant_df)

def aggregate_plants_con(grid_data, plants_aggr, aggregate_name=None):
    """
    This function aggregates conventionals power plants with the same energy source which are connected 
    to the same trafo
    
    INPUT:
        **grid_data** (dict) - all Informations about the target area
        **plants_aggr** (DataFrame) - all conventional power plants that sould be aggregate after voronoi analysis
    OPTIONAL:
        **aggregate_name** (string) - the original voltage level of the aggregated power plants 
    """
    # create list of all diffrent connection transformers
    connection_trafos = plants_aggr.connection_trafo_dave_name.tolist()
    trafo_names = []
    for tname in connection_trafos:
        if tname not in trafo_names:
            trafo_names.append(tname)
    trafo_names.sort()
    # iterate through the trafo_names to aggregate the power plants with the same energy source
    energy_sources = ['biomass', 'coal', 'gas', 'gas_mine', 'lignite', 'multiple_non_renewable',
                      'oil', 'other_non_renewable', 'pumped_storage', 'reservoir', 'run_of_river',
                      'uranium', 'waste']
    # concat all trafos to assigne the lv node name to the power plant
    trafos = pd.concat([grid_data.components_power.transformers.ehv_ehv,
                        grid_data.components_power.transformers.ehv_hv,
                        grid_data.components_power.transformers.hv_mv,
                        grid_data.components_power.transformers.mv_lv])
    # create aggregated power plants and assigne them to the grid data
    for trafo_name in trafo_names:
        plants_area = plants_aggr[plants_aggr.connection_trafo_dave_name == trafo_name]
        trafo_bus_lv = trafos[trafos.dave_name == trafo_name].iloc[0].bus_lv
        for esource in energy_sources:
            plant_esource = plants_area[plants_area.fuel == esource]
            if not plant_esource.empty:
                plant_power = pd.to_numeric(plant_esource.capacity_mw, downcast='float')
                plant_df = gpd.GeoDataFrame({'aggregated': aggregate_name,  
                                             'electrical_capacity_mw': plant_power.sum(),
                                             'fuel': esource,
                                             'voltage_level': plant_esource.voltage_level.iloc[0],
                                             'geometry': [plant_esource.connection_node.iloc[0]],
                                             'bus': trafo_bus_lv})
                grid_data.components_power.conventional_powerplants = grid_data.components_power.conventional_powerplants.append(plant_df)


def power_plant_lines(grid_data):
    """
    This function checks the distance between a power plant and the associated grid node.
    If the distance is greater than 50 meteres, a auxillary node for the power plant and a
    connection line to the originial node will be created.

    This function is not for aggregated power plants because these are anyway close to the
    connection point
    """
    print('create powerplant lines')
    print('-----------------------')
    # get all grid nodes
    ehv_nodes = grid_data.ehv_data.ehv_nodes
    hv_nodes = grid_data.hv_data.hv_nodes
    mv_nodes = grid_data.mv_data.mv_nodes
    lv_nodes = grid_data.lv_data.lv_nodes
    all_nodes = pd.concat([ehv_nodes, hv_nodes, mv_nodes, lv_nodes])
    all_nodes_3035 = all_nodes.to_crs(epsg=3035)  # project lines to crs with unit in meter
    # select all power plants
    renewables = grid_data.components_power.renewable_powerplants
    conventionals = grid_data.components_power.conventional_powerplants
    all_plants = pd.concat([renewables, conventionals])
    all_plants = all_plants.reset_index()
    # --- create auxillary buses and lines for the power plants
    if not all_plants.empty:
        if 'aggregated' in all_plants.keys():
            plants_rel = all_plants[all_plants.aggregated.isnull()]
        else: 
            plants_rel = all_plants
        plants_rel.crs = 'EPSG:4326'
        plants_rel_3035 = plants_rel.to_crs(epsg=3035)  # project lines to crs with unit in meter
        # considered voltage level
        considered_levels = []
        considered_levels.append(1) if ('EHV' in grid_data.target_input.power_levels[0]) else None
        considered_levels.append(3) if ('HV' in grid_data.target_input.power_levels[0]) else None
        considered_levels.append(5) if ('MV' in grid_data.target_input.power_levels[0]) else None
        considered_levels.append(7) if ('LV' in grid_data.target_input.power_levels[0]) else None
        for i, plant in plants_rel_3035.iterrows():
            plant_bus = all_nodes_3035[all_nodes_3035.dave_name == plant.bus].iloc[0]
            bus_geometry = plant_bus.geometry
            distance = plant.geometry.distance(bus_geometry)  # in meter
            if (distance > 50) and (plant_bus.voltage_level in considered_levels):
                # get plant coordinates in crs 4326
                plant_geometry = plants_rel.loc[plant.name].geometry
                # create auillary node
                if plant_bus.voltage_level == 1:  # (EHV)
                    buses = grid_data.ehv_data.ehv_nodes
                    last_bus_name = buses.iloc[len(buses)-1].dave_name
                    number = int(last_bus_name.replace('node_1_', ''))+1
                    dave_name_bus_aux = f'node_1_{number}'
                    auxillary_bus = gpd.GeoDataFrame({'dave_name': dave_name_bus_aux,
                                                      'voltage_kv': plant_bus.voltage_kv,
                                                      'geometry': [plant_geometry],
                                                      'voltage_level': plant_bus.voltage_level,
                                                      'source': 'dave internal'})
                    grid_data.ehv_data.ehv_nodes = grid_data.ehv_data.ehv_nodes.append(auxillary_bus).reset_index(drop=True)
                elif plant_bus.voltage_level == 3:  # (HV)
                    buses = grid_data.hv_data.hv_nodes
                    last_bus_name = buses.iloc[len(buses)-1].dave_name
                    number = int(last_bus_name.replace('node_3_', ''))+1
                    dave_name_bus_aux = f'node_3_{number}'
                    auxillary_bus = gpd.GeoDataFrame({'dave_name': dave_name_bus_aux,
                                                      'voltage_kv': plant_bus.voltage_kv,
                                                      'geometry': [plant_geometry],
                                                      'voltage_level': plant_bus.voltage_level,
                                                      'source': 'dave internal'})
                    grid_data.hv_data.hv_nodes = grid_data.hv_data.hv_nodes.append(auxillary_bus).reset_index(drop=True)
                elif plant_bus.voltage_level == 5:  # (MV)
                    buses = grid_data.mv_data.mv_nodes
                    last_bus_name = buses.iloc[len(buses)-1].dave_name
                    number = int(last_bus_name.replace('node_5_', ''))+1
                    dave_name_bus_aux = f'node_5_{number}'
                    auxillary_bus = gpd.GeoDataFrame({'dave_name': dave_name_bus_aux,
                                                      'voltage_kv': plant_bus.voltage_kv,
                                                      'geometry': [plant_geometry],
                                                      'voltage_level': plant_bus.voltage_level,
                                                      'source': 'dave internal'})
                    grid_data.mv_data.mv_nodes = grid_data.mv_data.mv_nodes.append(auxillary_bus).reset_index(drop=True)
                elif plant_bus.voltage_level == 7:  # (LV)
                    buses = grid_data.lv_data.lv_nodes
                    last_bus_name = buses.iloc[len(buses)-1].dave_name
                    number = int(last_bus_name.replace('node_7_', ''))+1
                    dave_name_bus_aux = f'node_7_{number}'
                    auxillary_bus = gpd.GeoDataFrame({'dave_name': dave_name_bus_aux,
                                                      'voltage_kv': plant_bus.voltage_kv,
                                                      'geometry': [plant_geometry],
                                                      'voltage_level': plant_bus.voltage_level,
                                                      'source': 'dave internal'})
                    grid_data.lv_data.lv_nodes = grid_data.lv_data.lv_nodes.append(auxillary_bus).reset_index(drop=True)
                # change bus name in power plant characteristics
                if plant.dave_name[:3] == 'con':
                    plant_index = conventionals[conventionals.dave_name == plant.dave_name].index[0]
                    grid_data.components_power.conventional_powerplants.at[plant_index, 'bus'] = dave_name_bus_aux
                elif plant.dave_name[:3] == 'ren':
                    plant_index = renewables[renewables.dave_name == plant.dave_name].index[0]
                    grid_data.components_power.renewable_powerplants.at[plant_index, 'bus'] = dave_name_bus_aux
                # create connection line
                bus_origin = all_nodes[all_nodes.dave_name == plant.bus].iloc[0]
                bus_geometry = bus_origin.geometry
                line_geometry = LineString([plant_geometry, bus_geometry])
                if plant_bus.voltage_level == 1:  # (EHV)
                    ehv_lines = grid_data.ehv_data.ehv_lines
                    last_line_name = ehv_lines.iloc[len(ehv_lines)-1].dave_name
                    number = int(last_line_name.replace('line_1_', ''))+1
                    dave_name_line_aux = f'line_1_{number}'
                    # check if there is a line neighbor
                    line_neighbor = ehv_lines[(ehv_lines.bus0 == bus_origin.dave_name) | (ehv_lines.bus1 == bus_origin.dave_name)]
                    if not line_neighbor.empty:
                        line_neighbor = line_neighbor.iloc[0]
                        auxillary_line = gpd.GeoDataFrame({'dave_name': dave_name_line_aux,
                                                           'bus0': dave_name_bus_aux,
                                                           'bus1': bus_origin.dave_name,
                                                           'x_ohm': line_neighbor.x_ohm_per_km/distance,
                                                           'x_ohm_per_km': line_neighbor.x_ohm_per_km,
                                                           'r_ohm': line_neighbor.r_ohm_per_km/distance,
                                                           'r_ohm_per_km': line_neighbor.r_ohm_per_km,
                                                           'c_nf': line_neighbor.c_nf_per_km/distance,
                                                           'c_nf_per_km': line_neighbor.c_nf_per_km,
                                                           's_nom_mva': line_neighbor.s_nom_mva,
                                                           'length_km': distance/1000,
                                                           'geometry': [line_geometry],
                                                           'voltage_kv': line_neighbor.voltage_kv,
                                                           'max_i_ka': line_neighbor.max_i_ka,
                                                           'parallel': line_neighbor.parallel,
                                                           'voltage_level': line_neighbor.voltage_level,
                                                           'source': 'dave internal'})
                    
                        grid_data.ehv_data.ehv_lines = grid_data.ehv_data.ehv_lines.append(auxillary_line).reset_index(drop=True)
                elif plant_bus.voltage_level == 3:  # (HV)
                    print('hv')
                    hv_lines = grid_data.hv_data.hv_lines
                    last_line_name = hv_lines.iloc[len(hv_lines)-1].dave_name
                    number = int(last_line_name.replace('line_3_', ''))+1
                    dave_name_line_aux = f'line_3_{number}'
                    # check if there is a line neighbor
                    line_neighbor = hv_lines[(hv_lines.bus0 == bus_origin.dave_name) | (hv_lines.bus1 == bus_origin.dave_name)]
                    if not line_neighbor.empty:
                        line_neighbor = line_neighbor.iloc[0]
                        auxillary_line = gpd.GeoDataFrame({'dave_name': dave_name_line_aux,
                                                           'bus0': dave_name_bus_aux,
                                                           'bus1': bus_origin.dave_name,
                                                           'x_ohm': line_neighbor.x_ohm_per_km/distance,
                                                           'x_ohm_per_km': line_neighbor.x_ohm_per_km,
                                                           'r_ohm': line_neighbor.r_ohm_per_km/distance,
                                                           'r_ohm_per_km': line_neighbor.r_ohm_per_km,
                                                           'c_nf': line_neighbor.c_nf_per_km/distance,
                                                           'c_nf_per_km': line_neighbor.c_nf_per_km,
                                                           's_nom_mva': line_neighbor.s_nom_mva,
                                                           'length_km': distance/1000,
                                                           'geometry': [line_geometry],
                                                           'voltage_kv': line_neighbor.voltage_kv,
                                                           'max_i_ka': line_neighbor.max_i_ka,
                                                           'parallel': line_neighbor.parallel,
                                                           'voltage_level': line_neighbor.voltage_level,
                                                           'source': 'dave internal'})
                        grid_data.hv_data.hv_lines = grid_data.hv_data.hv_lines.append(auxillary_line).reset_index(drop=True)
                elif plant_bus.voltage_level == 5:  # (MV)
                    mv_lines = grid_data.mv_data.mv_lines
                    last_line_name = mv_lines.iloc[len(mv_lines)-1].dave_name
                    number = int(last_line_name.replace('line_5_', ''))+1
                    dave_name_line_aux = f'line_5_{number}'
                    # check if there is a line neighbor
                    line_neighbor = mv_lines[(mv_lines.bus0 == bus_origin.dave_name) | (mv_lines.bus1 == bus_origin.dave_name)]
                    if not line_neighbor.empty:
                        line_neighbor = line_neighbor.iloc[0]
                        # Diese Parameter müssen evt noch angepasst werden wenn die MV Line Daten bekannt sind
                        auxillary_line = gpd.GeoDataFrame({'dave_name': dave_name_line_aux,
                                                           'bus0': dave_name_bus_aux,
                                                           'bus1': bus_origin.dave_name,
                                                           'x_ohm': line_neighbor.x_ohm_per_km/distance,
                                                           'x_ohm_per_km': line_neighbor.x_ohm_per_km,
                                                           'r_ohm': line_neighbor.r_ohm_per_km/distance,
                                                           'r_ohm_per_km': line_neighbor.r_ohm_per_km,
                                                           'c_nf': line_neighbor.c_nf_per_km/distance,
                                                           'c_nf_per_km': line_neighbor.c_nf_per_km,
                                                           's_nom_mva': line_neighbor.s_nom_mva,
                                                           'length_km': distance/1000,
                                                           'geometry': [line_geometry],
                                                           'voltage_kv': line_neighbor.voltage_kv,
                                                           'max_i_ka': line_neighbor.max_i_ka,
                                                           'parallel': line_neighbor.parallel,
                                                           'voltage_level': line_neighbor.voltage_level,
                                                           'source': 'dave internal'})
                        grid_data.mv_data.mv_lines = grid_data.mv_data.mv_lines.append(auxillary_line).reset_index(drop=True)
                elif plant_bus.voltage_level == 7:  # (LV)
                    lv_lines = grid_data.lv_data.lv_lines
                    last_line_name = lv_lines.iloc[len(lv_lines)-1].dave_name
                    number = int(last_line_name.replace('line_7_',''))+1
                    
                    
                    # line neighbor muss noch angepasst werden auf from und to bus aus lv_lines
                    line_neighbor = lv_lines[(lv_lines.bus0 == bus_origin.dave_name) | (lv_lines.bus1 == bus_origin.dave_name)].iloc[0]
                    
                    dave_name_line_aux = f'line_7_{number}'
                    # Diese Parameter müssen noch angepasst werden wenn lv neu berechnet wird
                    auxillary_line = gpd.GeoDataFrame({'dave_name': dave_name_line_aux,
                                                      'length_km': distance/1000,
                                                      'geometry': [line_geometry],
                                                      'voltage_kv': line_neighbor.voltage_kv,
                                                      'voltage_level': line_neighbor.voltage_level,
                                                      'source': 'dave internal'})
                    grid_data.lv_data.lv_lines = grid_data.lv_data.lv_lines.append(auxillary_line).reset_index(drop=True)
                

def renewable_powerplants(grid_data):
    """
    This function collects the generators based on ego_renewable_powerplant from OEP 
    and perhaps assign them their exact location by adress, if these are available. 
    Furthermore assign a grid node to the generators and aggregated them depending on the situation
    """
    print('create renewable powerplants for target area')
    print('--------------------------------------------')
    # load powerplant data in target area
    typ = grid_data.target_input.typ.iloc[0]
    if typ in ['postalcode', 'federal state', 'own area']:
        for plz in grid_data.target_input.data.iloc[0]:
            where = f'postcode={plz}'
            data = oep_request(schema='supply',
                               table='ego_renewable_powerplant',
                               where=where)
            if plz == grid_data.target_input.data.iloc[0][0]: 
                renewables = data
            else: 
                renewables = renewables.append(data)
    elif typ == 'town name':
        for name in grid_data.target_input.data.iloc[0]:
            where = f'city={name}'
            data = oep_request(schema='supply',
                               table='ego_renewable_powerplant',
                               where=where)
            if name == grid_data.target_input.data.iloc[0][0]: 
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
        renewables = renewables.rename(columns={'electrical_capacity': 'electrical_capacity_kw', 
                                                'thermal_capacity': 'thermal_capacity_kw'})
        # change voltage level to numbers
        for i, plant in renewables.iterrows():
            if plant.voltage_level:
                renewables.at[i, 'voltage_level'] = int(plant.voltage_level[1:2])
            else:
                # This is for plants which have a nan value at the voltage level parameter
                if float(plant.electrical_capacity_kw) <= 50:
                    renewables.at[i, 'voltage_level'] = 7
                else:
                    renewables.at[i, 'voltage_level'] = 5
        # restrict plants to considered power levels
        if 'EHV' in grid_data.target_input.power_levels[0]:
            renewables = renewables
        elif 'HV' in grid_data.target_input.power_levels[0]:
            renewables = renewables[renewables.voltage_level >= 3]
        elif 'MV' in grid_data.target_input.power_levels[0]:
            renewables = renewables[renewables.voltage_level >= 5]
        elif 'LV' in grid_data.target_input.power_levels[0]:
            renewables = renewables[renewables.voltage_level == 7]
        # find exact location by adress for renewable power plants which are on mv-level or lower
        if ('LV' in grid_data.target_input.power_levels[0]) or ('MV' in grid_data.target_input.power_levels[0]):
            geolocator = ArcGIS(timeout=10000)  # set on None when geopy 2.0 was released
            plant_georefernce = renewables[renewables.voltage_level >= 5]
            for i, plant in plant_georefernce.iterrows():
                if plant.address:
                    address = str(plant.address)+' ' + str(plant.postcode)+' '+str(plant.city)
                    location = geolocator.geocode(address)
                    renewables.at[i, 'lon'] = location.longitude
                    renewables.at[i, 'lat'] = location.latitude
                else:
                    pass
                    # zu diesem Zeitpunkt erstmal die Geokoordinaten des Rasterpunktes 
                    # behalten, falls keine Adresse bekannt. Das aber noch abändern. 
        # convert DataFrame into a GeoDataFrame
        renewables_geo = gpd.GeoDataFrame(renewables,
                                          crs = 'EPSG:4326',
                                          geometry=gpd.points_from_xy(renewables.lon,
                                                                      renewables.lat))
        # intersection of power plants with target_area when target is an own area
        if typ == 'own area':
            renewables_geo = gpd.overlay(renewables_geo, grid_data.area, how='intersection')
        # --- node assignment with case distinction depending on considered power levels
        # divide the plants in the target area according to their voltage level
        renewables_lv = renewables_geo[renewables_geo.voltage_level == 7]
        renewables_mv_lv = renewables_geo[renewables_geo.voltage_level == 6]
        renewables_mv = renewables_geo[renewables_geo.voltage_level == 5]
        renewables_hv_mv = renewables_geo[renewables_geo.voltage_level == 4]
        renewables_hv = renewables_geo[renewables_geo.voltage_level == 3]
        renewables_ehv_hv = renewables_geo[renewables_geo.voltage_level == 2]
        renewables_ehv = renewables_geo[renewables_geo.voltage_level == 1]
        # define power_levels
        power_levels = grid_data.target_input.power_levels[0]
        
        # --- nodes for level 7 plants (LV)
        if not renewables_lv.empty:
            if 'LV' in power_levels:
                # In this case the Level 7 plants are assigned to the nearest lv node
                voronoi_polygons = voronoi(grid_data.lv_data.lv_nodes[['dave_name', 'geometry']])
                intersection = gpd.sjoin(renewables_lv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right', 'centroid'])
                intersection = intersection.rename(columns={'dave_name': 'bus'})
                grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(intersection)
            # find next higher and considered voltage level to assigne the lv-plants
            elif ('MV' in power_levels) or ('HV' in power_levels) or ('EHV' in power_levels):
                if 'MV' in power_levels:
                    # In this case the Level 7 plants are aggregated and assigned to the nearest mv/lv-transformer
                    voronoi_polygons = voronoi(grid_data.components_power.transformers.mv_lv[['dave_name',
                                                                                              'geometry']])
                    voltage_level = 6
                    #In diesem Fall die Erzeuger mittels voronoi und Aggregation den MV/LV TRafos zuordnen
                elif 'HV' in power_levels:
                    # In this case the Level 7 plants are aggregated and assigned to the nearest hv/mv-transformer
                    voronoi_polygons = voronoi(grid_data.components_power.transformers.hv_mv[['dave_name',
                                                                                              'geometry']])
                    voltage_level = 4
                elif 'EHV' in power_levels:
                    # In this case the Level 7 plants are aggregated and assigned to the nearest ehv/hv-transformer
                    voronoi_polygons = voronoi(grid_data.components_power.transformers.ehv_hv[['dave_name',
                                                                                               'geometry']])
                    voltage_level = 2
                intersection = gpd.sjoin(renewables_lv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right'])
                intersection = intersection.rename(columns={'centroid': 'connection_node',
                                                            'dave_name': 'connection_trafo_dave_name'})
                # change voltage level to the new connection level
                intersection.voltage_level = voltage_level
                # select only data which is relevant after aggregation
                intersection_rel = intersection[['electrical_capacity_kw',
                                                  'generation_type',
                                                  'voltage_level',
                                                  'source',
                                                  'connection_node',
                                                  'connection_trafo_dave_name']]
                # aggregated power plants, set geometry to the connection node and write them into grid data
                aggregate_plants_ren(grid_data, intersection_rel, aggregate_name='level 7 plants')

        # --- nodes for level 6 plants (MV/LV)
        if not renewables_mv_lv.empty:
            if ('LV' in power_levels) or ('MV' in power_levels):
                # In this case the Level 6 plants are assigned to the nearest mv/lv-transformer
                voronoi_polygons = voronoi(grid_data.components_power.transformers.mv_lv[['dave_name',
                                                                                          'geometry']])
                intersection = gpd.sjoin(renewables_mv_lv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.rename(columns={'dave_name': 'trafo_name'})
                # search transformer bus lv name
                trafos = grid_data.components_power.transformers.mv_lv
                for i, plant in intersection.iterrows():
                    trafo_bus_lv = trafos[trafos.dave_name == plant.trafo_name].iloc[0].bus_lv
                    intersection.at[plant.name, 'bus'] = trafo_bus_lv
                intersection = intersection.drop(columns=['index_right', 'centroid', 'trafo_name'])
                grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(intersection)
            # find next higher and considered voltage level to assigne the mvlv-plants
            elif ('HV' in power_levels) or ('EHV' in power_levels):
                if 'HV' in power_levels:
                    # In this case the Level 6 plants are aggregated and assigned to the nearest hv/mv-transformer
                    voronoi_polygons = voronoi(grid_data.components_power.transformers.hv_mv[['dave_name', 
                                                                                              'geometry']])
                    voltage_level = 4
                elif 'EHV' in power_levels:
                    # In this case the Level 6 plants are aggregated and assigned to the nearest ehv/hv-transformer
                    voronoi_polygons = voronoi(grid_data.components_power.transformers.ehv_hv[['dave_name', 
                                                                                               'geometry']])
                    voltage_level = 2
                intersection = gpd.sjoin(renewables_mv_lv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right'])
                intersection = intersection.rename(columns={'centroid': 'connection_node',
                                                            'dave_name': 'connection_trafo_dave_name'})
                # change voltage level to the new connection level
                intersection.voltage_level = voltage_level
                # select only data which is relevant after aggregation
                intersection_rel = intersection[['electrical_capacity_kw',
                                                  'generation_type',
                                                  'voltage_level',
                                                  'source',
                                                  'connection_node',
                                                  'connection_trafo_dave_name']]
                # aggregated power plants, set geometry to the connection node and write them into grid data
                aggregate_plants_ren(grid_data, intersection_rel, aggregate_name='level 6 plants')

        # --- nodes for level 5 plants (MV)
        if not renewables_mv.empty:
            if 'MV' in power_levels:
                # In this case the Level 5 plants are assigned to the nearest mv node
                voronoi_polygons = voronoi(grid_data.mv_data.mv_nodes[['dave_name', 
                                                                       'geometry']])
                intersection = gpd.sjoin(renewables_mv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right', 'centroid'])
                intersection = intersection.rename(columns={'dave_name': 'bus'})
                grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(intersection)
            # find next higher and considered voltage level to assigne the mv-plants
            elif ('HV' in power_levels) or ('EHV' in power_levels):
                if 'HV' in power_levels:
                    # In this case the Level 5 plants are aggregated and assigned to the nearest hv/mv-transformer
                    voronoi_polygons = voronoi(grid_data.components_power.transformers.hv_mv[['dave_name', 
                                                                                              'geometry']])
                    voltage_level = 4
                elif 'EHV' in power_levels:
                    # In this case the Level 5 plants are aggregated and assigned to the nearest ehv/hv-transformer
                    voronoi_polygons = voronoi(grid_data.components_power.transformers.ehv_hv[['dave_name',
                                                                                               'geometry']])
                    voltage_level = 2
                intersection = gpd.sjoin(renewables_mv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right'])
                intersection = intersection.rename(columns={'centroid': 'connection_node',
                                                            'dave_name': 'connection_trafo_dave_name'})
                # change voltage level to the new connection level
                intersection.voltage_level = voltage_level
                # select only data which is relevant after aggregation
                intersection_rel = intersection[['electrical_capacity_kw',
                                                  'generation_type',
                                                  'voltage_level',
                                                  'source',
                                                  'connection_node',
                                                  'connection_trafo_dave_name']]
                # aggregated power plants, set geometry to the connection node and write them into grid data
                aggregate_plants_ren(grid_data, intersection_rel, aggregate_name='level 5 plants')

        # --- nodes for level 4 plants (HV/MV)
        if not renewables_hv_mv.empty:
            if ('MV' in power_levels) or ('HV' in power_levels):
                # In this case the Level 4 plants are assigned to the nearest hv/mv-transformer
                voronoi_polygons = voronoi(grid_data.components_power.transformers.hv_mv[['dave_name',
                                                                                          'geometry']])
                intersection = gpd.sjoin(renewables_hv_mv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.rename(columns={'dave_name': 'trafo_name'})
                # search transformer bus lv name
                trafos = grid_data.components_power.transformers.hv_mv
                for i, plant in intersection.iterrows():
                    trafo_bus_lv = trafos[trafos.dave_name == plant.trafo_name].iloc[0].bus_lv
                    intersection.at[plant.name, 'bus'] = trafo_bus_lv
                intersection = intersection.drop(columns=['index_right', 'centroid', 'trafo_name'])
                grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(intersection)
            # find next higher and considered voltage level to assigne the hvmv-plants
            elif 'EHV' in power_levels:
                # In this case the Level 4 plants are aggregated and assigned to the nearest ehv/hv-transformer
                voronoi_polygons = voronoi(grid_data.components_power.transformers.ehv_hv[['dave_name',
                                                                                           'geometry']])
                intersection = gpd.sjoin(renewables_hv_mv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right'])
                intersection = intersection.rename(columns={'centroid': 'connection_node',
                                                            'dave_name': 'connection_trafo_dave_name'})
                # change voltage level to the new connection level
                intersection.voltage_level = 2
                # select only data which is relevant after aggregation
                intersection_rel = intersection[['electrical_capacity_kw',
                                                  'generation_type',
                                                  'voltage_level',
                                                  'source',
                                                  'connection_node',
                                                  'connection_trafo_dave_name']]
                # aggregated power plants, set geometry to the connection node and write them into grid data
                aggregate_plants_ren(grid_data, intersection_rel, aggregate_name='level 4 plants')

        # --- nodes for level 3 plants (HV)
        if not renewables_hv.empty:
            if 'HV' in power_levels:
                # In this case the Level 3 plants are assigned to the nearest hv node
                voronoi_polygons = voronoi(grid_data.hv_data.hv_nodes[['dave_name',
                                                                       'geometry']])
                intersection = gpd.sjoin(renewables_hv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right', 'centroid'])
                intersection = intersection.rename(columns={'dave_name': 'bus'})
                grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(intersection)
            # find next higher and considered voltage level to assigne the hv-plants
            elif 'EHV' in power_levels:
                # In this case the Level 3 plants are aggregated and assigned to the nearest ehv/hv-transformer
                voronoi_polygons = voronoi(grid_data.components_power.transformers.ehv_hv[['dave_name',
                                                                                           'geometry']])
                intersection = gpd.sjoin(renewables_hv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right'])
                intersection = intersection.rename(columns={'centroid': 'connection_node',
                                                            'dave_name': 'connection_trafo_dave_name'})
                # change voltage level to the new connection level
                intersection.voltage_level = 2
                # select only data which is relevant after aggregation
                intersection_rel = intersection[['electrical_capacity_kw',
                                                  'generation_type',
                                                  'voltage_level',
                                                  'source',
                                                  'connection_node',
                                                  'connection_trafo_dave_name']]
                # aggregated power plants, set geometry to the connection node and write them into grid data
                aggregate_plants_ren(grid_data, intersection_rel, aggregate_name='level 3 plants')

        # --- nodes for level 2 plants (EHV/HV)
        if not renewables_ehv_hv.empty:
            if ('HV' in power_levels) or ('EHV' in power_levels):
                # In this case the Level 2 plants are assigned to the nearest ehv/hv-transformer
                voronoi_polygons = voronoi(grid_data.components_power.transformers.ehv_hv[['dave_name',
                                                                                           'geometry']])
                intersection = gpd.sjoin(renewables_ehv_hv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.rename(columns={'dave_name': 'trafo_name'})
                # search transformer bus lv name
                trafos = grid_data.components_power.transformers.ehv_hv
                for i, plant in intersection.iterrows():
                    trafo_bus_lv = trafos[trafos.dave_name == plant.trafo_name].iloc[0].bus_lv
                    intersection.at[plant.name, 'bus'] = trafo_bus_lv
                intersection = intersection.drop(columns=['index_right', 'centroid', 'trafo_name'])
                grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(intersection)

        # --- nodes for level 1 plants (EHV)
        if not renewables_ehv.empty:
            if 'EHV' in power_levels:
                # In this case the Level 1 plants are assigned to the nearest ehv node
                voronoi_polygons = voronoi(grid_data.ehv_data.ehv_nodes[['dave_name',
                                                                         'geometry']])
                intersection = gpd.sjoin(renewables_ehv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right', 'centroid'])
                intersection = intersection.rename(columns={'dave_name': 'bus'})
                grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(intersection)
        # add dave name
        grid_data.components_power.renewable_powerplants.insert(0, 'dave_name', None)
        grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.reset_index(drop=True)
        for i, plant in grid_data.components_power.renewable_powerplants.iterrows():
            grid_data.components_power.renewable_powerplants.at[plant.name, 'dave_name'] = f'ren_powerplant_{plant.voltage_level}_{i}'


def conventional_powerplants(grid_data):
    """
    This function collects the generators based on ego_conventional_powerplant from OEP
    Furthermore assign a grid node to the generators and aggregated them depending on the situation
    """
    print('create conventional powerplants for target area')
    print('-----------------------------------------------')
    # load powerplant data in target area
    typ = grid_data.target_input.typ.iloc[0]
    if typ in ['postalcode', 'federal state', 'own area']:
        for plz in grid_data.target_input.data.iloc[0]:
            where = f'postcode={plz}'
            data = oep_request(schema='supply',
                               table='ego_conventional_powerplant',
                               where=where)
            if plz == grid_data.target_input.data.iloc[0][0]:
                conventionals = data
            else:
                conventionals = conventionals.append(data)
    elif typ == 'town name':
        for name in grid_data.target_input.data.iloc[0]:
            where = f'city={name}'
            data = oep_request(schema='supply',
                               table='ego_conventional_powerplant',
                               where=where)
            if name == grid_data.target_input.data.iloc[0][0]:
                conventionals = data
            else:
                conventionals = conventionals.append(data)
    # prepare the DataFrame of the conventional plants
    if not conventionals.empty:
        conventionals = conventionals.reset_index()
        conventionals = conventionals.drop(columns=['gid',
                                                    'geom',
                                                    'index'])
        conventionals = conventionals.rename(columns={'capacity': 'capacity_mw',
                                                      'chp_capacity_uba': 'chp_capacity_uba_mw'})
        # prepare power plant voltage parameter for processing
        for i, plant in conventionals.iterrows():
            if plant.voltage == None:
                conventionals.at[plant.name, 'voltage'] = 'None'
            elif plant.voltage in ['HS', '10 und 110', '110/6']:
                conventionals.at[plant.name, 'voltage'] = '110'
            elif plant.voltage in ['MS', 'MSP', '10kV, 25kV', 'Mai 25']:
                conventionals.at[plant.name, 'voltage'] = '20'
            elif plant.voltage == '220 / 110 / 10':
                conventionals.at[plant.name, 'voltage'] = '220'
            elif plant.voltage == '30 auf 6':
                conventionals.at[plant.name, 'voltage'] = '30'
            elif plant.voltage == '6\n20':
                conventionals.at[plant.name, 'voltage'] = 'Werknetz'
        # drop plants with no voltage specification, plants at factory networks and shutdowned plants
        drop_plants = conventionals[conventionals.voltage.isin(['Werknetz', 'None'])].index.to_list()
        drop_plants = drop_plants + conventionals[conventionals.status == 'shutdown'].index.to_list()
        conventionals = conventionals.drop(drop_plants)
        # add voltage level
        for i, plant in conventionals.iterrows():
            if plant.voltage == 'HS':
                conventionals.at[i, 'voltage_level'] = 3
            elif plant.voltage == 'HS/MS':
                conventionals.at[i, 'voltage_level'] = 4
            elif plant.voltage == 'MS':
                conventionals.at[i, 'voltage_level'] = 5
            elif int(plant.voltage) >= 220:
                conventionals.at[i, 'voltage_level'] = 1
            elif int(plant.voltage) == 110:
                conventionals.at[i, 'voltage_level'] = 3
            elif (int(plant.voltage) <= 50) and (int(plant.voltage) >= 1):
                conventionals.at[i, 'voltage_level'] = 5
            elif int(plant.voltage) <= 0.4:
                conventionals.at[i, 'voltage_level'] = 7
        # add voltage level
        for i, plant in conventionals.iterrows():
            if plant.voltage == 'HS/MS':
                conventionals.at[i, 'voltage_level'] = 4
            elif int(plant.voltage) >= 220:
                conventionals.at[i, 'voltage_level'] = 1
            elif (int(plant.voltage) < 220) and (int(plant.voltage) >= 60):
                conventionals.at[i, 'voltage_level'] = 3
            elif (int(plant.voltage) < 60) and (int(plant.voltage) >= 1):
                conventionals.at[i, 'voltage_level'] = 5
            elif int(plant.voltage) < 1:
                conventionals.at[i, 'voltage_level'] = 7
        # restrict plants to considered power levels
        if 'EHV' in grid_data.target_input.power_levels[0]:
            conventionals = conventionals
        elif 'HV' in grid_data.target_input.power_levels[0]:
            conventionals = conventionals[conventionals.voltage_level >= 3]
        elif 'MV' in grid_data.target_input.power_levels[0]:
            conventionals = conventionals[conventionals.voltage_level >= 5]
        elif 'LV' in grid_data.target_input.power_levels[0]:
            conventionals = conventionals[conventionals.voltage_level == 7]
        # convert DataFrame into a GeoDataFrame
        conventionals_geo = gpd.GeoDataFrame(conventionals,
                                             crs='EPSG:4326',
                                             geometry=gpd.points_from_xy(conventionals.lon,
                                                                         conventionals.lat))
        # intersection of power plants with target_area when target is an own area
        if (typ == 'own area') and (not conventionals_geo.empty):
            conventionals_geo = gpd.overlay(conventionals_geo, grid_data.area, how='intersection')
        # --- node assignment with case distinction depending on considered power levels
        # divide the plants in the target area according to their voltage level
        conventionals_lv = conventionals_geo[conventionals_geo.voltage_level == 7]
        conventionals_mv_lv = conventionals_geo[conventionals_geo.voltage_level == 6]
        conventionals_mv = conventionals_geo[conventionals_geo.voltage_level == 5]
        conventionals_hv_mv = conventionals_geo[conventionals_geo.voltage_level == 4]
        conventionals_hv = conventionals_geo[conventionals_geo.voltage_level == 3]
        conventionals_ehv_hv = conventionals_geo[conventionals_geo.voltage_level == 2]
        conventionals_ehv = conventionals_geo[conventionals_geo.voltage_level == 1]
        # define power_levels
        power_levels = grid_data.target_input.power_levels[0]

        # --- nodes for level 7 plants (LV)
        if not conventionals_lv.empty:
            if 'LV' in power_levels:
                # In this case the Level 7 plants are assigned to the nearest lv node
                voronoi_polygons = voronoi(grid_data.lv_data.lv_nodes[['dave_name', 'geometry']])
                intersection = gpd.sjoin(conventionals_lv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right', 'centroid'])
                intersection = intersection.rename(columns={'dave_name': 'bus',
                                                            'capacity_mw': 'electrical_capacity_mw'})
                grid_data.components_power.conventional_powerplants = grid_data.components_power.conventional_powerplants.append(intersection)
            # find next higher and considered voltage level to assigne the lv-plants
            elif ('MV' in power_levels) or ('HV' in power_levels) or ('EHV' in power_levels):
                if 'MV' in power_levels:
                    # In this case the Level 7 plants are aggregated and assigned to the nearest mv/lv-transformer
                    voronoi_polygons = voronoi(grid_data.components_power.transformers.mv_lv[['dave_name', 
                                                                                              'geometry']])
                    voltage_level = 6
                elif 'HV' in power_levels:
                    # In this case the Level 7 plants are aggregated and assigned to the nearest hv/mv-transformer
                    voronoi_polygons = voronoi(grid_data.components_power.transformers.hv_mv[['dave_name', 
                                                                                              'geometry']])
                    voltage_level = 4
                elif 'EHV' in power_levels:
                    # In this case the Level 7 plants are aggregated and assigned to the nearest ehv/hv-transformer
                    voronoi_polygons = voronoi(grid_data.components_power.transformers.ehv_hv[['dave_name', 
                                                                                               'geometry']])
                    voltage_level = 2
                intersection = gpd.sjoin(conventionals_lv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right'])
                intersection = intersection.rename(columns={'centroid': 'connection_node',
                                                            'dave_name': 'connection_trafo_dave_name'})
                # change voltage level to the new connection level
                intersection.voltage_level = voltage_level
                # select only data which is relevant after aggregation
                intersection_rel =  intersection[['capacity_mw',
                                                  'voltage_level',
                                                  'fuel',
                                                  'connection_node',
                                                  'connection_trafo_dave_name']]
                # aggregated power plants, set geometry to the connection node and write them into grid data
                aggregate_plants_con(grid_data, intersection_rel, aggregate_name= 'level 7 plants')
        
        # --- nodes for level 6 plants (MV/LV)
        if not conventionals_mv_lv.empty:
            if ('LV' in power_levels) or ('MV' in power_levels):
                # In this case the Level 6 plants are assigned to the nearest mv/lv-transformer
                voronoi_polygons = voronoi(grid_data.components_power.transformers.mv_lv[['dave_name', 
                                                                                          'geometry']])
                intersection = gpd.sjoin(conventionals_mv_lv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right', 'centroid'])
                intersection = intersection.rename(columns={'dave_name': 'trafo_name',
                                                            'capacity_mw': 'electrical_capacity_mw'})
                # search transformer bus lv name
                trafos = grid_data.components_power.transformers.mv_lv
                for i, plant in intersection.iterrows():
                    trafo_bus_lv = trafos[trafos.dave_name == plant.trafo_name].iloc[0].bus_lv
                    intersection.at[plant.name, 'bus'] = trafo_bus_lv
                intersection = intersection.drop(columns=['index_right', 'centroid', 'trafo_name'])
                grid_data.components_power.conventional_powerplants = grid_data.components_power.conventional_powerplants.append(intersection)
            # find next higher and considered voltage level to assigne the mvlv-plants
            elif ('HV' in power_levels) or ('EHV' in power_levels):
                if 'HV' in power_levels:
                    # In this case the Level 6 plants are aggregated and assigned to the nearest hv/mv-transformer
                    voronoi_polygons = voronoi(grid_data.components_power.transformers.hv_mv[['dave_name',
                                                                                              'geometry']])
                    voltage_level = 4
                elif 'EHV' in power_levels:
                    # In this case the Level 6 plants are aggregated and assigned to the nearest ehv/hv-transformer
                    voronoi_polygons = voronoi(grid_data.components_power.transformers.ehv_hv[['dave_name', 
                                                                                               'geometry']])
                    voltage_level = 2
                intersection = gpd.sjoin(conventionals_mv_lv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right'])
                intersection = intersection.rename(columns={'centroid': 'connection_node',
                                                            'dave_name': 'connection_trafo_dave_name'})
                # change voltage level to the new connection level
                intersection.voltage_level = voltage_level
                # select only data which is relevant after aggregation
                intersection_rel =  intersection[['capacity_mw',
                                                  'voltage_level',
                                                  'fuel',
                                                  'connection_node',
                                                  'connection_trafo_dave_name']]
                # aggregated power plants, set geometry to the connection node and write them into grid data
                aggregate_plants_con(grid_data, intersection_rel, aggregate_name= 'level 6 plants')

        # --- nodes for level 5 plants (MV)
        if not conventionals_mv.empty:
            if 'MV' in power_levels:
                # In this case the Level 5 plants are assigned to the nearest mv node
                voronoi_polygons = voronoi(grid_data.mv_data.mv_nodes[['dave_name', 'geometry']])
                intersection = gpd.sjoin(conventionals_mv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right', 'centroid'])
                intersection = intersection.rename(columns={'dave_name': 'bus',
                                                            'capacity_mw': 'electrical_capacity_mw'})
                grid_data.components_power.conventional_powerplants = grid_data.components_power.conventional_powerplants.append(intersection)
            # find next higher and considered voltage level to assigne the mv-plants
            elif  ('HV' in power_levels) or ('EHV' in power_levels):
                if 'HV' in power_levels:
                    # In this case the Level 5 plants are aggregated and assigned to the nearest hv/mv-transformer
                    voronoi_polygons = voronoi(grid_data.components_power.transformers.hv_mv[['dave_name',
                                                                                              'geometry']])
                    voltage_level = 4
                elif 'EHV' in power_levels:
                    # In this case the Level 5 plants are aggregated and assigned to the nearest ehv/hv-transformer
                    voronoi_polygons = voronoi(grid_data.components_power.transformers.ehv_hv[['dave_name', 
                                                                                               'geometry']])
                    voltage_level = 2
                intersection = gpd.sjoin(conventionals_mv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right'])
                intersection = intersection.rename(columns={'centroid': 'connection_node',
                                                            'dave_name': 'connection_trafo_dave_name'})
                # change voltage level to the new connection level
                intersection.voltage_level = voltage_level
                # select only data which is relevant after aggregation
                intersection_rel =  intersection[['capacity_mw',
                                                  'voltage_level',
                                                  'fuel',
                                                  'connection_node',
                                                  'connection_trafo_dave_name']]
                # aggregated power plants, set geometry to the connection node and write them into grid data
                aggregate_plants_con(grid_data, intersection_rel, aggregate_name= 'level 5 plants')

        # --- nodes for level 4 plants (HV/MV)
        if not conventionals_hv_mv.empty:
            if ('MV' in power_levels) or ('HV' in power_levels):
                # In this case the Level 4 plants are assigned to the nearest hv/mv-transformer
                voronoi_polygons = voronoi(grid_data.components_power.transformers.hv_mv[['dave_name',
                                                                                          'geometry']])
                intersection = gpd.sjoin(conventionals_hv_mv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right', 'centroid'])
                intersection = intersection.rename(columns={'dave_name': 'trafo_name',
                                                            'capacity_mw': 'electrical_capacity_mw'})
                # search transformer bus lv name
                trafos = grid_data.components_power.transformers.hv_mv
                for i, plant in intersection.iterrows():
                    trafo_bus_lv = trafos[trafos.dave_name == plant.trafo_name].iloc[0].bus_lv
                    intersection.at[plant.name, 'bus'] = trafo_bus_lv
                intersection = intersection.drop(columns=['index_right', 'centroid', 'trafo_name'])
                grid_data.components_power.conventional_powerplants = grid_data.components_power.conventional_powerplants.append(intersection)
            # find next higher and considered voltage level to assigne the hvmv-plants
            elif 'EHV' in power_levels:
                # In this case the Level 4 plants are aggregated and assigned to the nearest ehv/hv-transformer
                voronoi_polygons = voronoi(grid_data.components_power.transformers.ehv_hv[['dave_name', 
                                                                                           'geometry']])
                intersection = gpd.sjoin(conventionals_hv_mv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right'])
                intersection = intersection.rename(columns={'centroid': 'connection_node',
                                                            'dave_name': 'connection_trafo_dave_name'})
                # change voltage level to the new connection level
                intersection.voltage_level = 2
                # select only data which is relevant after aggregation
                intersection_rel =  intersection[['capacity_mw',
                                                  'voltage_level',
                                                  'fuel',
                                                  'connection_node',
                                                  'connection_trafo_dave_name']]
                # aggregated power plants, set geometry to the connection node and write them into grid data
                aggregate_plants_con(grid_data, intersection_rel, aggregate_name= 'level 4 plants')

        # --- nodes for level 3 plants (HV)
        if not conventionals_hv.empty:
            if 'HV' in power_levels:
                # In this case the Level 3 plants are assigned to the nearest hv node
                voronoi_polygons = voronoi(grid_data.hv_data.hv_nodes[['dave_name', 'geometry']])
                intersection = gpd.sjoin(conventionals_hv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right', 'centroid'])
                intersection = intersection.rename(columns={'dave_name': 'bus',
                                                            'capacity_mw': 'electrical_capacity_mw'})
                grid_data.components_power.conventional_powerplants = grid_data.components_power.conventional_powerplants.append(intersection)
            # find next higher and considered voltage level to assigne the hv-plants
            elif 'EHV' in power_levels:
                # In this case the Level 3 plants are aggregated and assigned to the nearest ehv/hv-transformer
                voronoi_polygons = voronoi(grid_data.components_power.transformers.ehv_hv[['dave_name',
                                                                                           'geometry']])
                intersection = gpd.sjoin(conventionals_hv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right'])
                intersection = intersection.rename(columns={'centroid': 'connection_node',
                                                            'dave_name': 'connection_trafo_dave_name'})
                # change voltage level to the new connection level
                intersection.voltage_level = 2
                # select only data which is relevant after aggregation
                intersection_rel =  intersection[['capacity_mw',
                                                  'voltage_level',
                                                  'fuel',
                                                  'connection_node',
                                                  'connection_trafo_dave_name']]
                # aggregated power plants, set geometry to the connection node and write them into grid data
                aggregate_plants_con(grid_data, intersection_rel, aggregate_name= 'level 3 plants')

        # --- nodes for level 2 plants (EHV/HV)
        if not conventionals_ehv_hv.empty:
            if ('HV' in power_levels) or ('EHV' in power_levels):
                # In this case the Level 2 plants are assigned to the nearest ehv/hv-transformer
                voronoi_polygons = voronoi(grid_data.components_power.transformers.ehv_hv[['dave_name', 
                                                                                           'geometry']])
                intersection = gpd.sjoin(conventionals_ehv_hv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.rename(columns={'dave_name': 'trafo_name',
                                                            'capacity_mw': 'electrical_capacity_mw'})
                # search transformer bus lv name
                trafos = grid_data.components_power.transformers.ehv_hv
                for i, plant in intersection.iterrows():
                    trafo_bus_lv = trafos[trafos.dave_name == plant.trafo_name].iloc[0].bus_lv
                    intersection.at[plant.name, 'bus'] = trafo_bus_lv
                intersection = intersection.drop(columns=['index_right', 'centroid', 'trafo_name'])
                grid_data.components_power.conventional_powerplants = grid_data.components_power.conventional_powerplants.append(intersection)

        # --- nodes for level 1 plants (EHV)
        if not conventionals_ehv.empty:
            if 'EHV' in power_levels:
                # In this case the Level 1 plants are assigned to the nearest ehv node
                voronoi_polygons = voronoi(grid_data.ehv_data.ehv_nodes[['dave_name', 
                                                                         'geometry']])
                intersection = gpd.sjoin(conventionals_ehv, voronoi_polygons, how='inner', op='intersects')
                intersection = intersection.drop(columns=['index_right', 'centroid'])
                intersection = intersection.rename(columns={'dave_name': 'bus',
                                                            'capacity_mw': 'electrical_capacity_mw'})
                grid_data.components_power.conventional_powerplants = grid_data.components_power.conventional_powerplants.append(intersection)

        # add dave name
        grid_data.components_power.conventional_powerplants.insert(0, 'dave_name', None)
        grid_data.components_power.conventional_powerplants = grid_data.components_power.conventional_powerplants.reset_index(drop=True)
        for i, plant in grid_data.components_power.conventional_powerplants.iterrows():
            voltage_level = int(plant.voltage_level)
            grid_data.components_power.conventional_powerplants.at[plant.name, 'dave_name'] = f'con_powerplant_{voltage_level}_{i}'

def transformators(grid_data):
    """
    This function collects the transformers.
    EHV/EHV and EHV/HV trafos are based on ego_pf_hv_transformer from OEP
    HV/MV trafos are based on ego_dp_hvmv_substation from OEP
    MV/LV trafos are based on 
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
        if not hv_trafos.empty:
            remove_columns = grid_data.area.keys().tolist()
            remove_columns.remove('geometry')
            hv_trafos = hv_trafos.drop(columns=remove_columns)
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
            if not ehvhv_buses.empty:
                remove_columns = grid_data.area.keys().tolist()
                remove_columns.remove('geometry')
                ehvhv_buses = ehvhv_buses.drop(columns=remove_columns)
        # search for trafo voltage and create missing nodes
        for i, trafo in hv_trafos.iterrows():
            if 'EHV' in grid_data.target_input.power_levels[0]:
                ehv_bus0 = grid_data.ehv_data.ehv_nodes[grid_data.ehv_data.ehv_nodes.ego_bus_id == trafo.bus0]
                ehv_bus1 = grid_data.ehv_data.ehv_nodes[grid_data.ehv_data.ehv_nodes.ego_bus_id == trafo.bus1]
                if not ehv_bus0.empty:
                    ehv_bus_index0 = ehv_bus0.index[0]
                    hv_trafos.at[trafo.name, 'voltage_kv_lv'] = grid_data.ehv_data.ehv_nodes.loc[ehv_bus_index0].voltage_kv
                if not ehv_bus1.empty:
                    ehv_bus_index1 = ehv_bus1.index[0]
                    hv_trafos.at[trafo.name, 'voltage_kv_hv'] = grid_data.ehv_data.ehv_nodes.loc[ehv_bus_index1].voltage_kv
                if ('HV' not in grid_data.target_input.power_levels[0]) and (ehv_bus0.empty):
                    hv_buses = ehvhv_buses[ehvhv_buses.voltage_kv.isin([110])]
                    hv_bus0 = hv_buses[hv_buses.ego_bus_id == trafo.bus0]
                    if not hv_bus0.empty:
                        hv_bus_index0 = hv_bus0.index[0]
                        hv_trafos.at[trafo.name, 'voltage_kv_lv'] = hv_buses.loc[hv_bus_index0].voltage_kv
                        # check if node allready exsist, otherwise create them
                        if grid_data.hv_data.hv_nodes.empty:
                            hv_bus0['voltage_level'] = 3
                            grid_data.hv_data.hv_nodes = grid_data.hv_data.hv_nodes.append(hv_bus0)
                        else:
                            if grid_data.hv_data.hv_nodes[grid_data.hv_data.hv_nodes.ego_bus_id == trafo.bus0].empty:
                                hv_bus0['voltage_level'] = 3
                                grid_data.hv_data.hv_nodes = grid_data.hv_data.hv_nodes.append(hv_bus0)
                                
            if 'HV' in grid_data.target_input.power_levels[0]:
                hv_bus0 = grid_data.hv_data.hv_nodes[grid_data.hv_data.hv_nodes.ego_bus_id == trafo.bus0]
                if not hv_bus0.empty:
                    hv_bus_index0 = hv_bus0.index[0]
                    hv_trafos.at[trafo.name, 'voltage_kv_lv'] = grid_data.hv_data.hv_nodes.loc[hv_bus_index0].voltage_kv
                if ('EHV' not in grid_data.target_input.power_levels[0]) and (not hv_bus0.empty):
                    ehv_buses = ehvhv_buses[ehvhv_buses.voltage_kv.isin([380, 220])]
                    ehv_bus1 = ehv_buses[ehv_buses.ego_bus_id == trafo.bus1]
                    if not ehv_bus1.empty:
                        ehv_bus_index1 = ehv_bus1.index[0]
                        hv_trafos.at[trafo.name, 'voltage_kv_hv'] = ehv_buses.loc[ehv_bus_index1].voltage_kv
                        # check if node allready exsist, otherwise create them
                        if grid_data.ehv_data.ehv_nodes.empty:
                            ehv_bus1['voltage_level'] = 1
                            grid_data.ehv_data.ehv_nodes = grid_data.ehv_data.ehv_nodes.append(ehv_bus1)
                        else:
                            if grid_data.ehv_data.ehv_nodes[grid_data.ehv_data.ehv_nodes.ego_bus_id == trafo.bus1].empty:
                                ehv_bus1['voltage_level'] = 1
                                grid_data.ehv_data.ehv_nodes = grid_data.ehv_data.ehv_nodes.append(ehv_bus1)
        # add dave name for nodes which are created for the transformers
        if 'dave_name' not in grid_data.hv_data.hv_nodes.keys():
            hv_buses = grid_data.hv_data.hv_nodes
            grid_data.hv_data.hv_nodes.insert(0, 'dave_name', None)
            grid_data.hv_data.hv_nodes = grid_data.hv_data.hv_nodes.reset_index(drop=True)
            for i, bus in grid_data.hv_data.hv_nodes.iterrows():
                grid_data.hv_data.hv_nodes.at[bus.name, 'dave_name'] = f'node_3_{i}'
        if 'dave_name' not in grid_data.ehv_data.ehv_nodes.keys():
            # add dave name
            grid_data.ehv_data.ehv_nodes.insert(0, 'dave_name', None)
            grid_data.ehv_data.ehv_nodes = grid_data.ehv_data.ehv_nodes.reset_index(drop=True)
            for i, bus in grid_data.ehv_data.ehv_nodes.iterrows():
                grid_data.ehv_data.ehv_nodes.at[bus.name, 'dave_name'] = f'node_1_{i}'
        # write transformator data in grid data and decied the grid level depending on voltage level
        if not hv_trafos.empty:                        
            if 'EHV' in grid_data.target_input.power_levels[0]:
                ehv_ehv_trafos = hv_trafos[hv_trafos.voltage_kv_lv.isin([380, 220])]
                ehv_ehv_trafos['voltage_level'] = 1
                # add dave name for trafo and connection buses
                ehv_ehv_trafos.insert(0, 'dave_name', None)
                ehv_ehv_trafos.insert(1, 'bus_hv', None)
                ehv_ehv_trafos.insert(2, 'bus_lv', None)
                ehv_ehv_trafos = ehv_ehv_trafos.reset_index(drop=True)
                for i, trafo in ehv_ehv_trafos.iterrows():
                    ehv_ehv_trafos.at[trafo.name, 'dave_name'] = f'trafo_1_{i}'
                    # search for bus dave name and replace ego id
                    ehv_buses = grid_data.ehv_data.ehv_nodes
                    bus0_name = ehv_buses[ehv_buses.ego_bus_id == trafo.bus0].iloc[0].dave_name
                    bus1_name = ehv_buses[ehv_buses.ego_bus_id == trafo.bus1].iloc[0].dave_name
                    subst_name = ehv_buses[ehv_buses.ego_bus_id == trafo.bus0].iloc[0].subst_name
                    tso_name = ehv_buses[ehv_buses.ego_bus_id == trafo.bus0].iloc[0].tso_name
                    ehv_ehv_trafos.at[trafo.name, 'bus_lv'] = bus0_name
                    ehv_ehv_trafos.at[trafo.name, 'bus_hv'] = bus1_name
                    ehv_ehv_trafos.at[trafo.name, 'substation_name'] = subst_name
                    ehv_ehv_trafos.at[trafo.name, 'tso_name'] = tso_name
                # drop columns with ego_id
                ehv_ehv_trafos = ehv_ehv_trafos.drop(columns=['bus0', 'bus1'])
                # add ehv/ehv trafos to grid data
                grid_data.components_power.transformers.ehv_ehv = grid_data.components_power.transformers.ehv_ehv.append(ehv_ehv_trafos)
            ehv_hv_trafos = hv_trafos[hv_trafos.voltage_kv_lv == 110]
            ehv_hv_trafos['voltage_level'] = 2
            # add dave name trafo and connection buses
            ehv_hv_trafos.insert(0, 'dave_name', None)
            ehv_hv_trafos.insert(1, 'bus_hv', None)
            ehv_hv_trafos.insert(2, 'bus_lv', None)
            ehv_hv_trafos['tso_name'] = None
            ehv_hv_trafos = ehv_hv_trafos.reset_index(drop=True)
            for i, trafo in ehv_hv_trafos.iterrows():
                ehv_hv_trafos.at[trafo.name, 'dave_name'] = f'trafo_2_{i}'
                # search for bus dave name and replace ego id
                ehv_buses = grid_data.ehv_data.ehv_nodes
                hv_buses = grid_data.hv_data.hv_nodes
                bus0_name = hv_buses[hv_buses.ego_bus_id == trafo.bus0].iloc[0].dave_name
                bus1_name = ehv_buses[ehv_buses.ego_bus_id == trafo.bus1].iloc[0].dave_name
                subst_name = ehv_buses[ehv_buses.ego_bus_id == trafo.bus1].iloc[0].subst_name
                tso_name = ehv_buses[ehv_buses.ego_bus_id == trafo.bus1].iloc[0].tso_name
                ehv_hv_trafos.at[trafo.name, 'bus_lv'] = bus0_name
                ehv_hv_trafos.at[trafo.name, 'bus_hv'] = bus1_name
                ehv_hv_trafos.at[trafo.name, 'substation_name'] = subst_name
                ehv_hv_trafos.at[trafo.name, 'tso_name'] = tso_name
            # change column name
            ehv_hv_trafos = ehv_hv_trafos.drop(columns=['bus0', 'bus1'])
            # add ehv/ehv trafos to grid data
            grid_data.components_power.transformers.ehv_hv = grid_data.components_power.transformers.ehv_hv.append(ehv_hv_trafos)

    # --- create hv/mv trafos
    if 'HV' in grid_data.target_input.power_levels[0] or 'MV' in grid_data.target_input.power_levels[0]:
        # read transformator data from OEP, filter relevant parameters and rename paramter names
        substations = oep_request(schema='grid', 
                                  table='ego_dp_hvmv_substation', 
                                  where='version=v0.4.5',
                                  geometry='polygon')  # take substation polygon to get the full area
        substations = substations.rename(columns={'version': 'ego_version',
                                                  'subst_id': 'ego_subst_id',
                                                  'voltage': 'voltage_kv',
                                                  'ags_0': 'Gemeindeschluessel'})
        substations = substations.drop(columns = ['point', 'polygon', 'power_type', 'substation', 
                                                  'frequency', 'ref', 'dbahn', 'status', 'otg_id', 
                                                  'geom'])
        # filter substations with point as geometry
        drop_substations = []
        for i, sub in substations.iterrows():
            if (type(sub.geometry) == shapely.geometry.point.Point) or (type(sub.geometry) == shapely.geometry.linestring.LineString):
                drop_substations.append(sub.name)
        substations = substations.drop(drop_substations)
        # check for substations in the target area
        substations = gpd.overlay(substations, grid_data.area, how='intersection')
        if not substations.empty:
            remove_columns = grid_data.area.keys().tolist()
            remove_columns.remove('geometry')
            substations = substations.drop(columns=remove_columns)
        # --- prepare hv nodes for the transformers
        # check if the hv already nodes exist, otherwise create them
        if grid_data.hv_data.hv_nodes.empty:
            # --- in this case the missing hv nodes for the transformator must be procured from OEP
            # read hv node data from OpenEnergyPlatform and adapt names
            hv_nodes = oep_request(schema='grid', 
                                   table='ego_pf_hv_bus', 
                                   where='version=v0.4.6',
                                   geometry='geom')
            hv_nodes = hv_nodes.rename(columns={'version': 'ego_version', 
                                                'scn_name': 'ego_scn_name',
                                                'bus_id': 'ego_bus_id',
                                                'v_nom': 'voltage_kv'})
            # filter nodes which are on the hv level, current exsist and within the target area
            hv_nodes = hv_nodes[(hv_nodes.voltage_kv == 110) & 
                                (hv_nodes.ego_scn_name == 'Status Quo')]
            hv_nodes = gpd.overlay(hv_nodes, grid_data.area, how='intersection')
            if not hv_nodes.empty:
                remove_columns = grid_data.area.keys().tolist()
                remove_columns.remove('geometry')
                hv_nodes = hv_nodes.drop(columns=remove_columns)
            hv_nodes['voltage_level'] = 3
            hv_nodes = hv_nodes.drop(columns=(['current_type', 'v_mag_pu_min', 'v_mag_pu_max', 'geom']))
            # add dave name
            hv_nodes.insert(0, 'dave_name', None)
            hv_nodes = hv_buses.reset_index(drop=True)
            for i, bus in hv_nodes.iterrows():
                hv_nodes.at[bus.name, 'dave_name'] = f'node_3_{i}'
        else:
            hv_nodes =  grid_data.hv_data.hv_nodes
        # check for hv nodes within hv/mv substations
        substations_keys = substations.keys().tolist()
        substations_keys.remove('ego_subst_id')
        substations_keys.remove('geometry')
        substations_reduced = substations.drop(columns = (substations_keys))
        hv_nodes = gpd.overlay(hv_nodes, substations_reduced, how='intersection')
        # add relevant hv nodes if they don't exist before
        if grid_data.hv_data.hv_nodes.empty:
            grid_data.hv_data.hv_nodes = grid_data.hv_data.hv_nodes.append(hv_nodes)
        # --- prepare mv nodes for the transformers
        # check for mv nodes within hv/mv substations if they were created in mv topology function
        # Otherwise create missing mv nodes
        if grid_data.mv_data.mv_nodes.empty:
            # --- in this case the missing mv nodes for the transformers must be created
            for i, sub in substations.iterrows():
                mv_node_df = gpd.GeoDataFrame({'ego_version': sub.ego_version,
                                               'voltage_kv': [20],
                                               'voltage_level': [5],
                                               'ego_subst_id': sub.ego_subst_id,
                                               'geometry': [sub.geometry.centroid]})
                grid_data.mv_data.mv_nodes = grid_data.mv_data.mv_nodes.append(mv_node_df)
            # add dave name
            grid_data.mv_data.mv_nodes.insert(0, 'dave_name', None)
            grid_data.mv_data.mv_nodes = grid_data.mv_data.mv_nodes.reset_index(drop=True)
            for i, load in grid_data.mv_data.mv_nodes.iterrows():
                grid_data.mv_data.mv_nodes.at[load.name, 'dave_name'] = f'node_5_{i}'
            mv_nodes = grid_data.mv_data.mv_nodes
        else:
            # check for hv nodes within hv/mv substations
            substations_keys = substations.keys().tolist()
            substations_keys.remove('ego_subst_id')
            substations_keys.remove('geometry')
            substations_reduced = substations.drop(columns = (substations_keys))
            mv_nodes = gpd.overlay(grid_data.mv_data.mv_nodes, substations_reduced, how='intersection')
        # create hv/mv transfromers
        for i, sub in substations.iterrows():
            if sub.ego_subst_id in hv_nodes.ego_subst_id.tolist():
                bus_hv = hv_nodes[hv_nodes.ego_subst_id == sub.ego_subst_id].iloc[0].dave_name
            else:
                # find closest hv node to the substation
                multipoints_hv = MultiPoint(hv_nodes.geometry.tolist())
                nearest_point = shapely.ops.nearest_points(sub.geometry.centroid, multipoints_hv)[1]
                for i, node in hv_nodes.iterrows():
                    if nearest_point == node.geometry:
                        bus_hv = node.dave_name
                        break
            if sub.ego_subst_id in mv_nodes.ego_subst_id.tolist():
                bus_lv = mv_nodes[mv_nodes.ego_subst_id == sub.ego_subst_id].iloc[0].dave_name
            else:
                # find closest mv node to the substation
                multipoints_hv = MultiPoint(hv_nodes.geometry.tolist())
                nearest_point = shapely.ops.nearest_points(sub.geometry.centroid, multipoints_hv)[1]
                for i, node in hv_nodes.iterrows():
                    if nearest_point == node.geometry:
                        bus_hv = node.dave_name
                        break
            trafo_df = gpd.GeoDataFrame({'bus_hv': bus_hv,
                                         'bus_lv': bus_lv,
                                         'voltage_kv_hv': [110],
                                         'voltage_kv_lv': [20],
                                         'voltage_level': [4],
                                         'ego_version': sub.ego_version,
                                         'ego_subst_id': sub.ego_subst_id,
                                         'osm_id': sub.osm_id,
                                         'osm_www': sub.osm_www,
                                         'substation_name': sub.subst_name,
                                         'operator': sub.operator,
                                         'Gemeindeschluessel': sub.Gemeindeschluessel,
                                         'geometry': [sub.geometry.centroid]})
            grid_data.components_power.transformers.hv_mv = grid_data.components_power.transformers.hv_mv.append(trafo_df)
        # add dave name
        grid_data.components_power.transformers.hv_mv.insert(0, 'dave_name', None)
        grid_data.components_power.transformers.hv_mv = grid_data.components_power.transformers.hv_mv.reset_index(drop=True)
        for i, load in grid_data.components_power.transformers.hv_mv.iterrows():
            grid_data.components_power.transformers.hv_mv.at[load.name, 'dave_name'] = f'trafo_4_{i}'

    # --- create mv/lv trafos
    if 'MV' in grid_data.target_input.power_levels[0] or 'LV' in grid_data.target_input.power_levels[0]:
        pass
        # muss noch geschrieben werden


def loads(grid_data):
    """
    This function creates loads by osm landuse polygons in the target area an assigne them to a suitable node
    on the considered voltage level by voronoi analysis
    """
    print('create loads for target area')
    print('----------------------------')
    # define avarage values
    residential_load = 2  # in MW/km²
    industrial_load = 10  # in MW/km²
    commercial_load = 3  # in MW/km²
    # define power_levels
    power_levels = grid_data.target_input.power_levels[0]
    # create loads on grid level 7 (LV)
    if 'LV' in power_levels:
        pass
        # andere funktion als über Landnutzung, aggregation und Voronoi, da direkt den Häusern zuordnen
    elif ('MV' in power_levels) or ('HV' in power_levels) or ('EHV' in power_levels):
        # create loads on grid level 6 (MV/LV)
        if 'MV' in power_levels:
            # In this case the loads are assigned to the nearest mv/lv-transformer
            voronoi_polygons = voronoi(grid_data.components_power.transformers.mv_lv[['dave_name',
                                                                                      'geometry']])
            trafos = grid_data.components_power.transformers.mv_lv
            voltage_level = 6
        # create loads on grid level 4 (HV/MV)
        elif 'HV' in power_levels:
            # In this case the loads are assigned to the nearest hv/mv-transformer
            voronoi_polygons = voronoi(grid_data.components_power.transformers.hv_mv[['dave_name',
                                                                                      'geometry']])
            trafos = grid_data.components_power.transformers.hv_mv
            voltage_level = 4
        # create loads on grid level 2 (EHV/HV)
        elif 'EHV' in power_levels:
            # In this case the loads are assigned to the nearest ehv/hv-transformer
            voronoi_polygons = voronoi(grid_data.components_power.transformers.ehv_hv[['dave_name',
                                                                                       'geometry']])
            trafos = grid_data.components_power.transformers.ehv_hv
            voltage_level = 2
        # --- create loads for the lowest considered voltage level
        intersection = gpd.overlay(grid_data.landuse, voronoi_polygons, how='intersection')
        intersection = intersection.drop(columns=['area_km2'])
        # calculate area from intersected polygons
        intersection_3035 = intersection.to_crs(epsg=3035)  # project landuse to crs with unit in meter
        intersection_area = intersection_3035.area/1E06
        intersection['area_km2'] = intersection_area
        # --- calculate consumption for the diffrent landuses in every single voronoi polygon
        # create list of all diffrent connection transformers
        connection_trafos = intersection.dave_name.tolist()
        trafo_names = []
        for tname in connection_trafos:
            if tname not in trafo_names:
                trafo_names.append(tname)
        trafo_names.sort()
        # iterate trough diffrent transformers and calulate the diffrent landuse consumptions
        for trafo_name in trafo_names:
            # search trafo bus
            trafo_bus_lv = trafos[trafos.dave_name == trafo_name].iloc[0].bus_lv
            landuse_polygons = intersection[intersection.dave_name == trafo_name]
            # categorize landuse polygons and add to grid_data
            for loadtype in ['residential', 'industrial', 'commercial']:
                if loadtype == 'residential':
                    residential_polygons = landuse_polygons[landuse_polygons.landuse == 'residential']
                    area = residential_polygons.area_km2.sum()
                    p_mw = residential_load*area
                elif loadtype == 'industrial':
                    industrial_polygons = landuse_polygons[landuse_polygons.landuse == 'industrial']
                    area = industrial_polygons.area_km2.sum()
                    p_mw = industrial_load*area
                elif loadtype == 'commercial':
                    commercial_polygons = landuse_polygons[landuse_polygons.landuse.isin(['commercial', 'retail'])]
                    area = commercial_polygons.area_km2.sum()
                    p_mw = commercial_load*area
                if p_mw != 0:
                    load_df = gpd.GeoDataFrame({'bus': trafo_bus_lv,
                                                'p_mw': p_mw,
                                                'landuse': loadtype,
                                                'trafo_name': trafo_name,
                                                'area_km2': area,
                                                'voltage_level': [voltage_level]})
                grid_data.components_power.loads = grid_data.components_power.loads.append(load_df)
    # add dave name
    grid_data.components_power.loads.insert(0, 'dave_name', None)
    grid_data.components_power.loads = grid_data.components_power.loads.reset_index(drop=True)
    for i, load in grid_data.components_power.loads.iterrows():
        grid_data.components_power.loads.at[load.name, 'dave_name'] = f'load_{load.voltage_level}_{i}'


def power_components(grid_data):
    # add transformers
    transformators(grid_data)
    # add renewable powerplants
    renewable_powerplants(grid_data)
    # add conventional powerplants
    conventional_powerplants(grid_data)
    # create lines for power plants with a grid node far away
    power_plant_lines(grid_data)
    # add loads
    loads(grid_data)
