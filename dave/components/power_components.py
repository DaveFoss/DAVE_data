import pandas as pd
import geopandas as gpd
import requests
from geopy.geocoders import ArcGIS


def oep_request(schema, table, where=None):
    """
    This function is to requesting data from the open energy platform.
    The available data is to find on https://openenergy-platform.org/dataedit/schemas
    
    INPUT:
        **schema** (string) - schema name of the searched data
        **table** (string) - table name of the searched data 
    
    OPTIONAL:
        **where** (string) - filter the table of the searched data
                             example: 'postcode=34225'
    
    OUTPUT:
        **requested_data** (DataFrame) - table of the requested data
        
    """ 
    oep_url= 'http://oep.iks.cs.ovgu.de/'
    if where:
        request = requests.get(oep_url+'/api/v0/schema/'+schema+'/tables/'+table+'/rows/?where='+where, )
    else:
        request = requests.get(oep_url+'/api/v0/schema/'+schema+'/tables/'+table, )
    # convert data to dataframe
    if request.status_code == 200:  #200 is the code of a successful request
        # if request is empty their will be an JSONDecodeError
        try:
            request_data = pd.DataFrame(request.json())
        except:
            request_data = pd.DataFrame()
    else: 
        request_data = pd.DataFrame()
    return request_data

def renewable_powerplants(target_input, area=None):
    """
    This function collects the generators based on renewable enrgies from OEP 
    and assign them their exact location by adress, if these are available
    """
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
    """
    This function collects the generators based on conventional enrgies from OEP
    """
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






def transformators():
    pass

def loads():
    pass


def power_components(grid_data):
    print('create power components for target area')
    print('---------------------------------------')
    # add renewable powerplants
    renewable_data = renewable_powerplants(target_input = grid_data.target_input,
                                           area = grid_data.area)
    grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(renewable_data)
    # add conventional powerplants
    conventional_data = conventional_powerplants(
            target_input = grid_data.target_input, area = grid_data.area)
    grid_data.components_power.conventional_powerplants = grid_data.components_power.conventional_powerplants.append(conventional_data)

    
    