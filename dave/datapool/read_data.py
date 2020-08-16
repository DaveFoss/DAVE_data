import os
import geopandas as gpd
import pandas as pd
from shapely.wkb import loads, dumps

from dave import dave_dir


def get_data_path(filename=None, dirname=None):
    """
    This function returns the full os path for a given directory (and filename)
    """
    if filename:
        return os.path.join(dave_dir, 'datapool', dirname, filename)
    else:
        return os.path.join(dave_dir, 'datapool', dirname)


def convert_geometry_to_wkt(data_df):
    """
    This function converts geometry of a data frame from WKB to WKT format
    """
    data_df['geom'] = None  # create empty column, otherwise ther'e could be problems with add geoemtry
    for i, data in data_df.iterrows():
        data_df.at[i, 'geom'] = loads(data.geometry)
    data_df = data_df.drop(columns=['geometry'])
    data_df = data_df.rename(columns={"geom": "geometry"})
    return data_df

def convert_geometry_to_wkb(data_df):
    """
    This function converts geometry of a data frame from WKT to WKB format
    """
    data_df['geom'] = None  # create empty column, otherwise ther'e could be problems with add geoemtry
    for i, data in data_df.iterrows():
        data_df.at[i, 'geom'] = dumps(data.geometry)
    data_df = data_df.drop(columns=['geometry'])
    data_df = data_df.rename(columns={"geom": "geometry"})
    return data_df
    

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
    postalger = pd.read_hdf(get_data_path('postalger.h5', 'data'))
    postalger = convert_geometry_to_wkt(postalger)  # convert geometry
    postalger = gpd.GeoDataFrame(postalger, crs="EPSG:4326")
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
    federalstatesger = pd.read_hdf(get_data_path('federalstatesger.h5', 'data'))
    federalstatesger = convert_geometry_to_wkt(federalstatesger)  # convert geometry
    federalstatesger = gpd.GeoDataFrame(federalstatesger, crs="EPSG:4326")
    return federalstatesger


def read_ehv_data():
    """
    This data includes the node, line and transformer informations for the
    german extra high voltage level based of the data from the four german tso

    OUTPUT:
         **extra high voltage data** (dict) - Informations from the german tso

    EXAMPLE:
         import dave.datapool as data

         ehv_data = data.read_ehv_data()
    """
    # read data
    ehv_data = pd.HDFStore(get_data_path('ehv_data.h5', 'data'))
    # get the individual Data Frames
    ehv_nodes = ehv_data.get('/ehv_nodes')
    ehv_nodes = convert_geometry_to_wkt(ehv_nodes)
    ehv_nodes = gpd.GeoDataFrame(ehv_nodes, crs="EPSG:4326")
    ehv_node_changes = ehv_data.get('/ehv_node_changes')
    ehv_lines = ehv_data.get('/ehv_lines')
    ehv_trafos = ehv_data.get('/ehv_trafos')
    # close file
    ehv_data.close()
    # create dictonary
    ehv_data = {'ehv_nodes': ehv_nodes,
                'ehv_node_changes': ehv_node_changes,
                'ehv_lines': ehv_lines,
                'ehv_trafos': ehv_trafos}
    return ehv_data


def read_hp_data():
    """
    This data includes informations for the german high pressure gas grid based on the publication
    "Electricity, Heat, and Gas Sector Data for Modeling the German System".
    
    The reference year for the data is 2015.

    OUTPUT:
         **high pressure data** (dict) - Informations for the german high pressure gas grid

    EXAMPLE:
         import dave.datapool as data

         hp_data = data.read_hp_data()
    """
    # --- read data
    hp_data = pd.HDFStore(get_data_path('hp_data.h5', 'data'))
    # nodes
    hp_nodes = hp_data.get('/nodes')
    hp_nodes = convert_geometry_to_wkt(hp_nodes)
    hp_nodes = gpd.GeoDataFrame(hp_nodes, crs="EPSG:31468").to_crs(epsg=4326)
    # pipelines
    hp_pipelines = hp_data.get('/pipelines')
    hp_pipelines = convert_geometry_to_wkt(hp_pipelines)
    hp_pipelines = gpd.GeoDataFrame(hp_pipelines, crs="EPSG:31468").to_crs(epsg=4326)
    # production
    hp_production = hp_data.get('/production')
    hp_production = convert_geometry_to_wkt(hp_production)
    hp_production = gpd.GeoDataFrame(hp_production, crs="EPSG:31468").to_crs(epsg=4326)
    # industry
    hp_industry = hp_data.get('/industry')
    hp_industry = convert_geometry_to_wkt(hp_industry)
    hp_industry = gpd.GeoDataFrame(hp_industry, crs="EPSG:31468").to_crs(epsg=4326)
    # storgae
    hp_storages = hp_data.get('/storages')
    hp_storages = convert_geometry_to_wkt(hp_storages)
    hp_storages = gpd.GeoDataFrame(hp_storages, crs="EPSG:31468").to_crs(epsg=4326)
    # gas demand total
    hp_gas_demand_total = hp_data.get('/gas_demand_total')
    hp_gas_demand_total = convert_geometry_to_wkt(hp_gas_demand_total)
    hp_gas_demand_total = gpd.GeoDataFrame(hp_gas_demand_total, crs="EPSG:31468").to_crs(epsg=4326)
    # close file
    hp_data.close()
    # create dictonary
    hp_data = {'hp_nodes': hp_nodes,
               'hp_pipelines': hp_pipelines,
               'hp_production': hp_production,
               'hp_industry': hp_industry,
               'hp_storages': hp_storages,
               'hp_gas_demand_total': hp_gas_demand_total}
    return hp_data


def read_household_consumption():
    """
    This data includes informations for the german high pressure gas grid based on the publication
    "Electricity, Heat, and Gas Sector Data for Modeling the German System".
    
    The reference year for the data is 2015.

    OUTPUT:
         **high pressure data** (dict) - Informations for the german high pressure gas grid

    EXAMPLE:
         import dave.datapool as data

         hp_data = data.read_hp_data()
    """
    # --- read data
    consumption_data = pd.HDFStore(get_data_path('household_power_consumption.h5', 'data'))
    # consumption avarage
    household_consumptions = consumption_data.get('/household_consumptions')
    household_sizes = consumption_data.get('/household_sizes')
    # close file
    consumption_data.close()
    # create dictonary
    consumption_data = {'household_consumptions': household_consumptions,
                        'household_sizes': household_sizes}
    return consumption_data
