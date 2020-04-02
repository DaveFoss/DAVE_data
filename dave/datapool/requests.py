import geopandas as gpd
import pandas as pd
import requests
import shapely

from dave import dave_dir


def oep_request(schema, table, where=None, geometry=None):
    """
    This function is to requesting data from the open energy platform.
    The available data is to find on https://openenergy-platform.org/dataedit/schemas
    
    INPUT:
        **schema** (string) - schema name of the searched data
        **table** (string) - table name of the searched data 
    
    OPTIONAL:
        **where** (string) - filter the table of the searched data
                             example: 'postcode=34225'
        **geometry** (string) - name of the geometry parameter in the OEP dataset
                                to transform it from WKB to WKT
    
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
    if geometry:
        # --- convert into geopandas DataFrame with right crs
        # transform WKB to WKT / Geometry
        request_data['geometry'] = request_data[geometry].apply(lambda x:shapely.wkb.loads(x, hex=True))
        # create geoDataFrame
        request_data = gpd.GeoDataFrame(request_data,
                                        crs='EPSG:4326',
                                        geometry=request_data.geometry)
    return request_data