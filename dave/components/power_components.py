import geopandas as gpd
import pandas as pd
from geopy.geocoders import ArcGIS
from shapely.geometry import Point, MultiPoint
from shapely.ops import nearest_points
import numpy as np


from dave.datapool import oep_request
from dave.voronoi import voronoi

def aggregate_plants(grid_data, plants_aggr):
    """
    This function aggregates power plants with the same energy source which are connected to the same trafo
    
    INPUT:
        **grid_data** (dict) - all Informations about the target area
        **plants_aggr** (DataFrame) - all power plants that sould be aggregate after voronoi analysis
    """
    # create list of all diffrent connection transformers
    connection_trafos = plants_aggr.connection_trafo_dave_name.tolist()
    trafo_names = []
    for tname in connection_trafos:
        if tname not in trafo_names:
            trafo_names.append(tname)
    trafo_names.sort()
    # iterate through the trafo_names to aggregate the power plants with the same energy source
    energy_sources = ['biomass', 'gas','hydro', 'solar', 'wind']
    for trafo_name in trafo_names:
        plants_area = plants_aggr[plants_aggr.connection_trafo_dave_name == trafo_name]
        for esource in energy_sources:
            plant_esource = plants_area[plants_area.generation_type == esource]
            if not plant_esource.empty:
                sources = plant_esource.source.tolist()
                sources_diff = []
                for source in sources:
                    if source not in sources_diff:
                        sources_diff.append(source)
                plant_power = pd.to_numeric(plant_esource.electrical_capacity_kw, downcast='float')
                plant_df = gpd.GeoDataFrame({'aggregated': 'level 7 plants',  
                                             'electrical_capacity_kw': plant_power.sum(),
                                             'generation_type': esource,
                                             'voltage_level': plant_esource.voltage_level.iloc[0],
                                             'source': [sources_diff],
                                             'geometry': [plant_esource.connection_node.iloc[0]],
                                             'connection_trafo_dave_name': plant_esource.connection_trafo_dave_name.iloc[0]})
                grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(plant_df)
            

def renewable_lines(grid_data):
    pass
    """
    Diese Funktion soll schauen wie weit die für jede Anlage zugeordneten Knoten weg sind
    und wenn das recht lang ist dann eine LEitung erstellen und einen KNoten für die Anlage
    und in die grid_Data schreiben
    
    Das gilt nicht für aggregierte Anlagen, da bei diesen Angenommen wird, dass
    sie direkt an dem UW sitzen
    """

def renewable_powerplants(grid_data):
    # hier muss noch eine Fallunterscheidung gemacht werden, welche Spannungsebene in den inzput daten gewählt wurden
    # Das evt mit einem Case PArameter machen der dann der Funktion übergeben wird
    # Je nach dem müssen einige Erzeuger dann aggregiert werden
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
            renewables = renewables[renewables.voltage_level>=3]
        elif 'MV' in grid_data.target_input.power_levels[0]:
            renewables = renewables[renewables.voltage_level>=5]
        elif 'LV' in grid_data.target_input.power_levels[0]:
            renewables = renewables[renewables.voltage_level==7]
        # find exact location by adress for renewable power plants which are on mv-level or lower 
        if ('LV' in grid_data.target_input.power_levels[0]) or ('MV' in grid_data.target_input.power_levels[0]):
            geolocator = ArcGIS(timeout=10000)  # set on None when geopy 2.0 was released
            plant_georefernce = renewables[renewables.voltage_level>=5]
            for i, plant in plant_georefernce.iterrows():
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
            renewables_geo = gpd.overlay(renewables_geo, grid_data.area, how='intersection')
        # --- node assignment with case distinction depending on considered power levels
        # divide the plants in the target area according to their voltage level
        renewables_lv = renewables_geo[renewables_geo.voltage_level==7]
        renewables_mv_lv = renewables_geo[renewables_geo.voltage_level==6]
        renewables_mv = renewables_geo[renewables_geo.voltage_level==5]
        renewables_hv_mv = renewables_geo[renewables_geo.voltage_level==4]
        renewables_hv = renewables_geo[renewables_geo.voltage_level==3]
        renewables_ehv_hv = renewables_geo[renewables_geo.voltage_level==2]
        renewables_ehv = renewables_geo[renewables_geo.voltage_level==1]
        
        # nodes for level 7 plants (LV)
        if 'LV' in grid_data.target_input.power_levels[0]:
            # In this case the Level 7 plants are assign to the nearest lv node
            voronoi_polygons = voronoi(grid_data.lv_data.lv_nodes[['dave_name', 'geometry']])
            intersection = gpd.sjoin(renewables_lv, voronoi_polygons, how='inner', op='intersects')
            intersection = intersection.drop(columns=['index_right'])
            intersection = intersection.rename(columns={'centroid': 'connection_node', 
                                                        'dave_name': 'connection_node_dave_name'})
            grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(intersection)
            
            # hier müsste theoretisch noch berücksichtigt werden das bio anlagen nicht einem hausknoten zugeordnet werden (also nearest road analyse)
            # außerdem müsste bei weiten distancen eine Leitung gezogen werden
            
        # find next higher and considered voltage level to assigne the lv-plants
        elif 'MV' in grid_data.target_input.power_levels[0]:
            pass
            #In diesem Fall die Erzeuger mittels voronoi und Aggregation den MV/LV TRafos zuordnen
        elif 'HV' in grid_data.target_input.power_levels[0]:
            pass
            # In diesem Fall die Erzeuger mittels voronoi und Aggregation den HV/MV TRafos zuordnen
        elif 'EHV' in grid_data.target_input.power_levels[0]:
            voronoi_polygons = voronoi(grid_data.components_power.transformers.ehv_hv.geometry)
            intersection = gpd.sjoin(renewables_lv, voronoi_polygons, how='inner', op='intersects')
            intersection = intersection.rename(columns={'index_right': 'voronoi_id',
                                                        'centroid': 'conection_bus'})
            # change voltage level to the new connection level
            intersection.voltage_level = 2
            # aggregate power plants within a voronoi area
            
            # hier alle voronoi index in eine liste
            # dann über die liste iterrieren
            
            # alternativ und besser geht es über pandas groupby und agg = sum
            plants_aggregated = aggregate_plants(intersection)
            
            #Aggregieren und mit den informationen dem erzeuger df zuweisen
            
            
            # In diesem Fall die Erzeuger mittels voronoi und Aggregation den EHV/HV TRafos zuordnen

        # nodes for level 6 plants (MV/LV)
        if ('LV' in grid_data.target_input.power_levels[0]) or ('MV' in grid_data.target_input.power_levels[0]):
            pass
            #In diesem Fall die Erzeuger mittels voronoi den MV/LV TRafos zuordnen
        elif 'HV' in grid_data.target_input.power_levels[0]:
            pass
            # In diesem Fall die Erzeuger mittels voronoi und Aggregation den HV/MV TRafos zuordnen
        elif 'EHV' in grid_data.target_input.power_levels[0]:
            pass
            # In diesem Fall die Erzeuger mittels voronoi und Aggregation den EHV/HV TRafos zuordnen

        # nodes for level 5 plants (MV)
        if 'MV' in grid_data.target_input.power_levels[0]:
            pass
            #In diesem Fall die Erzeuger dem nächsten MV KNoten zuordnen
        elif 'HV' in grid_data.target_input.power_levels[0]:
            pass
            # In diesem Fall die Erzeuger mittels voronoi und Aggregation den HV/MV TRafos zuordnen
        elif 'EHV' in grid_data.target_input.power_levels[0]:
            pass
            # In diesem Fall die Erzeuger mittels voronoi und Aggregation den EHV/HV TRafos zuordnen
                    
        # nodes for level 4 plants (HV/MV)
        if ('MV' in grid_data.target_input.power_levels[0]) or ('HV' in grid_data.target_input.power_levels[0]):
            pass
            #In diesem Fall die Erzeuger mittels voronoi den HV/MV TRafos zuordnen
        elif 'EHV' in grid_data.target_input.power_levels[0]:
                pass
                # In diesem Fall die Erzeuger mittels voronoi und Aggregation den EHV/HV TRafos zuordnen
                    
        # nodes for level 3 plants (HV)
        if 'HV' in grid_data.target_input.power_levels[0]:
            # In this case the Level 3 plants are assign to the nearest hv node
            hv_grid_nodes = grid_data.hv_data.hv_nodes.geometry
            hv_grid_nodes_points = MultiPoint(list(hv_grid_nodes))
            for i, plant in renewables_hv.iterrows():
                # check if plant has geocoordinates
                if not np.isnan(plant.geometry.coords[:][0][0]):
                    nearest_node = nearest_points(plant.geometry, hv_grid_nodes_points)[1]
                    renewables_hv.at[plant.name, 'connection_bus'] = nearest_node
                    # check for the hv bus id
                    for j, node in grid_data.hv_data.hv_nodes.iterrows():
                        if nearest_node.coords[:] == node.geometry.coords[:]:
                            renewables_hv.at[plant.name, 'ego_bus_id'] = node.ego_bus_id
                            break
                else:
                    pass
                    # In diesem Fall hat die Anlage keine Koordinaten. (Bei HV 14 ANlagen, die an 'Markt Beratzhausen' und 'Sydower Fließ OT Tempelfelde' gehen) 
                    # Überlegen wie man ihr dennoch einen Knoten zuordnen könnte
            grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(renewables_hv)
        elif 'EHV' in grid_data.target_input.power_levels[0]:
                pass
                # In diesem Fall die Erzeuger mittels voronoi und Aggregation den EHV/HV TRafos zuordnen
                    
        # nodes for level 2 plants (EHV/HV)
        if ('HV' in grid_data.target_input.power_levels[0]) or ('EHV' in grid_data.target_input.power_levels[0]):
            pass
            # #In diesem Fall die Erzeuger mittels voronoi den EHV/HV TRafos zuordnen

        # nodes for level 1 plants (EHV)
        if 'EHV' in grid_data.target_input.power_levels[0]:
            # In this case the Level 1 plants are assign to the nearest ehv node
            ehv_grid_nodes = grid_data.ehv_data.ehv_nodes.geometry
            ehv_grid_nodes_points = MultiPoint(list(ehv_grid_nodes))
            for i, plant in renewables_ehv.iterrows():
                # check if plant has geocoordinates
                if not np.isnan(plant.geometry.coords[:][0][0]):
                    nearest_node = nearest_points(plant.geometry, ehv_grid_nodes_points)[1]
                    renewables_ehv.at[plant.name, 'connection_bus'] = nearest_node
                    # check for the ehv bus id
                    for j, node in grid_data.ehv_data.ehv_nodes.iterrows():
                        if nearest_node.coords[:] == node.geometry.coords[:]:
                            renewables_ehv.at[plant.name, 'ego_bus_id'] = node.ego_bus_id
                            break
                else:
                    pass
                    # In diesem Fall hat die Anlage keine Koordinaten. 
                    # Überlegen wie man ihr dennoch einen Knoten zuordnen könnte
            grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(renewables_ehv)
        
        # add dave name
        grid_data.components_power.renewable_powerplants.insert(0, 'dave_name', None)
        grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.reset_index(drop=True)
        for i, plant in grid_data.components_power.renewable_powerplants.iterrows():
            grid_data.components_power.renewable_powerplants.at[plant.name, 'dave_name'] = f'ren_powerplant_{voltage_level}_{i}'    

        
        
        
        
        
    # die zuteilung zu den grid_data über append für die Anlagen der verschiedenen Ebenen nachdem ein Knoten zugewieden wurde in den einzelnen Fällen
    #grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(renewables_geo)




def conventional_lines(grid_data):
    pass
    """
    Diese Funktion soll schauen wie weit die für jede Anlage zugeordneten Knoten weg sind
    und wenn das recht lang ist dann eine LEitung erstellen und einen KNoten für die Anlage
    und in die grid_Data schreiben
    
    Das gilt nicht für aggregierte Anlagen, da bei diesen Angenommen wird, dass
    sie direkt an dem UW sitzen
    """

    
def conventional_powerplants(grid_data):
    # hier muss noch eine Fallunterscheidung gemacht werden, welche Spannungsebene in den inzput daten gewählt wurden
    # Das evt mit einem Case PArameter machen der dann der Funktion übergeben wird
    # Je nach dem müssen einige Erzeuger dann aggregiert werden
    """
    This function collects the generators based on ego_conventional_powerplant from OEP
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
    # prepare the DataFrame of the renewable plants
    if not conventionals.empty:
        conventionals = conventionals.reset_index()
        conventionals = conventionals.drop(columns=['gid',
                                                    'geom',
                                                    'index'])
        conventionals.rename(columns={'capacity': 'capacity_mw',
                                      'chp_capacity_uba': 'chp_capacity_uba_mw'})
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
        # restrict plants to considered power levels
        if 'EHV' in grid_data.target_input.power_levels[0]:
            conventionals = conventionals
        elif 'HV' in grid_data.target_input.power_levels[0]:
            conventionals = conventionals[conventionals.voltage_level>=3]
        elif 'MV' in grid_data.target_input.power_levels[0]:
            conventionals = conventionals[conventionals.voltage_level>=5]
        elif 'LV' in grid_data.target_input.power_levels[0]:
            conventionals = conventionals[conventionals.voltage_level==7]
        # convert DataFrame into a GeoDataFrame
        conventionals_geo = gpd.GeoDataFrame(conventionals, 
                                             crs = 'EPSG:4326',
                                             geometry=gpd.points_from_xy(
                                                     conventionals.lon, conventionals.lat))
        # intersection of power plants with target_area when target is an own area
        if typ == 'own area':
            conventionals_geo = gpd.overlay(conventionals_geo, grid_data.area, how='intersection')

    grid_data.components_power.conventional_powerplants = grid_data.components_power.conventional_powerplants.append(conventionals_geo)

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
        if not hv_trafos.empty:                        
            if 'EHV' in grid_data.target_input.power_levels[0]:
                ehv_ehv_trafos = hv_trafos[hv_trafos.voltage_kv_us.isin([380, 220])]
                ehv_ehv_trafos['voltage_level'] = 1
                # add dave name
                ehv_ehv_trafos.insert(0, 'dave_name', None)
                ehv_ehv_trafos = ehv_ehv_trafos.reset_index(drop=True)
                for i, trafo in ehv_ehv_trafos.iterrows():
                    ehv_ehv_trafos.at[trafo.name, 'dave_name'] = f'trafo_1_{i}'
                # add ehv/ehv trafos to grid data
                grid_data.components_power.transformers.ehv_ehv = grid_data.components_power.transformers.ehv_ehv.append(ehv_ehv_trafos)
            ehv_hv_trafos = hv_trafos[hv_trafos.voltage_kv_us == 110]
            ehv_hv_trafos['voltage_level'] = 2
            # add dave name
            ehv_hv_trafos.insert(0, 'dave_name', None)
            ehv_hv_trafos = ehv_hv_trafos.reset_index(drop=True)
            for i, trafo in ehv_hv_trafos.iterrows():
                ehv_hv_trafos.at[trafo.name, 'dave_name'] = f'trafo_2_{i}'
            # add ehv/ehv trafos to grid data
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
    transformators(grid_data)
    #""" rausnehmen für Spannungsebenen größer LV solange noch keine Unterteilung/aggregation da ist, da es sonst sehr lange dauert
    # add renewable powerplants
    #renewable_powerplants(grid_data)
    # add conventional powerplants
    #conventional_powerplants(grid_data)
    #"""
    # add transformers
    
    