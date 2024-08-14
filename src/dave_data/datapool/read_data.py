# Copyright (c) 2022-2024 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from geopandas import GeoDataFrame, points_from_xy
from pandas import HDFStore, Series, read_excel, read_hdf
from shapely.geometry import LineString
from shapely.wkb import loads
from xmlschema import XMLSchema

from dave_data.settings import dave_settings
from dave_data.toolbox import get_data_path


def read_postal():
    """
    This data includes the town name, the area, the population and the
    geometry for all german postalcode areas

    OUTPUT:
         **postal areas** (GeodataFrame) - all german postalcode areas

    EXAMPLE:
         import dave_data.datapool as data

         postal = data.read_postal()
    """
    # get data from datapool
    postalger = read_hdf(get_data_path("postalcodesger.h5", "data"))
    # convert geometry
    postalger["geometry"] = postalger.geometry.apply(loads)
    postalger = GeoDataFrame(postalger, crs=dave_settings["crs_main"])
    # read meta data
    meta_data = read_excel(get_data_path("postalcodesger_meta.xlsx", "data"), sheet_name=None)
    return postalger, meta_data


def read_federal_states():
    """
    This data includes the name, the length, the area, the population and the
    geometry for all german federal states

    OUTPUT:
         **federal_statess** (GeodataFrame) - all german federal states

    EXAMPLE:
         import dave_data.datapool as data

         federal = data.read_federal_states()
    """
    federalstatesger = read_hdf(get_data_path("federalstatesger.h5", "data"))
    federalstatesger["geometry"] = federalstatesger.geometry.apply(loads)
    federalstatesger = GeoDataFrame(federalstatesger, crs=dave_settings["crs_main"])
    # read meta data
    meta_data = read_excel(get_data_path("federalstatesger_meta.xlsx", "data"), sheet_name=None)
    return federalstatesger, meta_data


def read_nuts_regions(year):
    """
    This data includes the name and the geometry for the nuts regions of the years 2013, 2016 and 2021

    OUTPUT:
         **nuts_regions** (GeodataFrame) - nuts regions of the years 2013, 2016 and 2021

    EXAMPLE:
         import dave_data.datapool as data

         nuts = data.read_nuts_regions()
    """
    if year == "2013":
        nuts_regions = read_hdf(get_data_path("nuts_regions.h5", "data"), key="/nuts_2013")
        nuts_regions["geometry"] = nuts_regions.geometry.apply(loads)
        nuts_regions = GeoDataFrame(nuts_regions, crs=dave_settings["crs_main"])
    elif year == "2016":
        nuts_regions = read_hdf(get_data_path("nuts_regions.h5", "data"), key="/nuts_2016")
        nuts_regions["geometry"] = nuts_regions.geometry.apply(loads)
        nuts_regions = GeoDataFrame(nuts_regions, crs=dave_settings["crs_main"])
    elif year == "2021":
        nuts_regions = read_hdf(get_data_path("nuts_regions.h5", "data"), key="/nuts_2021")
        nuts_regions["geometry"] = nuts_regions.geometry.apply(loads)
        nuts_regions = GeoDataFrame(nuts_regions, crs=dave_settings["crs_main"])
    # read meta data
    meta_data = read_excel(get_data_path("nuts_regions_meta.xlsx", "data"), sheet_name=None)
    return nuts_regions, meta_data


def read_household_consumption():
    """
    This data includes informations for the german avarage houshold consumption and the avarage
    houshold sizes per federal state

    OUTPUT:
         **houshold consumption data** (dict) - Informations for the german high pressure gas grid

    EXAMPLE:
         import dave_data.datapool as data

         household_consumption = data.read_household_consumption()
    """
    # --- get data from datapool
    # read data
    consumption_data = HDFStore(get_data_path("household_power_consumption.h5", "data"))
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
    meta_data = read_excel(
        get_data_path("household_power_consumption_meta.xlsx", "data"), sheet_name=None
    )
    return consumption_data, meta_data


def read_scigridgas_iggielgn():
    """
    This data includes informations for the europe gas grid produced by scigridgas.
    The dataset is know as "iggielgn".

    OUTPUT:
         **scigridgas iggielgn data** (dict) - Informations for the europe gas grid

    EXAMPLE:
         import dave_data.datapool as data

         scigridgas_iggielgn = data.read_scigridgas_iggielgn()
    """
    # --- get data from datapool
    # read data
    iggielgn_data = HDFStore(get_data_path("scigridgas_iggielgn.h5", "data"))
    # border_points
    border_points = iggielgn_data.get("/scigridgas_iggielgn_border_points")
    border_points = GeoDataFrame(
        border_points,
        geometry=points_from_xy(border_points.long, border_points.lat),
        crs=dave_settings["crs_main"],
    )
    # compressors
    compressors = iggielgn_data.get("/scigridgas_iggielgn_compressors")
    compressors = GeoDataFrame(
        compressors,
        geometry=points_from_xy(compressors.long, compressors.lat),
        crs=dave_settings["crs_main"],
    )
    # comsumer
    consumers = iggielgn_data.get("/scigridgas_iggielgn_consumers")
    consumers = GeoDataFrame(
        consumers,
        geometry=points_from_xy(consumers.long, consumers.lat),
        crs=dave_settings["crs_main"],
    )
    # lngss
    lngs = iggielgn_data.get("/scigridgas_iggielgn_lngs")
    lngs = GeoDataFrame(
        lngs, geometry=points_from_xy(lngs.long, lngs.lat), crs=dave_settings["crs_main"]
    )
    # nodes
    nodes = iggielgn_data.get("/scigridgas_iggielgn_nodes")
    nodes = GeoDataFrame(
        nodes,
        geometry=points_from_xy(nodes.long, nodes.lat),
        crs=dave_settings["crs_main"],
    )
    # pipe_segments
    pipe_segments = iggielgn_data.get("/scigridgas_iggielgn_pipe_segments")
    pipe_segments.lat = pipe_segments.lat.apply(eval)
    pipe_segments.long = pipe_segments.long.apply(eval)
    geometry = [LineString(list(zip(pipe.long, pipe.lat))) for i, pipe in pipe_segments.iterrows()]
    pipe_segments = GeoDataFrame(
        pipe_segments, geometry=Series(geometry), crs=dave_settings["crs_main"]
    )
    # productions
    productions = iggielgn_data.get("/scigridgas_iggielgn_productions")
    productions = GeoDataFrame(
        productions,
        geometry=points_from_xy(productions.long, productions.lat),
        crs=dave_settings["crs_main"],
    )
    # storages
    storages = iggielgn_data.get("/scigridgas_iggielgn_storages")
    storages = GeoDataFrame(
        storages,
        geometry=points_from_xy(storages.long, storages.lat),
        crs=dave_settings["crs_main"],
    )
    # close file
    iggielgn_data.close()
    # create dictonary
    storage_data = {
        "border_points": border_points,
        "compressors": compressors,
        "consumers": consumers,
        "lngs": lngs,
        "nodes": nodes,
        "pipe_segments": pipe_segments,
        "productions": productions,
        "storages": storages,
    }
    # read meta data
    meta_data = read_excel(get_data_path("scigridgas_iggielgn_meta.xlsx", "data"), sheet_name=None)
    return storage_data, meta_data


def read_gaslib():
    # read data from datapool
    schema = XMLSchema(get_data_path("gaslib/Gas.xsd", "data"))
    gaslib_dict = schema.to_dict(get_data_path("gaslib/GasLib-582-v2.net", "data"))
    # create data dictionary
    gaslib_data = {
        "nodes": gaslib_dict["framework:nodes"],
        "connections": gaslib_dict["framework:connections"],
    }
    # read meta data
    meta_data = gaslib_dict["framework:information"]
    return gaslib_data, meta_data
