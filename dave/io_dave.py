import geopandas as gpd
import pandas as pd
import os
import copy
from pandapower import to_json
from shapely.wkb import loads, dumps

import dave.create
from dave.settings import dave_settings


def _convert_data_from(file, key):
    data = file.get(key)
    if (not data.empty) and ('geometry' in data.keys()):
        data['geometry'] = data.geometry.apply(lambda x: loads(x))
    data = gpd.GeoDataFrame(data)
    return data


def _convert_data_to(data_key):
    data = copy.deepcopy(data_key)
    if not data.empty:
        if 'geometry' in data.keys():
            data['geometry'] = data.geometry.apply(lambda x: dumps(x))
        data = pd.DataFrame(data)
    else:
        data = pd.DataFrame([])
    return data


def read_dataset(dataset_path):
    """
    This functions reads a dave dataset from a user given path

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
        area = _convert_data_from(file, '/area')
        area = gpd.GeoDataFrame(area, crs=crs)
        grid_data.area = grid_data.area.append(area)
        # target input
        grid_data.target_input = grid_data.target_input.append(file.get('/target_input'))
        # buildings
        commercial = _convert_data_from(file, '/buildings/commercial')
        if not commercial.empty:
            commercial = gpd.GeoDataFrame(commercial, crs=crs)
            grid_data.buildings.commercial = grid_data.buildings.commercial.append(commercial)
        for_living = _convert_data_from(file, '/buildings/for_living')
        if not for_living.empty:
            for_living = gpd.GeoDataFrame(for_living, crs=crs)
            grid_data.buildings.for_living = grid_data.buildings.for_living.append(for_living)
        other = _convert_data_from(file, '/buildings/other')
        if not other.empty:
            other = gpd.GeoDataFrame(other, crs=crs)
            grid_data.buildings.other = grid_data.buildings.other.append(other)
        # roads
        roads = _convert_data_from(file, '/roads/roads')
        if not roads.empty:
            roads = gpd.GeoDataFrame(roads, crs=crs)
            grid_data.roads.roads = grid_data.roads.roads.append(roads)
        roads_plot = _convert_data_from(file, '/roads/roads_plot')
        if not roads_plot.empty:
            roads_plot = gpd.GeoDataFrame(roads_plot, crs=crs)
            grid_data.roads.roads_plot = grid_data.roads.roads_plot.append(roads_plot)
        road_junctions = _convert_data_from(file, '/roads/road_junctions')
        if not road_junctions.empty:
            road_junctions = road_junctions['geometry']
            road_junctions = gpd.GeoSeries(road_junctions, crs=crs)
            grid_data.roads.road_junctions = grid_data.roads.road_junctions.append(road_junctions)
        # landuse
        landuse = _convert_data_from(file, '/landuse')
        if not landuse.empty:
            landuse = gpd.GeoDataFrame(landuse, crs=crs)
            grid_data.landuse = grid_data.landuse.append(landuse)
        # ehv data
        ehv_lines = _convert_data_from(file, '/ehv_data/ehv_lines')
        if not ehv_lines.empty:
            ehv_lines = gpd.GeoDataFrame(ehv_lines, crs=crs)
            grid_data.ehv_data.ehv_lines = grid_data.ehv_data.ehv_lines.append(ehv_lines)
        ehv_nodes = _convert_data_from(file, '/ehv_data/ehv_nodes')
        if not ehv_nodes.empty:
            ehv_nodes = gpd.GeoDataFrame(ehv_nodes, crs=crs)
            grid_data.ehv_data.ehv_nodes = grid_data.ehv_data.ehv_nodes.append(ehv_nodes)
        ehv_substations = _convert_data_from(file, '/ehv_data/ehv_substations')
        if not ehv_substations.empty:
            ehv_substations = gpd.GeoDataFrame(ehv_substations, crs=crs)
            grid_data.ehv_data.ehv_substations = grid_data.ehv_data.ehv_substations.append(ehv_substations)
        # hv data
        hv_nodes = _convert_data_from(file, '/hv_data/hv_nodes')
        if not hv_nodes.empty:
            hv_nodes = gpd.GeoDataFrame(hv_nodes, crs=crs)
            grid_data.hv_data.hv_nodes = grid_data.hv_data.hv_nodes.append(hv_nodes)
        hv_lines = _convert_data_from(file, '/hv_data/hv_lines')
        if not hv_lines.empty:
            hv_lines = gpd.GeoDataFrame(hv_lines, crs=crs)
            grid_data.hv_data.hv_lines = grid_data.hv_data.hv_lines.append(hv_lines)
        # mv data
        mv_nodes = _convert_data_from(file, '/mv_data/mv_nodes')
        if not mv_nodes.empty:
            mv_nodes = gpd.GeoDataFrame(mv_nodes, crs=crs)
            grid_data.mv_data.mv_nodes = grid_data.mv_data.mv_nodes.append(mv_nodes)
        mv_lines = _convert_data_from(file, '/mv_data/mv_lines')
        if not mv_lines.empty:
            mv_lines = gpd.GeoDataFrame(mv_lines, crs=crs)
            grid_data.mv_data.mv_lines = grid_data.mv_data.mv_lines.append(mv_lines)
        # lv data
        lv_nodes = _convert_data_from(file, '/lv_data/lv_nodes')
        if not lv_nodes.empty:
            lv_nodes = gpd.GeoDataFrame(lv_nodes, crs=crs)
            grid_data.lv_data.lv_nodes = grid_data.lv_data.lv_nodes.append(lv_nodes)
        lv_lines = _convert_data_from(file, '/lv_data/lv_lines')
        if not lv_lines.empty:
            lv_lines = gpd.GeoDataFrame(lv_lines, crs=crs)
            grid_data.lv_data.lv_lines = grid_data.lv_data.lv_lines.append(lv_lines)
        # components_power
        conventional_powerplants = _convert_data_from(file, '/components_power/conventional_powerplants')
        if not conventional_powerplants.empty:
            conventional_powerplants = gpd.GeoDataFrame(conventional_powerplants, crs=crs)
            grid_data.components_power.conventional_powerplants = grid_data.components_power.conventional_powerplants.append(conventional_powerplants)
        renewable_powerplants = _convert_data_from(file, '/components_power/renewable_powerplants')
        if not renewable_powerplants.empty:
            renewable_powerplants = gpd.GeoDataFrame(renewable_powerplants, crs=crs)
            grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(renewable_powerplants)
        loads = _convert_data_from(file, '/components_power/loads')
        if not loads.empty:
            loads = gpd.GeoDataFrame(loads)
            grid_data.components_power.loads = grid_data.components_power.loads.append(loads)
        ehv_ehv = _convert_data_from(file, '/components_power/transformers/ehv_ehv')
        if not ehv_ehv.empty:
            ehv_ehv = gpd.GeoDataFrame(ehv_ehv, crs=crs)
            grid_data.components_power.transformers.ehv_ehv = grid_data.components_power.transformers.ehv_ehv.append(ehv_ehv)
        ehv_hv = _convert_data_from(file, '/components_power/transformers/ehv_hv')
        if not ehv_hv.empty:
            ehv_hv = gpd.GeoDataFrame(ehv_hv, crs=crs)
            grid_data.components_power.transformers.ehv_hv = grid_data.components_power.transformers.ehv_hv.append(ehv_hv)
        hv_mv = _convert_data_from(file, '/components_power/transformers/hv_mv')
        if not hv_mv.empty:
            hv_mv = gpd.GeoDataFrame(hv_mv, crs=crs)
            grid_data.components_power.transformers.hv_mv = grid_data.components_power.transformers.hv_mv.append(hv_mv)
        mv_lv = _convert_data_from(file, '/components_power/transformers/mv_lv')
        if not mv_lv.empty:
            mv_lv = gpd.GeoDataFrame(mv_lv, crs=crs)
            grid_data.components_power.transformers.mv_lv = grid_data.components_power.transformers.mv_lv.append(mv_lv)
        # hp data
        hp_junctions = _convert_data_from(file, '/hp_data/hp_junctions')
        if not hp_junctions.empty:
            hp_junctions = gpd.GeoDataFrame(hp_junctions, crs=crs)
            grid_data.hp_data.hp_junctions = grid_data.hp_data.hp_junctions.append(hp_junctions)
        hp_pipes = _convert_data_from(file, '/hp_data/hp_pipes')
        if not hp_pipes.empty:
            hp_pipes = gpd.GeoDataFrame(hp_pipes, crs=crs)
            grid_data.hp_data.hp_pipes = grid_data.hp_data.hp_pipes.append(hp_pipes)
        # mp data
        mp_junctions = _convert_data_from(file, '/mp_data/mp_junctions')
        if not mp_junctions.empty:
            mp_junctions = gpd.GeoDataFrame(mp_junctions, crs=crs)
            grid_data.mp_data.mp_junctions = grid_data.mp_data.mp_junctions.append(mp_junctions)
        mp_pipes = _convert_data_from(file, '/mp_data/mp_pipes')
        if not mp_pipes.empty:
            mp_pipes = gpd.GeoDataFrame(mp_pipes, crs=crs)
            grid_data.mp_data.mp_pipes = grid_data.mp_data.mp_pipes.append(mp_pipes)
        # lp data
        lp_junctions = _convert_data_from(file, '/lp_data/lp_junctions')
        if not lp_junctions.empty:
            lp_junctions = gpd.GeoDataFrame(lp_junctions, crs=crs)
            grid_data.lp_data.lp_junctions = grid_data.lp_data.lp_junctions.append(lp_junctions)
        lp_pipes = _convert_data_from(file, '/lp_data/lp_pipes')
        if not lp_pipes.empty:
            lp_pipes = gpd.GeoDataFrame(lp_pipes, crs=crs)
            grid_data.lp_data.lp_pipes = grid_data.lp_data.lp_pipes.append(lp_pipes)
        # components gas
        compressors = _convert_data_from(file, '/components_gas/compressors')
        if not compressors.empty:
            compressors = gpd.GeoDataFrame(compressors, crs=crs)
            grid_data.components_gas.compressors = grid_data.components_gas.compressors.append(compressors)
        sources = _convert_data_from(file, '/components_gas/sources')
        if not sources.empty:
            sources = gpd.GeoDataFrame(sources, crs=crs)
            grid_data.components_gas.sources = grid_data.components_gas.sources.append(sources)
        storages_gas = _convert_data_from(file, '/components_gas/storages_gas')
        if not storages_gas.empty:
            storages_gas = gpd.GeoDataFrame(storages_gas, crs=crs)
            grid_data.components_gas.storages_gas = grid_data.components_gas.storages_gas.append(storages_gas)
        # dave version
        dave_version = file.get('/dave_version')['dave_version'][0]
        grid_data.dave_version = dave_version
        # close file
        file.close()

        return grid_data
    else:
        print('Their is no suitable file at the given path')


def write_dataset(grid_data, dataset_path):
    """
    This functions stores a dave dataset at a given path
    """
    # --- create file
    archiv_file = pd.HDFStore(dataset_path)
    # area
    area = _convert_data_to(grid_data.area)
    archiv_file.put('/area', area)
    # target input
    archiv_file.put('/target_input', grid_data.target_input)
    # buildings
    commercial = _convert_data_to(grid_data.buildings.commercial)
    archiv_file.put('/buildings/commercial', commercial)
    for_living = _convert_data_to(grid_data.buildings.for_living)
    archiv_file.put('/buildings/for_living', for_living)
    other = _convert_data_to(grid_data.buildings.other)
    archiv_file.put('/buildings/other', other)
    # roads
    roads = _convert_data_to(grid_data.roads.roads)
    archiv_file.put('/roads/roads', roads)
    roads_plot = _convert_data_to(grid_data.roads.roads_plot)
    archiv_file.put('/roads/roads_plot', roads_plot)
    road_junctions = copy.deepcopy(grid_data.roads.road_junctions)
    if not road_junctions.empty:
        road_junctions = pd.DataFrame({'geometry': road_junctions})
        road_junctions['geometry'] = road_junctions.geometry.apply(lambda x: dumps(x))
    else:
        road_junctions = pd.DataFrame([])
    archiv_file.put('/roads/road_junctions', road_junctions)
    # landuse
    landuse = _convert_data_to(grid_data.landuse)
    archiv_file.put('/landuse', landuse)
    # ehv data
    ehv_lines = _convert_data_to(grid_data.ehv_data.ehv_lines)
    archiv_file.put('/ehv_data/ehv_lines', ehv_lines)
    ehv_nodes = _convert_data_to(grid_data.ehv_data.ehv_nodes)
    archiv_file.put('/ehv_data/ehv_nodes', ehv_nodes)
    ehv_substations = _convert_data_to(grid_data.ehv_data.ehv_substations)
    archiv_file.put('/ehv_data/ehv_substations', ehv_substations)
    # hv data
    hv_nodes = _convert_data_to(grid_data.hv_data.hv_nodes)
    archiv_file.put('/hv_data/hv_nodes', hv_nodes)
    hv_lines = _convert_data_to(grid_data.hv_data.hv_lines)
    archiv_file.put('/hv_data/hv_lines', hv_lines)
    # mv data
    mv_nodes = _convert_data_to(grid_data.mv_data.mv_nodes)
    archiv_file.put('/mv_data/mv_nodes', mv_nodes)
    mv_lines = _convert_data_to(grid_data.mv_data.mv_lines)
    archiv_file.put('/mv_data/mv_lines', mv_lines)
    # lv data
    lv_nodes = _convert_data_to(grid_data.lv_data.lv_nodes)
    archiv_file.put('/lv_data/lv_nodes', lv_nodes)
    lv_lines = _convert_data_to(grid_data.lv_data.lv_lines)
    archiv_file.put('/lv_data/lv_lines', lv_lines)
    # components_power
    conventional_powerplants = _convert_data_to(grid_data.components_power.conventional_powerplants)
    archiv_file.put('/components_power/conventional_powerplants', conventional_powerplants)
    renewable_powerplants = _convert_data_to(grid_data.components_power.renewable_powerplants)
    archiv_file.put('/components_power/renewable_powerplants', renewable_powerplants)
    loads = _convert_data_to(grid_data.components_power.loads)
    archiv_file.put('/components_power/loads', loads)
    ehv_ehv = _convert_data_to(grid_data.components_power.transformers.ehv_ehv)
    archiv_file.put('/components_power/transformers/ehv_ehv', ehv_ehv)
    ehv_hv = _convert_data_to(grid_data.components_power.transformers.ehv_hv)
    archiv_file.put('/components_power/transformers/ehv_hv', ehv_hv)
    hv_mv = _convert_data_to(grid_data.components_power.transformers.hv_mv)
    archiv_file.put('/components_power/transformers/hv_mv', hv_mv)
    mv_lv = _convert_data_to(grid_data.components_power.transformers.mv_lv)
    archiv_file.put('/components_power/transformers/mv_lv', mv_lv)
    # hp data
    hp_junctions = _convert_data_to(grid_data.hp_data.hp_junctions)
    archiv_file.put('/hp_data/hp_junctions', hp_junctions)
    hp_pipes = _convert_data_to(grid_data.hp_data.hp_pipes)
    archiv_file.put('/hp_data/hp_pipes', hp_pipes)
    # mp data
    mp_junctions = _convert_data_to(grid_data.mp_data.mp_junctions)
    archiv_file.put('/mp_data/mp_junctions', mp_junctions)
    mp_pipes = _convert_data_to(grid_data.mp_data.mp_pipes)
    archiv_file.put('/mp_data/mp_pipes', mp_pipes)
    # lp data
    lp_junctions = _convert_data_to(grid_data.lp_data.lp_junctions)
    archiv_file.put('/lp_data/lp_junctions', lp_junctions)
    lp_pipes = _convert_data_to(grid_data.lp_data.lp_pipes)
    archiv_file.put('/lp_data/lp_pipes', lp_pipes)
    # components gas
    compressors = _convert_data_to(grid_data.components_gas.compressors)
    archiv_file.put('/components_gas/compressors', compressors)
    sources = _convert_data_to(grid_data.components_gas.sources)
    archiv_file.put('/components_gas/sources', sources)
    storages_gas = _convert_data_to(grid_data.components_gas.storages_gas)
    archiv_file.put('/components_gas/storages_gas', storages_gas)
    # dave version
    dave_version = pd.DataFrame({'dave_version': grid_data.dave_version}, index=[0])
    archiv_file.put('/dave_version', dave_version)
    # close file
    archiv_file.close()


def pp_to_json(net_power, file_path):
    """
    This functions converts a pandapower model into a json file
    """
    # convert geometry
    if not net_power.trafo.empty:
        net_power.trafo['geometry'] = net_power.trafo.geometry.apply(lambda x: dumps(x, hex=True))
    if not net_power.gen.empty:
        net_power.gen['geometry'] = net_power.gen.geometry.apply(lambda x: dumps(x, hex=True))
    if not net_power.sgen.empty:
        net_power.sgen['geometry'] = net_power.sgen.geometry.apply(lambda x: dumps(x, hex=True))
    to_json(net_power, filename=file_path)
