import geopandas as gpd
import pandas as pd
import os

import dave.create
from dave.datapool import convert_geometry_to_wkt

def _convert_data(file, key):
    data = file.get(key)
    if not data.empty and ('geometry' in data.keys()):
        data = convert_geometry_to_wkt(data)
    data = gpd.GeoDataFrame(data)
    return data


def read_dataset(dataset_path):
    """
    This functions reads a dave dataset from a user given path
    
    Output  grid_data - dave dataset
    
    Example  grid_data = read_dataset(dataset_path)
    """
    crs='EPSG:4326'
    # check if file exist
    if os.path.exists(dataset_path):
        # read data
        file = pd.HDFStore(dataset_path)
        # create empty dave dataset
        grid_data = dave.create.create_empty_dataset()
        # --- create dave dataset from archiv file
        # area
        area = _convert_data(file, '/area')
        area = gpd.GeoDataFrame(area, crs=crs)
        grid_data.area = grid_data.area.append(area)
        # target input
        grid_data.target_input = grid_data.target_input.append(file.get('/target_input'))
        # buildings
        commercial = _convert_data(file, '/buildings/commercial')
        commercial = gpd.GeoDataFrame(commercial, crs=crs)
        grid_data.buildings.commercial = grid_data.buildings.commercial.append(commercial)
        for_living = _convert_data(file, '/buildings/for_living')
        for_living = gpd.GeoDataFrame(for_living, crs=crs)
        grid_data.buildings.for_living = grid_data.buildings.for_living.append(for_living)
        other = _convert_data(file, '/buildings/other')
        other = gpd.GeoDataFrame(other, crs=crs)
        grid_data.buildings.other = grid_data.buildings.other.append(other)
        # roads
        roads = _convert_data(file, '/roads/roads')
        roads = gpd.GeoDataFrame(roads, crs=crs)
        grid_data.roads.roads = grid_data.roads.roads.append(roads)
        roads_plot = _convert_data(file, '/roads/roads_plot')
        roads_plot = gpd.GeoDataFrame(roads_plot, crs=crs)
        grid_data.roads.roads_plot = grid_data.roads.roads_plot.append(roads_plot)
        road_junctions = _convert_data(file, '/roads/road_junctions')
        if not road_junctions.empty:
            road_junctions = road_junctions['geometry']
            road_junctions = gpd.GeoSeries(road_junctions, crs=crs)
            grid_data.roads.road_junctions = grid_data.roads.road_junctions.append(road_junctions)
        # landuse
        landuse = _convert_data(file, '/landuse')
        landuse = gpd.GeoDataFrame(landuse, crs=crs)
        grid_data.landuse = grid_data.landuse.append(landuse)
        # ehv data
        ehv_lines = _convert_data(file, '/ehv_data/ehv_lines')
        ehv_lines = gpd.GeoDataFrame(ehv_lines, crs=crs)
        grid_data.ehv_data.ehv_lines = grid_data.ehv_data.ehv_lines.append(ehv_lines)
        ehv_nodes = _convert_data(file, '/ehv_data/ehv_nodes')
        ehv_nodes = gpd.GeoDataFrame(ehv_nodes, crs=crs)
        grid_data.ehv_data.ehv_nodes = grid_data.ehv_data.ehv_nodes.append(ehv_nodes)
        ehv_substations = _convert_data(file, '/ehv_data/ehv_substations')
        ehv_substations = gpd.GeoDataFrame(ehv_substations, crs=crs)
        grid_data.ehv_data.ehv_substations = grid_data.ehv_data.ehv_substations.append(ehv_substations)
        # hv data
        hv_nodes = _convert_data(file, '/hv_data/hv_nodes')
        hv_nodes = gpd.GeoDataFrame(hv_nodes, crs=crs)
        grid_data.hv_data.hv_nodes = grid_data.hv_data.hv_nodes.append(hv_nodes)
        hv_lines = _convert_data(file, '/hv_data/hv_lines')
        hv_lines = gpd.GeoDataFrame(hv_lines, crs=crs)
        grid_data.hv_data.hv_lines = grid_data.hv_data.hv_lines.append(hv_lines)
        # mv data
        mv_nodes = _convert_data(file, '/mv_data/mv_nodes')
        mv_nodes = gpd.GeoDataFrame(mv_nodes, crs=crs)
        grid_data.mv_data.mv_nodes = grid_data.mv_data.mv_nodes.append(mv_nodes)
        mv_lines = _convert_data(file, '/mv_data/mv_lines')
        mv_lines = gpd.GeoDataFrame(mv_lines, crs=crs)
        grid_data.mv_data.mv_lines = grid_data.mv_data.mv_lines.append(mv_lines)
        # lv data
        lv_nodes = _convert_data(file, '/lv_data/lv_nodes')
        lv_nodes = gpd.GeoDataFrame(lv_nodes, crs=crs)
        grid_data.lv_data.lv_nodes = grid_data.lv_data.lv_nodes.append(lv_nodes)
        lv_lines = _convert_data(file, '/lv_data/lv_lines')
        lv_lines = gpd.GeoDataFrame(lv_lines, crs=crs)
        grid_data.lv_data.lv_lines = grid_data.lv_data.lv_lines.append(lv_lines)
        # components_power
        conventional_powerplants = _convert_data(file, '/components_power/conventional_powerplants')
        conventional_powerplants = gpd.GeoDataFrame(conventional_powerplants, crs=crs)
        grid_data.components_power.conventional_powerplants = grid_data.components_power.conventional_powerplants.append(conventional_powerplants)
        renewable_powerplants = _convert_data(file, '/components_power/renewable_powerplants')
        renewable_powerplants = gpd.GeoDataFrame(renewable_powerplants, crs=crs)
        grid_data.components_power.renewable_powerplants = grid_data.components_power.renewable_powerplants.append(renewable_powerplants)
        loads = _convert_data(file, '/components_power/loads')
        loads = gpd.GeoDataFrame(loads, crs=crs)
        grid_data.components_power.loads = grid_data.components_power.loads.append(loads)
        ehv_ehv = _convert_data(file, '/components_power/transformers/ehv_ehv')
        ehv_ehv = gpd.GeoDataFrame(ehv_ehv, crs=crs)
        grid_data.components_power.transformers.ehv_ehv = grid_data.components_power.transformers.ehv_ehv.append(ehv_ehv)
        ehv_hv = _convert_data(file, '/components_power/transformers/ehv_hv')
        ehv_hv = gpd.GeoDataFrame(ehv_hv, crs=crs)
        grid_data.components_power.transformers.ehv_hv = grid_data.components_power.transformers.ehv_hv.append(ehv_hv)
        hv_mv = _convert_data(file, '/components_power/transformers/hv_mv')
        hv_mv = gpd.GeoDataFrame(hv_mv, crs=crs)
        grid_data.components_power.transformers.hv_mv = grid_data.components_power.transformers.hv_mv.append(hv_mv)
        mv_lv = _convert_data(file, '/components_power/transformers/mv_lv')
        mv_lv = gpd.GeoDataFrame(mv_lv, crs=crs)
        grid_data.components_power.transformers.mv_lv = grid_data.components_power.transformers.mv_lv.append(mv_lv)
        # hp data
        hp_junctions = _convert_data(file, '/hp_data/hp_junctions')
        hp_junctions = gpd.GeoDataFrame(hp_junctions, crs=crs)
        grid_data.hp_data.hp_junctions = grid_data.hp_data.hp_junctions.append(hp_junctions)
        hp_pipes = _convert_data(file, '/hp_data/hp_pipes')
        hp_pipes = gpd.GeoDataFrame(hp_pipes, crs=crs)
        grid_data.hp_data.hp_pipes = grid_data.hp_data.hp_pipes.append(hp_pipes)
        # mp data
        mp_junctions = _convert_data(file, '/mp_data/mp_junctions')
        mp_junctions = gpd.GeoDataFrame(mp_junctions, crs=crs)
        grid_data.mp_data.mp_junctions = grid_data.mp_data.mp_junctions.append(mp_junctions)
        mp_pipes = _convert_data(file, '/mp_data/mp_pipes')
        mp_pipes = gpd.GeoDataFrame(mp_pipes, crs=crs)
        grid_data.mp_data.mp_pipes = grid_data.mp_data.mp_pipes.append(mp_pipes)
        # lp data
        lp_junctions = _convert_data(file, '/lp_data/lp_junctions')
        lp_junctions = gpd.GeoDataFrame(lp_junctions, crs=crs)
        grid_data.lp_data.lp_junctions = grid_data.lp_data.lp_junctions.append(lp_junctions)
        lp_pipes = _convert_data(file, '/lp_data/lp_pipes')
        lp_pipes = gpd.GeoDataFrame(lp_pipes, crs=crs)
        grid_data.lp_data.lp_pipes = grid_data.lp_data.lp_pipes.append(lp_pipes)
        # components gas
        sinks = _convert_data(file, '/components_gas/sinks')
        sinks = gpd.GeoDataFrame(sinks, crs=crs)
        grid_data.components_gas.sinks = grid_data.components_gas.sinks.append(sinks)
        sources = _convert_data(file, '/components_gas/sources')
        sources = gpd.GeoDataFrame(sources, crs=crs)
        grid_data.components_gas.sources = grid_data.components_gas.sources.append(sources)
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
    area = _convert_to_archiv_data(grid_data.area)
    archiv_file.put('/area', area)
    # target input
    archiv_file.put('/target_input', grid_data.target_input)
    # buildings
    commercial = _convert_to_archiv_data(grid_data.buildings.commercial)
    archiv_file.put('/buildings/commercial', commercial)
    for_living = _convert_to_archiv_data(grid_data.buildings.for_living)
    archiv_file.put('/buildings/for_living', for_living)
    other = _convert_to_archiv_data(grid_data.buildings.other)
    archiv_file.put('/buildings/other', other)
    # roads
    roads = _convert_to_archiv_data(grid_data.roads.roads)
    archiv_file.put('/roads/roads', roads)
    roads_plot = _convert_to_archiv_data(grid_data.roads.roads_plot)
    archiv_file.put('/roads/roads_plot', roads_plot)
    road_junctions = copy.deepcopy(grid_data.roads.road_junctions)
    if not road_junctions.empty:
        road_junctions = pd.DataFrame({'geometry': road_junctions})
        road_junctions = convert_geometry_to_wkb(road_junctions)
    else:
        road_junctions = pd.DataFrame([])
    archiv_file.put('/roads/road_junctions', road_junctions)
    # landuse
    landuse = _convert_to_archiv_data(grid_data.landuse)
    archiv_file.put('/landuse', landuse)
    # ehv data
    ehv_lines = _convert_to_archiv_data(grid_data.ehv_data.ehv_lines)
    archiv_file.put('/ehv_data/ehv_lines', ehv_lines)
    ehv_nodes = _convert_to_archiv_data(grid_data.ehv_data.ehv_nodes)
    archiv_file.put('/ehv_data/ehv_nodes', ehv_nodes)
    ehv_substations = _convert_to_archiv_data(grid_data.ehv_data.ehv_substations)
    archiv_file.put('/ehv_data/ehv_substations', ehv_substations)
    # hv data
    hv_nodes = _convert_to_archiv_data(grid_data.hv_data.hv_nodes)
    archiv_file.put('/hv_data/hv_nodes', hv_nodes)
    hv_lines = _convert_to_archiv_data(grid_data.hv_data.hv_lines)
    archiv_file.put('/hv_data/hv_lines', hv_lines)
    # mv data
    mv_nodes = _convert_to_archiv_data(grid_data.mv_data.mv_nodes)
    archiv_file.put('/mv_data/mv_nodes', mv_nodes)
    mv_lines = _convert_to_archiv_data(grid_data.mv_data.mv_lines)
    archiv_file.put('/mv_data/mv_lines', mv_lines)
    # lv data
    lv_nodes = _convert_to_archiv_data(grid_data.lv_data.lv_nodes)
    archiv_file.put('/lv_data/lv_nodes', lv_nodes)
    lv_lines = _convert_to_archiv_data(grid_data.lv_data.lv_lines)
    archiv_file.put('/lv_data/lv_lines', lv_lines)
    # components_power
    conventional_powerplants = _convert_to_archiv_data(grid_data.components_power.conventional_powerplants)
    archiv_file.put('/components_power/conventional_powerplants', conventional_powerplants)
    renewable_powerplants = _convert_to_archiv_data(grid_data.components_power.renewable_powerplants)
    archiv_file.put('/components_power/renewable_powerplants', renewable_powerplants)
    loads = _convert_to_archiv_data(grid_data.components_power.loads)
    archiv_file.put('/components_power/loads', loads)
    ehv_ehv = _convert_to_archiv_data(grid_data.components_power.transformers.ehv_ehv)
    archiv_file.put('/components_power/transformers/ehv_ehv', ehv_ehv)
    ehv_hv = _convert_to_archiv_data(grid_data.components_power.transformers.ehv_hv)
    archiv_file.put('/components_power/transformers/ehv_hv', ehv_hv)
    hv_mv = _convert_to_archiv_data(grid_data.components_power.transformers.hv_mv)
    archiv_file.put('/components_power/transformers/hv_mv', hv_mv)
    mv_lv = _convert_to_archiv_data(grid_data.components_power.transformers.mv_lv)
    archiv_file.put('/components_power/transformers/mv_lv', mv_lv)
    # hp data
    hp_junctions = _convert_to_archiv_data(grid_data.hp_data.hp_junctions)
    archiv_file.put('/hp_data/hp_junctions', hp_junctions)
    hp_pipes = _convert_to_archiv_data(grid_data.hp_data.hp_pipes)
    archiv_file.put('/hp_data/hp_pipes', hp_pipes)
    # mp data
    mp_junctions = _convert_to_archiv_data(grid_data.mp_data.mp_junctions)
    archiv_file.put('/mp_data/mp_junctions', mp_junctions)
    mp_pipes = _convert_to_archiv_data(grid_data.mp_data.mp_pipes)
    archiv_file.put('/mp_data/mp_pipes', mp_pipes)
    # lp data
    lp_junctions = _convert_to_archiv_data(grid_data.lp_data.lp_junctions)
    archiv_file.put('/lp_data/lp_junctions', lp_junctions)
    lp_pipes = _convert_to_archiv_data(grid_data.lp_data.lp_pipes)
    archiv_file.put('/lp_data/lp_pipes', lp_pipes)
    # components gas
    sinks = _convert_to_archiv_data(grid_data.components_gas.sinks)
    archiv_file.put('/components_gas/sinks', sinks)
    sources = _convert_to_archiv_data(grid_data.components_gas.sources)
    archiv_file.put('/components_gas/sources', sources)
    # dave version
    dave_version = pd.DataFrame({'dave_version': grid_data.dave_version}, index=[0])
    archiv_file.put('/dave_version', dave_version)
    # close file
    archiv_file.close()

