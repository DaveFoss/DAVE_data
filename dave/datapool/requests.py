import geopandas as gpd
import pandas as pd
import shapely
import requests

from dave.settings import dave_settings


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
    oep_url = 'http://oep.iks.cs.ovgu.de/'
    if where:
        request = requests.get(''.join([oep_url,'/api/v0/schema/',schema,'/tables/',table,'/rows/?where=',where]))
    else:
        request = requests.get(''.join([oep_url,'/api/v0/schema/',schema,'/tables/',table,'/rows/']))
    # convert data to dataframe
    if request.status_code == 200:  # 200 is the code of a successful request
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
        request_data['geometry'] = request_data[geometry].apply(
            lambda x: shapely.wkb.loads(x, hex=True))
        # create geoDataFrame
        request_data = gpd.GeoDataFrame(request_data,
                                        crs=dave_settings()['crs_main'],
                                        geometry=request_data.geometry)

    # --- request meta informations for a dataset
    request = requests.get(''.join([oep_url,'/api/v0/schema/',schema,'/tables/',table,'/meta/']))
    # convert data to meta dict
    if request.status_code == 200:  # 200 is the code of a successful request
        request_meta = request.json()
        # get region
        if request_meta['spatial']['location']:
            region = request_meta['spatial']['location']
        elif 'extent' in request_meta['spatial'].keys():
            region = request_meta['spatial']['extent']
        elif 'extend' in request_meta['spatial'].keys():
            region = request_meta['spatial']['extend']
        else:
            region = None
        # get meta version
        if 'metadata_version' in request_meta.keys():
            meta_version = request_meta['metadata_version']
        elif 'meta_version' in request_meta.keys():
            meta_version = request_meta['meta_version']
        # create dict
        meta_data = {'Main': pd.DataFrame({'Titel': request_meta['title'],
                                           'Description': request_meta['description'],
                                           'Region': region,
                                           'License': request_meta['license']['id'],
                                           'License_url': request_meta['license']['url'],
                                           'copyright': request_meta['license']['copyright'],
                                           'metadata_version': meta_version},
                                          index=[0]),
                     'Sources': pd.DataFrame(request_meta['sources']),
                     'Data': pd.DataFrame(request_meta['resources'][0]['fields'])}
    else:
        meta_data = pd.DataFrame()
    return request_data, meta_data
