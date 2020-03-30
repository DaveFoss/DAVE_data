import geopandas as gpd
import shapely.geometry
from shapely import affinity
from shapely.ops import cascaded_union
import pandas as pd

from dave.datapool import read_ehv_data


   
def create_ehv_topology(grid_data):
    """
    This function creates a dictonary with all relevant parameters for the
    estra high voltage level

    INPUT:
        **target_area** (dict) - all Informations about the target area

    OPTIONAL:

    OUTPUT:

    EXAMPLE:
    """
    # print to inform user
    print('create extra high voltage network for target area')
    print('-------------------------------------------------')
    # read ehv tso data
    ehv_data = read_ehv_data()
    # search for ehv nodes in the target area
    ehv_nodes = gpd.overlay(ehv_data['ehv_nodes'],
                            grid_data.area,
                            how='intersection')
    ehv_nodes = ehv_nodes.rename(columns={'name_1': 'name'})
    ehv_nodes = ehv_nodes.sort_values(by=['name']).reset_index()
    ehv_nodes = ehv_nodes.filter(['name', 'name_osm', 'typ', 'voltage_kv', 
                                  'tso', 'osm_id', 'substation_typ', 
                                  'substation_geometry', 'substation_voltage', 
                                  'geometry'])
    grid_data.ehv_data.ehv_nodes = ehv_nodes
    
    
    
    
    
    """
    # create polygon for the whole target area
    target_polygon = cascaded_union(target_area['area'].geometry)
    """
    
    #hier schauen ob ehv knoten und leitung im Zielgebeit
    
    

    
    
    """
    hier muss bei den Leitungen eine filterung nach Spannungsebene (nur LEitungen auf 380 und 220kV) 
    und dann noch schauen ob sie im atrget gebiet liegen
    """
