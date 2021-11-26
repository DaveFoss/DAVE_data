import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString
from shapely.wkb import loads

from dave.io import from_mongo
from dave.settings import dave_settings
from dave.toolbox import get_data_path


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
    # requestn data from database
    postalger = from_mongo("geo", "postalcodes")
    # read meta data
    meta_data = pd.read_excel(r"data\postalger_meta.xlsx", sheet_name=None)
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
    federalstatesger = pd.read_hdf(get_data_path("federalstatesger.h5", "data"))
    federalstatesger["geometry"] = federalstatesger.geometry.apply(loads)
    federalstatesger = gpd.GeoDataFrame(federalstatesger, crs=dave_settings()["crs_main"])
    # read meta data
    meta_data = pd.read_excel(r"data\federalstatesger_meta.xlsx", sheet_name=None)
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
    ehv_data = pd.HDFStore(get_data_path("ehv_data.h5", "data"))
    # get the individual Data Frames
    ehv_nodes = ehv_data.get("/ehv_nodes")
    ehv_nodes["geometry"] = ehv_nodes.geometry.apply(loads)
    ehv_nodes = gpd.GeoDataFrame(ehv_nodes, crs=dave_settings()["crs_main"])
    ehv_node_changes = ehv_data.get("/ehv_node_changes")
    ehv_lines = ehv_data.get("/ehv_lines")
    ehv_trafos = ehv_data.get("/ehv_trafos")
    # close file
    ehv_data.close()
    # create dictonary
    ehv_data = {
        "ehv_nodes": ehv_nodes,
        "ehv_node_changes": ehv_node_changes,
        "ehv_lines": ehv_lines,
        "ehv_trafos": ehv_trafos,
    }
    # read meta data
    meta_data = pd.read_excel(r"data\ehv_data_meta.xlsx", sheet_name=None)
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
    hp_data = pd.HDFStore(get_data_path("hp_data.h5", "data"))
    data_crs = "EPSG:31468"
    # nodes
    hp_nodes = hp_data.get("/nodes")
    hp_nodes["geometry"] = hp_nodes.geometry.apply(loads)
    hp_nodes = gpd.GeoDataFrame(hp_nodes, crs=data_crs).to_crs(dave_settings()["crs_main"])
    # pipelines
    hp_pipelines = hp_data.get("/pipelines")
    hp_pipelines["geometry"] = hp_pipelines.geometry.apply(loads)
    hp_pipelines = gpd.GeoDataFrame(hp_pipelines, crs=data_crs).to_crs(dave_settings()["crs_main"])
    # production
    hp_production = hp_data.get("/production")
    hp_production["geometry"] = hp_production.geometry.apply(loads)
    hp_production = gpd.GeoDataFrame(hp_production, crs=data_crs).to_crs(
        dave_settings()["crs_main"]
    )
    # industry
    hp_industry = hp_data.get("/industry")
    hp_industry["geometry"] = hp_industry.geometry.apply(loads)
    hp_industry = gpd.GeoDataFrame(hp_industry, crs=data_crs).to_crs(dave_settings()["crs_main"])
    # storgae
    hp_storages = hp_data.get("/storages")
    hp_storages["geometry"] = hp_storages.geometry.apply(loads)
    hp_storages = gpd.GeoDataFrame(hp_storages, crs=data_crs).to_crs(dave_settings()["crs_main"])
    # gas demand total
    hp_gas_demand_total = hp_data.get("/gas_demand_total")
    hp_gas_demand_total["geometry"] = hp_gas_demand_total.geometry.apply(loads)
    hp_gas_demand_total = gpd.GeoDataFrame(hp_gas_demand_total, crs=data_crs).to_crs(
        dave_settings()["crs_main"]
    )
    # close file
    hp_data.close()
    # create dictonary
    hp_data = {
        "hp_nodes": hp_nodes,
        "hp_pipelines": hp_pipelines,
        "hp_production": hp_production,
        "hp_industry": hp_industry,
        "hp_storages": hp_storages,
        "hp_gas_demand_total": hp_gas_demand_total,
    }
    # read meta data
    meta_data = pd.read_excel(r"data\ehv_data_meta.xlsx", sheet_name=None)
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
    storage_data = pd.HDFStore(get_data_path("gas_storage_ugs.h5", "data"))
    # cavern storage for crude oil, petroleum products and liquid gas
    cavern_fluid = storage_data.get("/fluid cavern storage")
    cavern_fluid = gpd.GeoDataFrame(
        cavern_fluid,
        geometry=gpd.points_from_xy(cavern_fluid.Lon, cavern_fluid.Lat),
        crs=dave_settings()["crs_main"],
    )
    # cavern storages for natural gas
    cavern_gas = storage_data.get("/natural gas cavern storage")
    cavern_gas = gpd.GeoDataFrame(
        cavern_gas,
        geometry=gpd.points_from_xy(cavern_gas.Lon, cavern_gas.Lat),
        crs=dave_settings()["crs_main"],
    )
    # pore storages for natural gas
    pore_gas = storage_data.get("/natural gas pore storage")
    pore_gas = gpd.GeoDataFrame(
        pore_gas,
        geometry=gpd.points_from_xy(pore_gas.Lon, pore_gas.Lat),
        crs=dave_settings()["crs_main"],
    )

    # close file
    storage_data.close()
    # create dictonary
    storage_data = {"cavern_fluid": cavern_fluid, "cavern_gas": cavern_gas, "pore_gas": pore_gas}
    # read meta data
    meta_data = pd.read_excel(r"data\ehv_data_meta.xlsx", sheet_name=None)
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
    consumption_data = pd.HDFStore(get_data_path("household_power_consumption.h5", "data"))
    # consumption avarage
    household_consumptions = consumption_data.get("/household_consumptions")
    household_sizes = consumption_data.get("/household_sizes")
    # close file
    consumption_data.close()
    # create dictonary
    consumption_data = {
        "household_consumptions": household_consumptions,
        "household_sizes": household_sizes,
    }
    # read meta data
    meta_data = pd.read_excel(r"data\ehv_data_meta.xlsx", sheet_name=None)
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
    igginl_data = pd.HDFStore(get_data_path("scigridgas_igginl.h5", "data"))
    # border_points
    border_points = igginl_data.get("/border_points")
    border_points = gpd.GeoDataFrame(
        border_points,
        geometry=gpd.points_from_xy(border_points.long, border_points.lat),
        crs=dave_settings()["crs_main"],
    )
    # compressors
    compressors = igginl_data.get("/compressors")
    compressors = gpd.GeoDataFrame(
        compressors,
        geometry=gpd.points_from_xy(compressors.long, compressors.lat),
        crs=dave_settings()["crs_main"],
    )
    # entry_points
    entry_points = igginl_data.get("/entry_points")
    entry_points = gpd.GeoDataFrame(
        entry_points,
        geometry=gpd.points_from_xy(entry_points.long, entry_points.lat),
        crs=dave_settings()["crs_main"],
    )
    # inter_connection_points
    connection_points = igginl_data.get("/inter_connection_points")
    inter_connection_points = gpd.GeoDataFrame(
        connection_points,
        geometry=gpd.points_from_xy(connection_points.long, connection_points.lat),
        crs=dave_settings()["crs_main"],
    )
    # lngss
    lngs = igginl_data.get("/lngs")
    lngs = gpd.GeoDataFrame(
        lngs, geometry=gpd.points_from_xy(lngs.long, lngs.lat), crs=dave_settings()["crs_main"]
    )
    # nodes
    nodes = igginl_data.get("/nodes")
    nodes = gpd.GeoDataFrame(
        nodes, geometry=gpd.points_from_xy(nodes.long, nodes.lat), crs=dave_settings()["crs_main"]
    )
    # pipe_segments
    pipe_segments = igginl_data.get("/pipe_segments")
    pipe_segments.lat = pipe_segments.lat.apply(eval)
    pipe_segments.long = pipe_segments.long.apply(eval)
    geometry = [LineString(list(zip(pipe.long, pipe.lat))) for i, pipe in pipe_segments.iterrows()]
    pipe_segments = gpd.GeoDataFrame(
        pipe_segments, geometry=pd.Series(geometry), crs=dave_settings()["crs_main"]
    )
    # productions
    productions = igginl_data.get("/productions")
    productions = gpd.GeoDataFrame(
        productions,
        geometry=gpd.points_from_xy(productions.long, productions.lat),
        crs=dave_settings()["crs_main"],
    )
    # storages
    storages = igginl_data.get("/storages")
    storages = gpd.GeoDataFrame(
        storages,
        geometry=gpd.points_from_xy(storages.long, storages.lat),
        crs=dave_settings()["crs_main"],
    )
    # close file
    igginl_data.close()
    # create dictonary
    storage_data = {
        "border_points": border_points,
        "compressors": compressors,
        "entry_points": entry_points,
        "inter_connection_points": inter_connection_points,
        "lngs": lngs,
        "nodes": nodes,
        "pipe_segments": pipe_segments,
        "productions": productions,
        "storages": storages,
    }
    # read meta data
    meta_data = pd.read_excel(r"data\scigridgas_igginl_meta.xlsx", sheet_name=None)
    return storage_data, meta_data


def read_scigridgas_iggielgn():
    """
    This data includes informations for the europe gas grid produced by scigridgas.
    The dataset is know as "iggielgn".

    OUTPUT:
         **scigridgas iggielgn data** (dict) - Informations for the europe gas grid

    EXAMPLE:
         import dave.datapool as data

         scigridgas_iggielgn = data.read_scigridgas_iggielgn()
    """
    # --- read data
    iggielgn_data = pd.HDFStore(get_data_path("scigridgas_iggielgn.h5", "data"))
    # border_points
    border_points = iggielgn_data.get("/border_points")
    border_points = gpd.GeoDataFrame(
        border_points,
        geometry=gpd.points_from_xy(border_points.long, border_points.lat),
        crs=dave_settings()["crs_main"],
    )
    # compressors
    compressors = iggielgn_data.get("/compressors")
    compressors = gpd.GeoDataFrame(
        compressors,
        geometry=gpd.points_from_xy(compressors.long, compressors.lat),
        crs=dave_settings()["crs_main"],
    )
    # connection points
    connection_points = iggielgn_data.get("/connection_points")
    connection_points = gpd.GeoDataFrame(
        connection_points,
        geometry=gpd.points_from_xy(connection_points.long, connection_points.lat),
        crs=dave_settings()["crs_main"],
    )
    # comsumer
    consumers = iggielgn_data.get("/consumers")
    consumers = gpd.GeoDataFrame(
        consumers,
        geometry=gpd.points_from_xy(consumers.long, consumers.lat),
        crs=dave_settings()["crs_main"],
    )
    # entry_points
    entry_points = iggielgn_data.get("/entry_points")
    entry_points = gpd.GeoDataFrame(
        entry_points,
        geometry=gpd.points_from_xy(entry_points.long, entry_points.lat),
        crs=dave_settings()["crs_main"],
    )
    # inter_connection_points
    connection_points = iggielgn_data.get("/inter_connection_points")
    inter_connection_points = gpd.GeoDataFrame(
        connection_points,
        geometry=gpd.points_from_xy(connection_points.long, connection_points.lat),
        crs=dave_settings()["crs_main"],
    )
    # lngss
    lngs = iggielgn_data.get("/lngs")
    lngs = gpd.GeoDataFrame(
        lngs, geometry=gpd.points_from_xy(lngs.long, lngs.lat), crs=dave_settings()["crs_main"]
    )
    # nodes
    nodes = iggielgn_data.get("/nodes")
    nodes = gpd.GeoDataFrame(
        nodes, geometry=gpd.points_from_xy(nodes.long, nodes.lat), crs=dave_settings()["crs_main"]
    )
    # pipe_segments
    pipe_segments = iggielgn_data.get("/pipe_segments")
    pipe_segments.lat = pipe_segments.lat.apply(eval)
    pipe_segments.long = pipe_segments.long.apply(eval)
    geometry = [LineString(list(zip(pipe.long, pipe.lat))) for i, pipe in pipe_segments.iterrows()]
    pipe_segments = gpd.GeoDataFrame(
        pipe_segments, geometry=pd.Series(geometry), crs=dave_settings()["crs_main"]
    )
    # productions
    productions = iggielgn_data.get("/productions")
    productions = gpd.GeoDataFrame(
        productions,
        geometry=gpd.points_from_xy(productions.long, productions.lat),
        crs=dave_settings()["crs_main"],
    )
    # storages
    storages = iggielgn_data.get("/storages")
    storages = gpd.GeoDataFrame(
        storages,
        geometry=gpd.points_from_xy(storages.long, storages.lat),
        crs=dave_settings()["crs_main"],
    )
    # close file
    iggielgn_data.close()
    # create dictonary
    storage_data = {
        "border_points": border_points,
        "compressors": compressors,
        "connection_points": connection_points,
        "consumers": consumers,
        "entry_points": entry_points,
        "inter_connection_points": inter_connection_points,
        "lngs": lngs,
        "nodes": nodes,
        "pipe_segments": pipe_segments,
        "productions": productions,
        "storages": storages,
    }
    # read meta data
    meta_data = pd.read_excel(r"data\scigridgas_iggielgn_meta.xlsx", sheet_name=None)
    return storage_data, meta_data
