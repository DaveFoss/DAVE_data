import os
import geopandas as gpd
import pandas as pd

from dave import dave_dir

def _get_data_path(filename=None, dirname=None):
    """
    This function returns the full os path for a given directory (and filename)
    """
    if filename:
        return os.path.join(dave_dir, 'datapool', dirname, filename)
    else:
        return os.path.join(dave_dir, 'datapool', dirname)
# test
def read_postal():
    """
    This data includes the town name, the area, the population and the 
    geometry for all german postalcode areas

    OUTPUT:
         **postal areas** (GeodataFrame) - all german postalcode areas 

    EXAMPLE:
         import dave.datapool as data

         postal = data.read_postal()
    """
    postalger = gpd.read_file(_get_data_path('postalger.shp', 'postalger'))
    return postalger

def read_federal_states():
    """
    This data includes the name, the length, the area, the population and the 
    geometry for all german federal states

    OUTPUT:
         **federal_statess** (GeodataFrame) - all german federal states 

    EXAMPLE:
         import dave.datapool as data

         postal = data.read_federal_states()
    """
    federalstatesger = gpd.read_file(_get_data_path('federalstatesger.shp',
                                                    'federalstatesger'))
    return federalstatesger

def read_ehv_data():
    """
    This data includes the node, line and transformer informations for the 
    german extra high voltage level based of the data from the four german tso
    
    OUTPUT:
         **extra high voltage data** (dict) - Informations from the german tso 

    EXAMPLE:
         import dave.datapool as data

         postal = data.read_ehv_data()
    """
    ehv_data = {'ehv_nodes': pd.read_pickle(_get_data_path('ehv_nodes.p', 'ehvdata')),
                'ehv_node_changes': pd.read_pickle(_get_data_path('ehv_node_changes.p',
                                                           'ehvdata')),
                'ehv_lines': pd.read_pickle(_get_data_path('ehv_lines.p', 'ehvdata')),
                'ehv_trafos': pd.read_pickle(_get_data_path('ehv_trafos.p',
                                                     'ehvdata'))}
    return ehv_data



