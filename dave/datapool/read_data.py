import os
import geopandas as gpd

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
    This data includes the town name, the area, the population and the geometry for all german 
    postalcode areas

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
    This data includes the name, the length, the area, the population and the geometry for all 
    german federal states

    OUTPUT:
         **federal_statess** (GeodataFrame) - all german federal states 

    EXAMPLE:
         import dave.datapool as data

         postal = data.read_federal_states()
    """
    federalstatesger = gpd.read_file(_get_data_path('federalstatesger.shp', 'federalstatesger'))
    return federalstatesger

