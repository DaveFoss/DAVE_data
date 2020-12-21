import os
import geopandas as gpd
import pandas as pd
from shapely.wkb import loads, dumps
from shapely.geometry import LineString

from dave import dave_dir
from dave.settings import dave_settings


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
    postalger = gpd.GeoDataFrame(postalger, crs=dave_settings()['crs_main'])
    # read meta data
    meta_data = pd.read_excel(get_data_path('postalger_meta.xlsx', 'data'), sheet_name=None)
    return postalger, meta_data


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
    federalstatesger = gpd.GeoDataFrame(federalstatesger, crs=dave_settings()['crs_main'])
    # read meta data
    meta_data = pd.read_excel(get_data_path('federalstatesger_meta.xlsx', 'data'), sheet_name=None)
    return federalstatesger, meta_data


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
    ehv_nodes = gpd.GeoDataFrame(ehv_nodes, crs=dave_settings()['crs_main'])
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
    # read meta data
    meta_data = pd.read_excel(get_data_path('ehv_data_meta.xlsx', 'data'), sheet_name=None)
    return ehv_data, meta_data


def read_hp_data():
    """
    This data includes informations for the german high pressure gas grid based on the publication
    "Electricity, Heat, and Gas Sector Data for Modeling the German System" from the LKD_eu project.

    The reference year for the data is 2015.
    
    Hint: This data ist also include at the scigridgas_igginl dataset

    OUTPUT:
         **high pressure data** (dict) - Informations for the german high pressure gas grid

    EXAMPLE:
         import dave.datapool as data

         hp_data = data.read_hp_data()
    """
    # --- read data
    hp_data = pd.HDFStore(get_data_path('hp_data.h5', 'data'))
    data_crs = 'EPSG:31468'
    # nodes
    hp_nodes = hp_data.get('/nodes')
    hp_nodes = convert_geometry_to_wkt(hp_nodes)
    hp_nodes = gpd.GeoDataFrame(hp_nodes, crs=data_crs).to_crs(dave_settings()['crs_main'])
    # pipelines
    hp_pipelines = hp_data.get('/pipelines')
    hp_pipelines = convert_geometry_to_wkt(hp_pipelines)
    hp_pipelines = gpd.GeoDataFrame(hp_pipelines, crs=data_crs).to_crs(dave_settings()['crs_main'])
    # production
    hp_production = hp_data.get('/production')
    hp_production = convert_geometry_to_wkt(hp_production)
    hp_production = gpd.GeoDataFrame(hp_production, crs=data_crs).to_crs(dave_settings()['crs_main'])
    # industry
    hp_industry = hp_data.get('/industry')
    hp_industry = convert_geometry_to_wkt(hp_industry)
    hp_industry = gpd.GeoDataFrame(hp_industry, crs=data_crs).to_crs(dave_settings()['crs_main'])
    # storgae
    hp_storages = hp_data.get('/storages')
    hp_storages = convert_geometry_to_wkt(hp_storages)
    hp_storages = gpd.GeoDataFrame(hp_storages, crs=data_crs).to_crs(dave_settings()['crs_main'])
    # gas demand total
    hp_gas_demand_total = hp_data.get('/gas_demand_total')
    hp_gas_demand_total = convert_geometry_to_wkt(hp_gas_demand_total)
    hp_gas_demand_total = gpd.GeoDataFrame(hp_gas_demand_total, crs=data_crs).to_crs(dave_settings()['crs_main'])
    # close file
    hp_data.close()
    # create dictonary
    hp_data = {'hp_nodes': hp_nodes,
               'hp_pipelines': hp_pipelines,
               'hp_production': hp_production,
               'hp_industry': hp_industry,
               'hp_storages': hp_storages,
               'hp_gas_demand_total': hp_gas_demand_total}
    # read meta data
    meta_data = pd.read_excel(get_data_path('ehv_data_meta.xlsx', 'data'), sheet_name=None)
    return hp_data, meta_data


def read_gas_storage_ugs():
    """
    This data includes informations for the gas storages in germany based on the publication
    "Underground Gas Storage in Germany".

    The reference year for the data is 2019.

    OUTPUT:
         **gas storage data** (dict) - Informations for gas storages in germany

    EXAMPLE:
         import dave.datapool as data

         storage_data = data.read_gas_storage_ugs()
    """
    # --- read data
    storage_data = pd.HDFStore(get_data_path('gas_storage_ugs.h5', 'data'))
    # cavern storage for crude oil, petroleum products and liquid gas
    cavern_fluid = storage_data.get('/fluid cavern storage')
    cavern_fluid = gpd.GeoDataFrame(cavern_fluid,
                                    geometry=gpd.points_from_xy(cavern_fluid.Lon, cavern_fluid.Lat),
                                    crs=dave_settings()['crs_main'])
    # cavern storages for natural gas
    cavern_gas = storage_data.get('/natural gas cavern storage')
    cavern_gas = gpd.GeoDataFrame(cavern_gas,
                                  geometry=gpd.points_from_xy(cavern_gas.Lon, cavern_gas.Lat),
                                  crs=dave_settings()['crs_main'])
    # pore storages for natural gas
    pore_gas = storage_data.get('/natural gas pore storage')
    pore_gas = gpd.GeoDataFrame(pore_gas,
                                geometry=gpd.points_from_xy(pore_gas.Lon, pore_gas.Lat),
                                crs=dave_settings()['crs_main'])

    # close file
    storage_data.close()
    # create dictonary
    storage_data = {'cavern_fluid': cavern_fluid,
                    'cavern_gas': cavern_gas,
                    'pore_gas': pore_gas}
    # read meta data
    meta_data = pd.read_excel(get_data_path('ehv_data_meta.xlsx', 'data'), sheet_name=None)
    return storage_data, meta_data


def read_household_consumption():
    """
    This data includes informations for the german avarage houshold consumption and the avarage 
    houshold sizes per federal state

    OUTPUT:
         **houshold consumption data** (dict) - Informations for the german high pressure gas grid

    EXAMPLE:
         import dave.datapool as data

         household_consumption = data.read_household_consumption()
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
    # read meta data
    meta_data = pd.read_excel(get_data_path('ehv_data_meta.xlsx', 'data'), sheet_name=None)
    return consumption_data, meta_data


def read_scigridgas_igginl():
    """
    This data includes informations for the europe gas grid produced by scigridgas.
    The dataset is know as "igginl".

    OUTPUT:
         **scigridgas igginl data** (dict) - Informations for the europe gas grid

    EXAMPLE:
         import dave.datapool as data

         scigridgas_igginl = data.read_scigridgas_igginl()
    """
    # --- read data
    igginl_data = pd.HDFStore(get_data_path('scigridgas_igginl.h5', 'data'))
    # border_points
    border_points = igginl_data.get('/border_points')
    border_points = gpd.GeoDataFrame(border_points, geometry=gpd.points_from_xy(border_points.long,
                                                                                border_points.lat),
                                     crs=dave_settings()['crs_main'])
    # compressors
    compressors = igginl_data.get('/compressors')
    compressors = gpd.GeoDataFrame(compressors, geometry=gpd.points_from_xy(compressors.long,
                                                                            compressors.lat),
                                   crs=dave_settings()['crs_main'])
    # entry_points
    entry_points = igginl_data.get('/entry_points')
    entry_points = gpd.GeoDataFrame(entry_points, geometry=gpd.points_from_xy(entry_points.long,
                                                                              entry_points.lat),
                                    crs=dave_settings()['crs_main'])
    # inter_connection_points
    connection_points = igginl_data.get('/inter_connection_points')
    inter_connection_points = gpd.GeoDataFrame(connection_points,
                                               geometry=gpd.points_from_xy(connection_points.long,
                                                                           connection_points.lat),
                                               crs=dave_settings()['crs_main'])
    # lngss
    lngs = igginl_data.get('/lngs')
    lngs = gpd.GeoDataFrame(lngs, geometry=gpd.points_from_xy(lngs.long, lngs.lat),
                            crs=dave_settings()['crs_main'])
    # nodes
    nodes = igginl_data.get('/nodes')
    nodes = gpd.GeoDataFrame(nodes, geometry=gpd.points_from_xy(nodes.long, nodes.lat),
                             crs=dave_settings()['crs_main'])
    # pipe_segments
    pipe_segments = igginl_data.get('/pipe_segments')
    pipe_segments.lat = pipe_segments.lat.apply(lambda x: eval(x))
    pipe_segments.long = pipe_segments.long.apply(lambda x: eval(x))
    geometry = []
    for i, pipe in pipe_segments.iterrows():
        lat = pipe.lat
        long = pipe.long
        line = LineString(list(zip(long, lat)))
        geometry.append(line)
    pipe_segments = gpd.GeoDataFrame(pipe_segments, geometry=pd.Series(geometry),
                                     crs=dave_settings()['crs_main'])
    # productions
    productions = igginl_data.get('/productions')
    productions = gpd.GeoDataFrame(productions, geometry=gpd.points_from_xy(productions.long,
                                                                            productions.lat),
                                   crs=dave_settings()['crs_main'])
    # storages
    storages = igginl_data.get('/storages')
    storages = gpd.GeoDataFrame(storages, geometry=gpd.points_from_xy(storages.long, storages.lat),
                                crs=dave_settings()['crs_main'])
    # close file
    igginl_data.close()
    # create dictonary
    storage_data = {'border_points': border_points,
                    'compressors': compressors,
                    'entry_points': entry_points,
                    'inter_connection_points': inter_connection_points,
                    'lngs': lngs,
                    'nodes': nodes,
                    'pipe_segments': pipe_segments,
                    'productions': productions,
                    'storages': storages}
    # read meta data
    meta_data = pd.read_excel(get_data_path('scigridgas_igginl.xlsx', 'data'), sheet_name=None)
    return storage_data, meta_data
