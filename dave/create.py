import pandas as pd
import geopandas as gpd
from dave.dave_sturcture import davestructure
from dave import __version__


def create_empty_dataset():
    """
    This function initializes the dave datastructure.

    OUTPUT:
        **grid_data** (attrdict) - dave attrdict with empty tables:

    EXAMPLE:
        grid_data = create_empty_dataset()

    """
    # define crs
    crs = 'EPSG:4326'
    # define dave structure
    grid_data = davestructure({
                 # target data
                 'area': pd.DataFrame(),
                 'target_input': pd.DataFrame(),
                 'buildings': davestructure({'building_centroids': gpd.GeoSeries([], crs=crs),
                                             'commercial': gpd.GeoDataFrame([], crs=crs),
                                             'for_living': gpd.GeoDataFrame([], crs=crs),
                                             'other': gpd.GeoDataFrame([], crs=crs)
                                             }),
                 'roads': davestructure({'roads': gpd.GeoDataFrame([], crs=crs),
                                         'roads_plot': gpd.GeoDataFrame([], crs=crs),
                                         'road_junctions': gpd.GeoSeries([], crs=crs)
                                         }),
                 'landuse': gpd.GeoDataFrame([], crs=crs),
                 # power grid data
                 'ehv_data': davestructure({'ehv_nodes': gpd.GeoDataFrame([], crs=crs)}),
                 'lv_data': davestructure({'lv_nodes': davestructure({'building_connections': pd.DataFrame()
                                                                      }),
                                           'lv_lines': davestructure({'line_buildings': gpd.GeoDataFrame([], crs=crs),
                                                                      'line_connections': gpd.GeoDataFrame([], crs=crs)
                                                                      })
                                           }),
                 'components_power':davestructure({'renewable_powerplants':gpd.GeoDataFrame([], crs=crs),
                                                   'conventional_powerplants': gpd.GeoDataFrame([], crs=crs)}),
                 # auxillary
                 'dave_version': __version__
                 })
    return grid_data



def create_grid(postalcode=None, town_name=None, federal_state=None, own_area=None,voltage_level=['ALL'], pressure_level=['ALL']):
    
    """
    Hier eine funktion schreiben die alle modellierungsfunktionen so aufruft das aus einem Ortsnamen 
    oder einer PLZ ein fertiges Netz für strom und gas rauskommt
    
    Eingangsparameter müssten dann Ortsname, Bundeslandslame oder PLZ sein, sowie ein Parameter welche Spannungns- und/oder Druckebenen berücksichtigt werden sollen

    hier berücksichtigen das verschiedene Spannungsebenen, verschiedene funktionen benötigen
    Parameter voltage_level ist list of string mit allen SPannungsebeen die gewünsct sind ['HS','MS','NS']
    """
    # hier noch auswahl welchen eingangsparamter wir haben und parameter für das Netzgebiet über target_area funktion besorgen
    target=target_area(own_area=path)
    """
    if 'EHV' in in voltage_level:
        pass
    if 'HV' is in voltage_level:
        pass
    if 'MV' is in voltage_level:
        pass
    if 'LV' is in voltage_level:
        pass
    if 'HP' is in pressure_level:
        pass
    if 'MP' is in pressure_level:
        pass
    if 'LP' is in pressure_level:
        pass
    """