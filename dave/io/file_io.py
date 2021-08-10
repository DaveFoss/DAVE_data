import json
import os
import geopandas as gpd
import pandas as pd
from pandapower import to_json, from_json
from shapely.wkb import loads, dumps
from shapely.geometry import Point, LineString, MultiLineString

import dave.create
from dave.settings import dave_settings
from dave.datapool import get_data_path
from dave.io.convert_format import wkb_to_wkt, wkt_to_wkb, wkt_to_wkb_dataset
from dave.io.io_utils import archiv_inventory, DaVeJSONEncoder, encrypt_string
from dave.dave_structure import davestructure


def to_json(grid_data, file_path=None, encryption_key=None):
    """
    This function converts the DaVe dataset into the JSON format.
    Input:
        grid data
        file_path - absoulut path of the file. If None is given the function returns a JSON string
    """
    # convert geometric data in dave dataset
    grid_data_geo = wkt_to_wkb_dataset(grid_data)
    # convert DaVe dataset into a json string with custom encoder
    json_string = json.dumps(grid_data_geo, cls=DaVeJSONEncoder, indent=2)
    # encrypt json string
    if encryption_key is not None:
        json_string = encrypt_string(json_string, encryption_key)
    # only return json string
    if file_path is None:
        return json_string
    # save json string at given file path
    if hasattr(file_path, 'write'):
        file_path.write(json_string)
    else:
        with open(file_path, "w"):
            file_path.write(json_string)


def from_hdf(dataset_path):
    """
    This functions reads a dave dataset in HDF5 format from a user given path

    Output  grid_data - dave dataset

    Example  grid_data = read_dataset(dataset_path)
    """
    crs = dave_settings()['crs_main']
    # check if path exist
    if os.path.exists(dataset_path):
        # create empty dave dataset
        grid_data = dave.create.create_empty_dataset()
        # open hdf file
        file = pd.HDFStore(dataset_path)
        # --- create dave dataset from archiv file
        for key in file.keys():
            # read data from file and convert geometry
            data = file.get(key)
            if 'geometry' in data.keys():
                data = wkb_to_wkt(data, crs)
            if not data.empty:
                # seperate the keys
                key_parts = key[1:].split('/')
                # assign data to the dave dataset
                if len(key_parts) == 1:
                    if key_parts[0] == 'dave_version':
                        grid_data.dave_version = data['dave_version'][0]
                    else:
                        grid_data[key_parts[0]] = grid_data[key_parts[0]].append(data)
                elif len(key_parts) == 2:
                    grid_data[key_parts[0]][key_parts[1]] = grid_data[
                        key_parts[0]][key_parts[1]].append(data)
                elif len(key_parts) == 3:
                    grid_data[key_parts[0]][key_parts[1]][key_parts[2]] = grid_data[
                        key_parts[0]][key_parts[1]][key_parts[2]].append(data)
        # close file
        file.close()
        return grid_data
    else:
        print('Their is no suitable file at the given path')


def to_hdf(grid_data, dataset_path):
    """
    This functions stores a dave dataset at a given path in the HDF5 format
    """
    # create hdf file
    file = pd.HDFStore(dataset_path)
    # go trough the dave dataset keys and save each data in the hdf5 file
    for key in grid_data.keys():
        if isinstance(grid_data[key], davestructure):
            for key_sec in grid_data[key].keys():
                if isinstance(grid_data[key][key_sec], davestructure):
                    for key_trd in grid_data[key][key_sec].keys():
                        if isinstance(grid_data[key][key_sec][key_trd], gpd.GeoDataFrame):
                            file.put(f'/{key}/{key_sec}/{key_trd}',
                                     wkt_to_wkb(grid_data[key][key_sec][key_trd]))
                elif isinstance(grid_data[key][key_sec], gpd.GeoDataFrame):
                    file.put(f'/{key}/{key_sec}', wkt_to_wkb(grid_data[key][key_sec]))
                elif isinstance(grid_data[key][key_sec], gpd.GeoSeries):
                    if not grid_data[key][key_sec].empty:
                        data = pd.DataFrame({'geometry': grid_data[key][key_sec]})
                        data['geometry'] = data.geometry.apply(dumps)
                        file.put(f'/{key}/{key_sec}', data)
                elif isinstance(grid_data[key][key_sec], pd.DataFrame):
                    file.put(f'/{key}/{key_sec}', grid_data[key][key_sec])
        elif isinstance(grid_data[key], gpd.GeoDataFrame):
            file.put(f'/{key}', wkt_to_wkb(grid_data[key]))
        elif isinstance(grid_data[key], pd.DataFrame):
            file.put(f'/{key}', grid_data[key])
        elif isinstance(grid_data[key], str):
            file.put(f'/{key}', pd.DataFrame({key: grid_data[key]}, index=[0]))
    # close file
    file.close()


def from_archiv(dataset_name):
    """
    This functions reads a dave dataset from the dave internal archiv
    """
    crs = 'EPSG:4326'
    # check if file exist
    files_in_archiv = os.listdir(get_data_path(dirname='dave_archiv'))
    if dataset_name in files_in_archiv:
        # read data
        archiv_file = pd.HDFStore(get_data_path(dataset_name, 'dave_archiv'))
        # create empty dave dataset
        grid_data = dave.create.create_empty_dataset()
        # --- create dave dataset from archiv file
        # area
        grid_data.area = grid_data.area.append(
            gpd.GeoDataFrame(wkb_to_wkt(archiv_file, '/area'), crs=crs))
        # target input
        grid_data.target_input = grid_data.target_input.append(archiv_file.get('/target_input'))
        # buildings
        grid_data.buildings.commercial = grid_data.buildings.commercial.append(
            gpd.GeoDataFrame(wkb_to_wkt(archiv_file, '/buildings/commercial'),
                             crs=crs))
        grid_data.buildings.for_living = grid_data.buildings.for_living.append(
            gpd.GeoDataFrame(wkb_to_wkt(archiv_file, '/buildings/for_living'),
                             crs=crs))
        grid_data.buildings.other = grid_data.buildings.other.append(
            gpd.GeoDataFrame(wkb_to_wkt(archiv_file, '/buildings/other'), crs=crs))
        # roads
        grid_data.roads.roads = grid_data.roads.roads.append(
            gpd.GeoDataFrame(wkb_to_wkt(archiv_file, '/roads/roads'), crs=crs))
        grid_data.roads.roads_plot = grid_data.roads.roads_plot.append(
            gpd.GeoDataFrame(wkb_to_wkt(archiv_file, '/roads/roads_plot'), crs=crs))
        road_junctions = wkb_to_wkt(archiv_file, '/roads/road_junctions')
        if not road_junctions.empty:
            road_junctions = road_junctions['geometry']
            road_junctions = gpd.GeoSeries(road_junctions, crs=crs)
            grid_data.roads.road_junctions = grid_data.roads.road_junctions.append(road_junctions)
        # landuse
        grid_data.landuse = grid_data.landuse.append(
            gpd.GeoDataFrame(wkb_to_wkt(archiv_file, '/landuse'), crs=crs))
        # ehv data
        grid_data.ehv_data.ehv_lines = grid_data.ehv_data.ehv_lines.append(
            gpd.GeoDataFrame(wkb_to_wkt(archiv_file, '/ehv_data/ehv_lines'),
                             crs=crs))
        grid_data.ehv_data.ehv_nodes = grid_data.ehv_data.ehv_nodes.append(
            gpd.GeoDataFrame(wkb_to_wkt(archiv_file, '/ehv_data/ehv_nodes'),
                             crs=crs))
        # hv data
        grid_data.hv_data.hv_nodes = grid_data.hv_data.hv_nodes.append(
            gpd.GeoDataFrame(wkb_to_wkt(archiv_file, '/hv_data/hv_nodes'), crs=crs))
        grid_data.hv_data.hv_lines = grid_data.hv_data.hv_lines.append(
            gpd.GeoDataFrame(wkb_to_wkt(archiv_file, '/hv_data/hv_lines'), crs=crs))
        # mv data
        grid_data.mv_data.mv_nodes = grid_data.mv_data.mv_nodes.append(
            gpd.GeoDataFrame(wkb_to_wkt(archiv_file, '/mv_data/mv_nodes'), crs=crs))
        grid_data.mv_data.mv_lines = grid_data.mv_data.mv_lines.append(
            gpd.GeoDataFrame(wkb_to_wkt(archiv_file, '/mv_data/mv_lines'), crs=crs))
        # lv data
        grid_data.lv_data.lv_nodes = grid_data.lv_data.lv_nodes.append(
            gpd.GeoDataFrame(wkb_to_wkt(archiv_file, '/lv_data/lv_nodes'), crs=crs))
        grid_data.lv_data.lv_lines = grid_data.lv_data.lv_lines.append(
            gpd.GeoDataFrame(wkb_to_wkt(archiv_file, '/lv_data/lv_lines'), crs=crs))
        # components_power
        grid_data.components_power.conventional_powerplants = \
            grid_data.components_power.conventional_powerplants.append(
                gpd.GeoDataFrame(wkb_to_wkt(
                    archiv_file, '/components_power/conventional_powerplants'), crs=crs))
        grid_data.components_power.renewable_powerplants = \
            grid_data.components_power.renewable_powerplants.append(gpd.GeoDataFrame(
                wkb_to_wkt(archiv_file, '/components_power/renewable_powerplants'),
                crs=crs))
        grid_data.components_power.loads = grid_data.components_power.loads.append(
            gpd.GeoDataFrame(wkb_to_wkt(archiv_file, '/components_power/loads'),
                             crs=crs))
        grid_data.components_power.transformers.ehv_ehv = \
            grid_data.components_power.transformers.ehv_ehv.append(gpd.GeoDataFrame(
                wkb_to_wkt(archiv_file, '/components_power/transformers/ehv_ehv'),
                crs=crs))
        grid_data.components_power.transformers.ehv_hv = \
            grid_data.components_power.transformers.ehv_hv.append(gpd.GeoDataFrame(
                wkb_to_wkt(archiv_file, '/components_power/transformers/ehv_hv'),
                crs=crs))
        grid_data.components_power.transformers.hv_mv = \
            grid_data.components_power.transformers.hv_mv.append(gpd.GeoDataFrame(
                wkb_to_wkt(archiv_file, '/components_power/transformers/hv_mv'),
                crs=crs))
        grid_data.components_power.transformers.mv_lv = \
            grid_data.components_power.transformers.mv_lv.append(gpd.GeoDataFrame(
                wkb_to_wkt(archiv_file, '/components_power/transformers/mv_lv'),
                crs=crs))
        grid_data.components_power.substations.ehv_hv = \
            grid_data.components_power.substations.ehv_hv.append(gpd.GeoDataFrame(
                wkb_to_wkt(archiv_file, '/components_power/substations/ehv_hv'),
                crs=crs))
        grid_data.components_power.substations.hv_mv = \
            grid_data.components_power.substations.hv_mv.append(gpd.GeoDataFrame(
                wkb_to_wkt(archiv_file, '/components_power/substations/hv_mv'),
                crs=crs))
        grid_data.components_power.substations.mv_lv = \
            grid_data.components_power.substations.mv_lv.append(gpd.GeoDataFrame(
                wkb_to_wkt(archiv_file, '/components_power/substations/mv_lv'),
                crs=crs))
        # hp data
        grid_data.hp_data.hp_junctions = grid_data.hp_data.hp_junctions.append(gpd.GeoDataFrame(
            wkb_to_wkt(archiv_file, '/hp_data/hp_junctions'), crs=crs))
        grid_data.hp_data.hp_pipes = grid_data.hp_data.hp_pipes.append(gpd.GeoDataFrame(
            wkb_to_wkt(archiv_file, '/hp_data/hp_pipes'), crs=crs))
        # mp data
        grid_data.mp_data.mp_junctions = grid_data.mp_data.mp_junctions.append(gpd.GeoDataFrame(
            wkb_to_wkt(archiv_file, '/mp_data/mp_junctions'), crs=crs))
        grid_data.mp_data.mp_pipes = grid_data.mp_data.mp_pipes.append(gpd.GeoDataFrame(
            wkb_to_wkt(archiv_file, '/mp_data/mp_pipes'), crs=crs))
        # lp data
        grid_data.lp_data.lp_junctions = grid_data.lp_data.lp_junctions.append(gpd.GeoDataFrame(
            wkb_to_wkt(archiv_file, '/lp_data/lp_junctions'), crs=crs))
        grid_data.lp_data.lp_pipes = grid_data.lp_data.lp_pipes.append(gpd.GeoDataFrame(
            wkb_to_wkt(archiv_file, '/lp_data/lp_pipes'), crs=crs))
        # components gas
        grid_data.components_gas.compressors = grid_data.components_gas.compressors.append(
            gpd.GeoDataFrame(wkb_to_wkt(archiv_file, '/components_gas/compressors'),
                             crs=crs))
        grid_data.components_gas.sources = grid_data.components_gas.sources.append(gpd.GeoDataFrame(
            wkb_to_wkt(archiv_file, '/components_gas/sources'), crs=crs))
        grid_data.components_gas.storages_gas = grid_data.components_gas.storages_gas.append(
            gpd.GeoDataFrame(wkb_to_wkt(archiv_file, '/components_gas/storages_gas'),
                             crs=crs))
        # dave version
        grid_data.dave_version = archiv_file.get('/dave_version')['dave_version'][0]
        # close file
        archiv_file.close()
        return grid_data
    else:
        print('The requested file is not found in the dave archiv')

def to_archiv(grid_data):
    """
    This functions stores a dave dataset in the dave internal archiv
    """
    # check if file already exists and create file name for archiv
    file_exists, file_name = archiv_inventory(grid_data)
    # create archive file if the dataset does not exists in the archiv
    if not file_exists:
        # --- create file
        archiv_file = pd.HDFStore(get_data_path(f'{file_name}.h5', 'dave_archiv'))
        # area
        area = wkt_to_wkb(grid_data.area)
        archiv_file.put('/area', area)
        # target input
        archiv_file.put('/target_input', grid_data.target_input)
        # buildings
        archiv_file.put('/buildings/commercial',
                        wkt_to_wkb(grid_data.buildings.commercial))
        archiv_file.put('/buildings/for_living',
                        wkt_to_wkb(grid_data.buildings.for_living))
        archiv_file.put('/buildings/other', wkt_to_wkb(grid_data.buildings.other))
        # roads
        archiv_file.put('/roads/roads', wkt_to_wkb(grid_data.roads.roads))
        archiv_file.put('/roads/roads_plot', wkt_to_wkb(grid_data.roads.roads_plot))
        road_junctions = grid_data.roads.road_junctions.copy(deep=True)
        if not road_junctions.empty:
            road_junctions = pd.DataFrame({'geometry': road_junctions})
            road_junctions['geometry'] = road_junctions.geometry.apply(dumps)
        else:
            road_junctions = pd.DataFrame([])
        archiv_file.put('/roads/road_junctions', road_junctions)
        # landuse
        archiv_file.put('/landuse', wkt_to_wkb(grid_data.landuse))
        # ehv data
        archiv_file.put('/ehv_data/ehv_lines',
                        wkt_to_wkb(grid_data.ehv_data.ehv_lines))
        archiv_file.put('/ehv_data/ehv_nodes',
                        wkt_to_wkb(grid_data.ehv_data.ehv_nodes))
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
                        wkt_to_wkb(
                            grid_data.components_power.conventional_powerplants))
        archiv_file.put('/components_power/renewable_powerplants',
                        wkt_to_wkb(grid_data.components_power.renewable_powerplants))
        archiv_file.put('/components_power/loads',
                        wkt_to_wkb(grid_data.components_power.loads))
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
        archiv_file.put('/hp_data/hp_junctions',
                        wkt_to_wkb(grid_data.hp_data.hp_junctions))
        archiv_file.put('/hp_data/hp_pipes', wkt_to_wkb(grid_data.hp_data.hp_pipes))
        # mp data
        archiv_file.put('/mp_data/mp_junctions',
                        wkt_to_wkb(grid_data.mp_data.mp_junctions))
        archiv_file.put('/mp_data/mp_pipes', wkt_to_wkb(grid_data.mp_data.mp_pipes))
        # lp data
        archiv_file.put('/lp_data/lp_junctions',
                        wkt_to_wkb(grid_data.lp_data.lp_junctions))
        archiv_file.put('/lp_data/lp_pipes', wkt_to_wkb(grid_data.lp_data.lp_pipes))
        # components gas
        archiv_file.put('/components_gas/compressors',
                        wkt_to_wkb(grid_data.components_gas.compressors))
        archiv_file.put('/components_gas/sources',
                        wkt_to_wkb(grid_data.components_gas.sources))
        archiv_file.put('/components_gas/storages_gas',
                        wkt_to_wkb(grid_data.components_gas.storages_gas))
        # dave version
        archiv_file.put('/dave_version',
                        pd.DataFrame({'dave_version': grid_data.dave_version}, index=[0]))
        # close file
        archiv_file.close()
    else:
        print('The dataset you tried to save already exist in the DaVe archiv'
              f' with the name "{file_name}"')
    return file_name


def pp_to_json(net, file_path):
    """
    This functions converts a pandapower model into a json file
    """
    # convert geometry
    if not net.bus.empty and all(list(map(lambda x: isinstance(x, Point), net.bus.geometry))):
        net.bus['geometry'] = net.bus.geometry.apply(lambda x: dumps(x, hex=True))
    if not net.line.empty and all(list(map(lambda x: isinstance(x, (LineString, MultiLineString)),
                                           net.line.geometry))):
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
    """
    This functions converts a json file into a pandapower model
    """
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
