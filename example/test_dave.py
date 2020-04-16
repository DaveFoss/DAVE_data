# must import:
import os
import timeit

#from dave.create import create_grid
from dave.topology import target_area
from dave.plotting import plot_target_area, plot_grid_data
from dave.topology import create_lv_topology, create_hv_topology, create_ehv_topology
from dave.model import create_power_grid
from dave.components import power_components
from dave import create_empty_dataset
from dave.datapool import oep_request



# imports for tests:
#from dave import dave_dir
#import dave.datapool as data
from dave.datapool import read_ehv_data
import geopandas as gpd
import geopandas_osm.osm
import matplotlib.pyplot as plt
import shapely.geometry
import shapely.ops
from shapely.ops import cascaded_union, nearest_points
from shapely.geometry import Point, MultiPoint
import pandas as pd
import pandapower.plotting as pplt
import requests
from geopy.geocoders import ArcGIS
import numpy as np


"""
This is a example file for testing dave
"""

# start runtime
_start_time = timeit.default_timer()

from dave.create import create_grid

########## testing Input Settings #########################
# test target by plz
_postalcode_1=['34225']
_postalcode_2=['34225', '34311']
_postalcode_3=['ALL']

# test target by town_name
_town_name_1=['Baunatal']
_town_name_2=['KAsSel', 'Baunatal']
_town_name_3=['ALL']

# test target by federal state
_federal_state_1=['Hessen']
_federal_state_2=['HeSsEn', 'SchleSWIg-HOLstein']
_federal_state_3=['ALL']


# test own shape (Hertingshausen is a part from the Town Baunatal). 
# It has 500 relevant Buildings(for living and commercial))
_own_area = os.path.dirname(os.path.realpath(__file__))+'\\hertingshausen\\hertingshausen.shp'


##################### test with main function ##########################
"""
grid_data= create_grid(postalcode=None, 
                       town_name=None, 
                       federal_state=None, 
                       own_area=_own_area,
                       power_levels=['LV'], 
                       gas_levels=[], 
                       plot=True, 
                       convert = False)
"""
"""
grid_data= create_grid(postalcode=None, 
                       town_name=None, 
                       federal_state=_federal_state_3, 
                       own_area=None,
                       power_levels=['EHV', 'HV'], 
                       gas_levels=[], 
                       plot=False, 
                       convert = False)
"""
###################### Test manuel ##########################################
"""
# create empty datastructure
grid_data = create_empty_dataset()

# create target area
target_area(grid_data, own_area=_path, buffer=0).target()

# plot target area
plot_target_area(grid_data=grid_data)


# ---create low voltage topology:
create_lv_topology(grid_data=grid_data)

# --- create power components:
power_components(grid_data)

# plot target area with grid data
plot_grid_data(grid_data=grid_data)

# ---create pandapower model
power_grid = create_power_grid(grid_data)

# plotting testweise, später mal selbst richtig machen mit angepassten farben usw. 
#pplt.simple_plot(power_grid, line_width=1.5, bus_size=0.15)

"""


############# test ehv  level ##############
"""

# test ehv level:
# create empty datastructure
grid_data = create_empty_dataset()
# test target by federal state
target_area(grid_data, federal_state=['ALL'], roads=False, roads_plot=False, buildings=False, landuse=False, power_levels = ['ALL']).target()
# plot target area
#plot_target_area(grid_data=grid_data)
# create extra high voltage topology:
if 'EHV' in grid_data.target_input.power_levels[0]:
    create_ehv_topology(grid_data=grid_data)
# create high voltage topology:
if 'HV' in grid_data.target_input.power_levels[0]:
    create_hv_topology(grid_data=grid_data)
# plot target area with grid data
plot_grid_data(grid_data=grid_data)

# create power components:
power_components(grid_data)

# ---create pandapower model
net = create_power_grid(grid_data)

"""

################# test mv/lv trafos ##########################
"""
# ---test mv/lv trafos openego
# oedb
oep_url= 'http://oep.iks.cs.ovgu.de/'

# select opsd renewable power plants
schema='grid'
table='ego_dp_mvlv_substation'
where = 'version=v0.2.8'  

trafo = requests.get(oep_url+'/api/v0/schema/'+schema+'/tables/'+table+'/rows/?where='+where, )
trafo.status_code

# convert to dataframe
df_pp = pd.DataFrame(trafo.json())

# --- convert to geopandas with right crs
# transform WKB to WKT / Geometry
df_pp['geom'] = df_pp['geom'].apply(lambda x:shapely.wkb.loads(x, hex=True))
# create geoDataFrame
crs = {'init' :'epsg:3035'}
gdf_pp = gpd.GeoDataFrame(df_pp, crs=crs, geometry=df_pp.geom)
gdf_pp_4326 = gdf_pp.to_crs(epsg=4326)
# filter trafos for target area
trafo_intersection = gpd.overlay(gdf_pp_4326, target_area['area'], how='intersection').geometry
"""

################## test create ehv topology #################
"""
# ehv substations
ehv_substations = oep_request(schema='grid', 
                              table='ego_dp_ehv_substation', 
                              where='version=v0.4.5',
                              geometry='polygon')
ehv_substations = ehv_substations.rename(columns={'version': 'ego_version', 
                                                  'subst_id': 'ego_subst_id',
                                                  'voltage': 'voltage_kv'})

# ehv nodes
ehvhv_buses = oep_request(schema='grid', 
                          table='ego_pf_hv_bus', 
                          where='version=v0.4.6',
                          geometry='geom')
ehvhv_buses = ehvhv_buses.rename(columns={'version': 'ego_version', 
                                          'scn_name': 'ego_scn_name',
                                          'bus_id': 'ego_bus_id',
                                          'v_nom': 'voltage_kv'})
# filter nodes their on the ehv level
ehv_buses = ehvhv_buses[(ehvhv_buses.voltage_kv.isin([380, 220])) & (ehvhv_buses.ego_scn_name == 'Status Quo')]
# search for the substations where the ehv nodes are within
for i, bus in ehv_buses.iterrows():
    for j, sub in ehv_substations.iterrows():
        if bus.geometry.within(sub.geometry):
            ehv_buses.at[bus.name, 'ego_subst_id'] = sub.ego_subst_id
            ehv_buses.at[bus.name, 'subst_name'] = sub.subst_name
            break

# read ehv tso data
ehv_data = read_ehv_data()
# search for the nearest point for each tso ehv node in ego ehv nodes
for i, node in ehv_data['ehv_nodes'].iterrows():
    if node.osm_id:
        # search for the matching ego ehv substation
        node_osm_id = 'w'+node.osm_id
        substation = ehv_substations[ehv_substations.osm_id == node_osm_id]
        if not substation.empty:
            substation_id = ehv_substations[ehv_substations.osm_id == node_osm_id].iloc[0].ego_subst_id
            ehv_buses_index = ehv_buses[ehv_buses.ego_subst_id == substation_id].index
            for index in ehv_buses_index:
                ehv_buses.at[index, 'tso_name'] = node['name'].replace('_380','').replace('_220','')
                ehv_buses.at[index, 'tso'] = node['tso']
    else:
        # search for tso connection points in ego ehv nodes
        for j, bus in ehv_buses.iterrows():
            distance = node.geometry.distance(bus.geometry)
            if distance < 2E-03:
                ehv_buses.at[bus.name, 'tso_name'] = node['name']
                ehv_buses.at[bus.name, 'tso'] = node['tso']
                break
       
# create ehv lines
ehv_lines = oep_request(schema='grid', 
                        table='ego_pf_hv_line', 
                        where='version=v0.4.6',
                        geometry='geom')
ehv_lines = ehv_lines.rename(columns={'version': 'ego_version', 
                                      'subst_id': 'ego_subst_id',
                                      'scn_name': 'ego_scn_name',
                                      'line_id': 'ego_line_id'})
# filter lines which are on the ehv level by check if both endpoints on the ehv level
ehv_bus_ids = ehv_buses.ego_bus_id.tolist()
ehv_lines = ehv_lines[(ehv_lines.bus0.isin(ehv_bus_ids)) & 
                      (ehv_lines.bus1.isin(ehv_bus_ids)) & 
                      (ehv_lines.ego_scn_name == 'Status Quo')]
# search for line voltage
for i, line in ehv_lines.iterrows():
    ehv_bus_index = ehv_buses[ehv_buses.ego_bus_id == line.bus0].index[0]
    ehv_lines.at[line.name, 'voltage_kv'] = ehv_buses.loc[ehv_bus_index].voltage_kv
"""


######################## test create hv topology #######################
"""
# hv nodes
ehvhv_buses = oep_request(schema='grid', 
                          table='ego_pf_hv_bus', 
                          where='version=v0.4.6',
                          geometry='geom')
ehvhv_buses = ehvhv_buses.rename(columns={'version': 'ego_version', 
                                          'scn_name': 'ego_scn_name',
                                          'bus_id': 'ego_bus_id',
                                          'v_nom': 'voltage_kv'})
# filter nodes which are on the hv level and current exist
hv_buses = ehvhv_buses[(ehvhv_buses.voltage_kv == 110) & (ehvhv_buses.ego_scn_name == 'Status Quo')]

        
# create hv lines
hv_lines = oep_request(schema='grid', 
                        table='ego_pf_hv_line', 
                        where='version=v0.4.6',
                        geometry='geom')
hv_lines = hv_lines.rename(columns={'version': 'ego_version', 
                                     'subst_id': 'ego_subst_id',
                                     'scn_name': 'ego_scn_name',
                                     'line_id': 'ego_line_id'})
# filter lines which are on the hv level by check if both endpoints on the hv level
hv_bus_ids = hv_buses.ego_bus_id.tolist()
hv_lines = hv_lines[(hv_lines.bus0.isin(hv_bus_ids)) & 
                    (hv_lines.bus1.isin(hv_bus_ids)) & 
                    (hv_lines.ego_scn_name == 'Status Quo')]
"""
  
#################### Test renewables ####################

# create empty datastructure
grid_data = create_empty_dataset()
# create target_area

target_area(grid_data, power_levels=['EHV'], gas_levels=[], 
                    federal_state=_federal_state_3, 
                    buffer=0, roads=False, roads_plot=False, 
                    buildings=False, landuse=False).target()
#create_ehv_topology(grid_data)
#create_hv_topology(grid_data)

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
    # find exact location by adress
    if ('LV' in grid_data.target_input.power_levels[0]) or ('MV' in grid_data.target_input.power_levels[0]):
        geolocator = ArcGIS(timeout=10000)  # set on None when geopy 2.0 was released
        plant_georefernce = renewables[renewables.voltage_level>=5]
        for i, plant in plant_georefernce.iterrows():
            # find exact address for renewables which are on the medium voltage or on a lowerlevel  
            if plant.address:
                address = str(plant.address)+' ' + str(plant.postcode)+' '+str(plant.city)
                location = geolocator.geocode(address)
                renewables.at[plant.name,'lon'] = location.longitude
                renewables.at[plant.name,'lat'] = location.latitude
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
    renewables_lv['connection_bus'] = None
    renewables_mv_lv = renewables_geo[renewables_geo.voltage_level==6]
    renewables_mv_lv['connection_bus'] = None
    renewables_mv = renewables_geo[renewables_geo.voltage_level==5]
    renewables_mv['connection_bus'] = None
    renewables_hv_mv = renewables_geo[renewables_geo.voltage_level==4]
    renewables_hv_mv['connection_bus'] = None
    renewables_hv = renewables_geo[renewables_geo.voltage_level==3]
    renewables_hv['connection_bus'] = None
    renewables_ehv_hv = renewables_geo[renewables_geo.voltage_level==2]
    renewables_ehv_hv['connection_bus'] = None
    renewables_ehv = renewables_geo[renewables_geo.voltage_level==1]
    renewables_ehv['connection_bus'] = None
    
    if 'LV' in grid_data.target_input.power_levels[0]:
            # In this case the Level 7 plants are assign to the nearest lv node
            lv_grid_nodes = grid_data.lv_data.lv_nodes.building_connections.building_centroid.append(grid_data.lv_data.lv_nodes.building_connections.nearest_point) 
            lv_grid_nodes_points = MultiPoint(list(lv_grid_nodes))
            for i, plant in renewables_lv.iterrows():
                nearest_node = nearest_points(plant.geometry, lv_grid_nodes_points)[1]
                renewables_lv.at[plant.name, 'connection_bus'] = nearest_node
            # hier müsste theoretisch noch berücksichtigt werden das bio anlagen nicht einem hausknoten zugeordnet werden (also nearest road analyse)
            # außerdem müsste bei weiten distancen eine Leitung gezogen werden
            grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(renewables_lv)
    # find next higher and considered voltage level to assigne the lv-plants
    elif 'MV' in grid_data.target_input.power_levels[0]:
        pass
        #In diesem Fall die Erzeuger mittels voronoi und Aggregation den MV/LV TRafos zuordnen
    elif 'HV' in grid_data.target_input.power_levels[0]:
        pass
        # In diesem Fall die Erzeuger mittels voronoi und Aggregation den HV/MV TRafos zuordnen
    elif 'EHV' in grid_data.target_input.power_levels[0]:
        pass
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
                # In diesem Fall hat die Anlage keine Koordinaten. (Bei EHV 21 ANlagen, die alle an UW Bentwisch gehen) 
                # Überlegen wie man ihr dennoch einen Knoten zuordnen könnte
        grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(renewables_ehv)

# die zuteilung zu den grid_data über append für die Anlagen der verschiedenen Ebenen nachdem ein Knoten zugewieden wurde
#grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(renewables_geo)
    
"""


# stop and show runtime
_stop_time = timeit.default_timer()
print('runtime = ' + str(round((_stop_time - _start_time)/60,2)) + 'min')
