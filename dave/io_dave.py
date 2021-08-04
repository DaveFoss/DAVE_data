import os
import copy
import geopandas as gpd
import pandas as pd
from pandapower import to_json, from_json
from shapely.wkb import loads, dumps
from shapely.geometry import Point, LineString, MultiLineString

import dave.create
from dave.settings import dave_settings
from dave.io import wkb_to_wkt, wkt_to_wkb


def from_hdf(dataset_path):
    """
    This functions reads a dave dataset in HDF5 format from a user given path

    Output  grid_data - dave dataset

    Example  grid_data = read_dataset(dataset_path)
    """
    crs = dave_settings()['crs_main']
    # check if file exist
    if os.path.exists(dataset_path):
        # read data
        file = pd.HDFStore(dataset_path)
        # create empty dave dataset
        grid_data = dave.create.create_empty_dataset()
        # --- create dave dataset from archiv file
        # area
        area = wkb_to_wkt(file, '/area')
        area = gpd.GeoDataFrame(area, crs=crs)
        grid_data.area = grid_data.area.append(area)
        # target input
        grid_data.target_input = grid_data.target_input.append(file.get('/target_input'))
        # buildings
        commercial = wkb_to_wkt(file, '/buildings/commercial')
        if not commercial.empty:
            grid_data.buildings.commercial = grid_data.buildings.commercial.append(gpd.GeoDataFrame(
                commercial, crs=crs))
        for_living = wkb_to_wkt(file, '/buildings/for_living')
        if not for_living.empty:
            grid_data.buildings.for_living = grid_data.buildings.for_living.append(gpd.GeoDataFrame(
                for_living, crs=crs))
        other = wkb_to_wkt(file, '/buildings/other')
        if not other.empty:
            grid_data.buildings.other = grid_data.buildings.other.append(gpd.GeoDataFrame(other,
                                                                                          crs=crs))
        # roads
        roads = wkb_to_wkt(file, '/roads/roads')
        if not roads.empty:
            grid_data.roads.roads = grid_data.roads.roads.append(gpd.GeoDataFrame(roads, crs=crs))
        roads_plot = wkb_to_wkt(file, '/roads/roads_plot')
        if not roads_plot.empty:
            grid_data.roads.roads_plot = grid_data.roads.roads_plot.append(gpd.GeoDataFrame(
                roads_plot, crs=crs))
        road_junctions = wkb_to_wkt(file, '/roads/road_junctions')
        if not road_junctions.empty:
            road_junctions = gpd.GeoSeries(road_junctions['geometry'], crs=crs)
            grid_data.roads.road_junctions = grid_data.roads.road_junctions.append(road_junctions)
        # landuse
        landuse = wkb_to_wkt(file, '/landuse')
        if not landuse.empty:
            grid_data.landuse = grid_data.landuse.append(gpd.GeoDataFrame(landuse, crs=crs))
        # ehv data
        ehv_lines = wkb_to_wkt(file, '/ehv_data/ehv_lines')
        if not ehv_lines.empty:
            grid_data.ehv_data.ehv_lines = grid_data.ehv_data.ehv_lines.append(
                gpd.GeoDataFrame(ehv_lines, crs=crs))
        ehv_nodes = wkb_to_wkt(file, '/ehv_data/ehv_nodes')
        if not ehv_nodes.empty:
            grid_data.ehv_data.ehv_nodes = grid_data.ehv_data.ehv_nodes.append(
                gpd.GeoDataFrame(ehv_nodes, crs=crs))
        # hv data
        hv_nodes = wkb_to_wkt(file, '/hv_data/hv_nodes')
        if not hv_nodes.empty:
            grid_data.hv_data.hv_nodes = grid_data.hv_data.hv_nodes.append(gpd.GeoDataFrame(
                hv_nodes, crs=crs))
        hv_lines = wkb_to_wkt(file, '/hv_data/hv_lines')
        if not hv_lines.empty:
            grid_data.hv_data.hv_lines = grid_data.hv_data.hv_lines.append(gpd.GeoDataFrame(
                hv_lines, crs=crs))
        # mv data
        mv_nodes = wkb_to_wkt(file, '/mv_data/mv_nodes')
        if not mv_nodes.empty:
            grid_data.mv_data.mv_nodes = grid_data.mv_data.mv_nodes.append(gpd.GeoDataFrame(
                mv_nodes, crs=crs))
        mv_lines = wkb_to_wkt(file, '/mv_data/mv_lines')
        if not mv_lines.empty:
            grid_data.mv_data.mv_lines = grid_data.mv_data.mv_lines.append(gpd.GeoDataFrame(
                mv_lines, crs=crs))
        # lv data
        lv_nodes = wkb_to_wkt(file, '/lv_data/lv_nodes')
        if not lv_nodes.empty:
            grid_data.lv_data.lv_nodes = grid_data.lv_data.lv_nodes.append(gpd.GeoDataFrame(
                lv_nodes, crs=crs))
        lv_lines = wkb_to_wkt(file, '/lv_data/lv_lines')
        if not lv_lines.empty:
            grid_data.lv_data.lv_lines = grid_data.lv_data.lv_lines.append(gpd.GeoDataFrame(
                lv_lines, crs=crs))
        # components_power
        conventional_powerplants = wkb_to_wkt(file, '/components_power/conventional_powerplants')
        if not conventional_powerplants.empty:
            grid_data.components_power.conventional_powerplants = \
                grid_data.components_power.conventional_powerplants.append(gpd.GeoDataFrame(
                    conventional_powerplants, crs=crs))
        renewable_powerplants = wkb_to_wkt(file, '/components_power/renewable_powerplants')
        if not renewable_powerplants.empty:
            grid_data.components_power.renewable_powerplants = \
                grid_data.components_power.renewable_powerplants.append(gpd.GeoDataFrame(
                    renewable_powerplants, crs=crs))
        load = wkb_to_wkt(file, '/components_power/loads')
        if not load.empty:
            grid_data.components_power.loads = grid_data.components_power.loads.append(
                gpd.GeoDataFrame(load))
        ehv_ehv = wkb_to_wkt(file, '/components_power/transformers/ehv_ehv')
        if not ehv_ehv.empty:
            grid_data.components_power.transformers.ehv_ehv = \
                grid_data.components_power.transformers.ehv_ehv.append(gpd.GeoDataFrame(ehv_ehv,
                                                                                        crs=crs))
        ehv_hv = wkb_to_wkt(file, '/components_power/transformers/ehv_hv')
        if not ehv_hv.empty:
            grid_data.components_power.transformers.ehv_hv = \
                grid_data.components_power.transformers.ehv_hv.append(gpd.GeoDataFrame(ehv_hv,
                                                                                       crs=crs))
        hv_mv = wkb_to_wkt(file, '/components_power/transformers/hv_mv')
        if not hv_mv.empty:
            grid_data.components_power.transformers.hv_mv = \
                grid_data.components_power.transformers.hv_mv.append(gpd.GeoDataFrame(hv_mv,
                                                                                      crs=crs))
        mv_lv = wkb_to_wkt(file, '/components_power/transformers/mv_lv')
        if not mv_lv.empty:
            grid_data.components_power.transformers.mv_lv = \
                grid_data.components_power.transformers.mv_lv.append(gpd.GeoDataFrame(mv_lv,
                                                                                      crs=crs))
        ehv_hv = wkb_to_wkt(file, '/components_power/substations/ehv_hv')
        if not ehv_hv.empty:
            grid_data.components_power.substations.ehv_hv = \
                grid_data.components_power.substations.ehv_hv.append(gpd.GeoDataFrame(ehv_hv,
                                                                                      crs=crs))
        hv_mv = wkb_to_wkt(file, '/components_power/substations/hv_mv')
        if not hv_mv.empty:
            grid_data.components_power.substations.hv_mv = \
                grid_data.components_power.substations.hv_mv.append(gpd.GeoDataFrame(hv_mv,
                                                                                     crs=crs))
        mv_lv = wkb_to_wkt(file, '/components_power/substations/mv_lv')
        if not mv_lv.empty:
            grid_data.components_power.substations.mv_lv = \
                grid_data.components_power.substations.mv_lv.append(gpd.GeoDataFrame(mv_lv,
                                                                                     crs=crs))
        # hp data
        hp_junctions = wkb_to_wkt(file, '/hp_data/hp_junctions')
        if not hp_junctions.empty:
            grid_data.hp_data.hp_junctions = grid_data.hp_data.hp_junctions.append(
                gpd.GeoDataFrame(hp_junctions, crs=crs))
        hp_pipes = wkb_to_wkt(file, '/hp_data/hp_pipes')
        if not hp_pipes.empty:
            grid_data.hp_data.hp_pipes = grid_data.hp_data.hp_pipes.append(gpd.GeoDataFrame(
                hp_pipes, crs=crs))
        # mp data
        mp_junctions = wkb_to_wkt(file, '/mp_data/mp_junctions')
        if not mp_junctions.empty:
            grid_data.mp_data.mp_junctions = grid_data.mp_data.mp_junctions.append(
                gpd.GeoDataFrame(mp_junctions, crs=crs))
        mp_pipes = wkb_to_wkt(file, '/mp_data/mp_pipes')
        if not mp_pipes.empty:
            grid_data.mp_data.mp_pipes = grid_data.mp_data.mp_pipes.append(gpd.GeoDataFrame(
                mp_pipes, crs=crs))
        # lp data
        lp_junctions = wkb_to_wkt(file, '/lp_data/lp_junctions')
        if not lp_junctions.empty:
            grid_data.lp_data.lp_junctions = grid_data.lp_data.lp_junctions.append(gpd.GeoDataFrame(
                lp_junctions, crs=crs))
        lp_pipes = wkb_to_wkt(file, '/lp_data/lp_pipes')
        if not lp_pipes.empty:
            grid_data.lp_data.lp_pipes = grid_data.lp_data.lp_pipes.append(gpd.GeoDataFrame(
                lp_pipes, crs=crs))
        # components gas
        compressors = wkb_to_wkt(file, '/components_gas/compressors')
        if not compressors.empty:
            grid_data.components_gas.compressors = grid_data.components_gas.compressors.append(
                gpd.GeoDataFrame(compressors, crs=crs))
        sources = wkb_to_wkt(file, '/components_gas/sources')
        if not sources.empty:
            grid_data.components_gas.sources = grid_data.components_gas.sources.append(
                gpd.GeoDataFrame(sources, crs=crs))
        storages_gas = wkb_to_wkt(file, '/components_gas/storages_gas')
        if not storages_gas.empty:
            grid_data.components_gas.storages_gas = grid_data.components_gas.storages_gas.append(
                gpd.GeoDataFrame(storages_gas, crs=crs))
        # dave version
        grid_data.dave_version = file.get('/dave_version')['dave_version'][0]
        # close file
        file.close()

        return grid_data
    else:
        print('Their is no suitable file at the given path')


def to_hdf(grid_data, dataset_path):
    """
    This functions stores a dave dataset at a given path in the HDF5 format
    """
    # --- create file
    archiv_file = pd.HDFStore(dataset_path)
    # area
    area = wkt_to_wkb(grid_data.area)
    archiv_file.put('/area', area)
    # target input
    archiv_file.put('/target_input', grid_data.target_input)
    # buildings
    archiv_file.put('/buildings/commercial', wkt_to_wkb(grid_data.buildings.commercial))
    archiv_file.put('/buildings/for_living', wkt_to_wkb(grid_data.buildings.for_living))
    archiv_file.put('/buildings/other', wkt_to_wkb(grid_data.buildings.other))
    # roads
    archiv_file.put('/roads/roads', wkt_to_wkb(grid_data.roads.roads))
    archiv_file.put('/roads/roads_plot', wkt_to_wkb(grid_data.roads.roads_plot))
    road_junctions = copy.deepcopy(grid_data.roads.road_junctions)
    if not road_junctions.empty:
        road_junctions = pd.DataFrame({'geometry': road_junctions})
        road_junctions['geometry'] = road_junctions.geometry.apply(dumps)
    else:
        road_junctions = pd.DataFrame([])
    archiv_file.put('/roads/road_junctions', road_junctions)
    # landuse
    archiv_file.put('/landuse', wkt_to_wkb(grid_data.landuse))
    # ehv data
    archiv_file.put('/ehv_data/ehv_lines', wkt_to_wkb(grid_data.ehv_data.ehv_lines))
    archiv_file.put('/ehv_data/ehv_nodes', wkt_to_wkb(grid_data.ehv_data.ehv_nodes))
    # hv data
    archiv_file.put('/hv_data/hv_nodes', wkt_to_wkb(grid_data.hv_data.hv_nodes))
    archiv_file.put('/hv_data/hv_lines', wkt_to_wkb(grid_data.hv_data.hv_lines))
    # mv data
    archiv_file.put('/mv_data/mv_nodes', wkt_to_wkb(grid_data.mv_data.mv_nodes))
    archiv_file.put('/mv_data/mv_lines', wkt_to_wkb(grid_data.mv_data.mv_lines))
    # lv data
    archiv_file.put('/lv_data/lv_nodes', wkt_to_wkb(grid_data.lv_data.lv_nodes))
    archiv_file.put('/lv_data/lv_lines', wkt_to_wkb(grid_data.lv_data.lv_lines))
    # components_power
    archiv_file.put('/components_power/conventional_powerplants',
                    wkt_to_wkb(grid_data.components_power.conventional_powerplants))
    archiv_file.put('/components_power/renewable_powerplants',
                    wkt_to_wkb(grid_data.components_power.renewable_powerplants))
    archiv_file.put('/components_power/loads', wkt_to_wkb(grid_data.components_power.loads))
    archiv_file.put('/components_power/transformers/ehv_ehv',
                    wkt_to_wkb(grid_data.components_power.transformers.ehv_ehv))
    archiv_file.put('/components_power/transformers/ehv_hv',
                    wkt_to_wkb(grid_data.components_power.transformers.ehv_hv))
    archiv_file.put('/components_power/transformers/hv_mv',
                    wkt_to_wkb(grid_data.components_power.transformers.hv_mv))
    archiv_file.put('/components_power/transformers/mv_lv',
                    wkt_to_wkb(grid_data.components_power.transformers.mv_lv))
    archiv_file.put('/components_power/substations/ehv_hv',
                    wkt_to_wkb(grid_data.components_power.substations.ehv_hv))
    archiv_file.put('/components_power/substations/hv_mv',
                    wkt_to_wkb(grid_data.components_power.substations.hv_mv))
    archiv_file.put('/components_power/substations/mv_lv',
                    wkt_to_wkb(grid_data.components_power.substations.mv_lv))
    # hp data
    archiv_file.put('/hp_data/hp_junctions', wkt_to_wkb(grid_data.hp_data.hp_junctions))
    archiv_file.put('/hp_data/hp_pipes', wkt_to_wkb(grid_data.hp_data.hp_pipes))
    # mp data
    archiv_file.put('/mp_data/mp_junctions', wkt_to_wkb(grid_data.mp_data.mp_junctions))
    archiv_file.put('/mp_data/mp_pipes', wkt_to_wkb(grid_data.mp_data.mp_pipes))
    # lp data
    archiv_file.put('/lp_data/lp_junctions', wkt_to_wkb(grid_data.lp_data.lp_junctions))
    archiv_file.put('/lp_data/lp_pipes', wkt_to_wkb(grid_data.lp_data.lp_pipes))
    # components gas
    archiv_file.put('/components_gas/compressors', wkt_to_wkb(grid_data.components_gas.compressors))
    archiv_file.put('/components_gas/sources', wkt_to_wkb(grid_data.components_gas.sources))
    archiv_file.put('/components_gas/storages_gas',
                    wkt_to_wkb(grid_data.components_gas.storages_gas))
    # dave version
    archiv_file.put('/dave_version', pd.DataFrame({'dave_version': grid_data.dave_version},
                                                  index=[0]))
    # close file
    archiv_file.close()


def pp_to_json(net, file_path):
    """
    This functions converts a pandapower model into a json file
    """
    # convert geometry
    if not net.bus.empty and all(list(map(lambda x: isinstance(x, Point), net.bus.geometry))):
        net.bus['geometry'] = net.bus.geometry.apply(lambda x: dumps(x, hex=True))
    if not net.line.empty and all(list(map(lambda x: isinstance(x, LineString) or
                                           isinstance(x, MultiLineString), net.line.geometry))):
        net.line['geometry'] = net.line.geometry.apply(lambda x: dumps(x, hex=True))
    if not net.trafo.empty and all(list(map(lambda x: isinstance(x, Point), net.trafo.geometry))):
        net.trafo['geometry'] = net.trafo.geometry.apply(lambda x: dumps(x, hex=True))
    if not net.gen.empty and all(list(map(lambda x: isinstance(x, Point), net.gen.geometry))):
        net.gen['geometry'] = net.gen.geometry.apply(lambda x: dumps(x, hex=True))
    if not net.sgen.empty and all(list(map(lambda x: isinstance(x, Point), net.sgen.geometry))):
        net.sgen['geometry'] = net.sgen.geometry.apply(lambda x: dumps(x, hex=True))
    # convert pp model to json and save the file
    to_json(net, filename=file_path)


def json_to_pp(file_path):
    # read json file and convert to pp model
    net = from_json(file_path)
    # convert geometry
    if not net.bus.empty and all(list(map(lambda x: isinstance(x, str), net.bus.geometry))):
        net.bus['geometry'] = net.bus.geometry.apply(lambda x: loads(x, hex=True))
    if not net.line.empty and all(list(map(lambda x: isinstance(x, str), net.line.geometry))):
        net.line['geometry'] = net.line.geometry.apply(lambda x: loads(x, hex=True))
    if not net.trafo.empty and all(list(map(lambda x: isinstance(x, str), net.trafo.geometry))):
        net.trafo['geometry'] = net.trafo.geometry.apply(lambda x: loads(x, hex=True))
    if not net.gen.empty and all(list(map(lambda x: isinstance(x, str), net.gen.geometry))):
        net.gen['geometry'] = net.gen.geometry.apply(lambda x: loads(x, hex=True))
    if not net.sgen.empty and all(list(map(lambda x: isinstance(x, str), net.sgen.geometry))):
        net.sgen['geometry'] = net.sgen.geometry.apply(lambda x: loads(x, hex=True))
    return net
