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
        conv_powerplants = requests.get(oep_url+'/api/v0/schema/'+schema+'/tables/'+table+'/rows/?where='+where, )
    else:
        conv_powerplants = requests.get(oep_url+'/api/v0/schema/'+schema+'/tables/'+table, )
    # convert data to dataframe
    request_data = pd.DataFrame(conv_powerplants.json())
    return request_data

def renewable_powerplants(target_input, area=None):
    """
    This function collects the generators based on renewable enrgies and 
    assign them their exact location by adress, if these are available
    """
    typ = target_input.typ.iloc[0]
    if typ in ['postalcode', 'federal state', 'own area']:
        for plz in target_input.data.iloc[0]:
            where = f'postcode={plz}'
            data = oep_request(schema='supply', table='ego_renewable_powerplant', where=where)
            if plz == target_input.data.iloc[0][0]: 
                renewables = data
            else: 
                renewables = renewables.append(data)
        # bei fedaral state noch schauen ob ich dazu schon die plz raussuche oder nicht
        
        
    elif typ == 'town name':
        for name in target_input.data.iloc[0]:
            where = f'city={name}'
            data = oep_request(schema='supply', table='ego_renewable_powerplant', where=where)
            if name == target_input.data.iloc[0][0]: 
                renewables = data
            else: 
                renewables = renewables.append(data)
    # prepare the DataFrame of the renewable plants
    renewables = renewables.drop(columns=['id', 'gps_accuracy', 'geom'])
    renewables['lon'] = renewables['lon'].astype(float)
    renewables['lat'] = renewables['lat'].astype(float)
    # find exact location by adress
    geolocator = ArcGIS(timeout=10000)  # set on None when geopy 2.0 was released
    for i, plant in renewables.iterrows():
        address = str(plant.address)+' ' + str(plant.postcode)+' '+str(plant.city)
        location = geolocator.geocode(address)
        renewables.at[i,'lon'] = location.longitude
        renewables.at[i,'lat'] = location.latitude   
    
    # convert DataFrame into a GeoDataFrame
    renewables_geo = gpd.GeoDataFrame(renewables, geometry=gpd.points_from_xy(
                                      renewables.lon, renewables.lat))
    # intersection of power plants with target_area when target is an own shape file
    if typ == 'own area':
        renewables_geo = gpd.overlay(renewables_geo, area, how='intersection')
        
        
        
    return renewables_geo


def conventional_powerplants():
    pass

def transformators():
    pass

def loads():
    pass


def power_components(grid_data):
    # hier die einzelnen Komponenten über die einzelenen skripte bestimmen und zu dem Grid Data dict hinzufügen
    
    # create dict for components in the grid data
    grid_data['components']={}
    # add renewable powerplants
    renewable_data = renewable_powerplants(target_input = grid_data['target_input'],
                                           area = grid_data['area'])
    grid_data['components']['renewable_powerplants'] = renewable_data
    
    
    return grid_data
    
    