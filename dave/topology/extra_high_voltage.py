import geopandas as gpd
import shapely.geometry
from shapely import affinity
import pandas as pd


   
def create_ehv_topology():
    """
    This function creates a dictonary with all relevant parameters for the
    estra high voltage level

    INPUT:
        **target_area** (dict) - all Informations about the target area

    OPTIONAL:

    OUTPUT:
        **grid data_ehv** (dict) - expanded grid_data dictonary with all 
                                   informations about the ehv topology
    EXAMPLE:
    """
    # print to inform user
    print('create extra high voltage network for target area')
    print('------------------------------------------')
    
    
    
    
    
    """
    hier muss bei den Leitungen eine filterung nach Spannungsebene (nur LEitungen auf 380 und 220kV) 
    und dann noch schauen ob sie im atrget gebiet liegen
    """
