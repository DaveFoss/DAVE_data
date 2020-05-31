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

         ehv_data = data.read_ehv_data()
    """
    # read data
    ehv_nodes = pd.read_pickle(_get_data_path('ehv_nodes.p', 'ehvdata')).to_crs(epsg=4326)
    ehv_node_changes = pd.read_pickle(_get_data_path('ehv_node_changes.p', 'ehvdata'))
    ehv_lines = pd.read_pickle(_get_data_path('ehv_lines.p', 'ehvdata'))
    ehv_trafos = pd.read_pickle(_get_data_path('ehv_trafos.p', 'ehvdata'))
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
    # read data
    hp_nodes = gpd.read_file(_get_data_path('nodes.shp', 'hpdata')).to_crs(epsg=4326)
    hp_pipelines = gpd.read_file(_get_data_path('pipelines.shp', 'hpdata')).to_crs(epsg=4326)
    hp_pipelines = hp_pipelines.rename(columns={'LENGTH': 'LENGTH_km',
                                                'DIAMETER': 'DIAMETER_mm',
                                                'PRESSURE': 'PRESSURE_bar',
                                                'DIAM_EST': 'DIAM_EST_mm',
                                                'PRESS_EST': 'PRESS_EST_bar',
                                                'CAPACITY': 'CAPACITY_gwh_per_d'})
    hp_production = gpd.read_file(_get_data_path('production.shp', 'hpdata')).to_crs(epsg=4326)
    hp_production = hp_production.rename(columns={'PROD_QGIS_': 'MAX_CAPACITY_gwh_th_per_d'})
    hp_industry = gpd.read_file(_get_data_path('industry.shp', 'hpdata')).to_crs(epsg=4326)
    hp_storages = gpd.read_file(_get_data_path('storages.shp', 'hpdata')).to_crs(epsg=4326)
    hp_storages = hp_storages.rename(columns={'MAX_INJECT': 'MAX_INJECT_gwh_th_per_d',
                                              'MAX_WITHDR': 'MAX_WITHDR_gwh_th_per_d'})
    hp_gas_demand_total = gpd.read_file(_get_data_path('gas_demand_total.shp', 'hpdata')).to_crs(epsg=4326)
    hp_gas_demand_total = hp_gas_demand_total.rename(columns={'POWER_PLAN': 'POWER_PLANT_tj',
                                                              'HOUSEHOLD': 'HOUSEHOLD_tj',
                                                              'INDUSTRY': 'INDUSTRY_tj',
                                                              'TOTAL': 'TOTAL_tj'})
    # create dictonary
    hp_data = {'hp_nodes': hp_nodes,
               'hp_pipelines': hp_pipelines,
               'hp_production': hp_production,
               'hp_industry': hp_industry,
               'hp_storages': hp_storages,
               'hp_gas_demand_total': hp_gas_demand_total}
    return hp_data
